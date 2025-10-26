from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os, json, re, unicodedata
import pdfplumber, fitz, pytesseract
from pdf2image import convert_from_path
import arabic_reshaper
from bidi.algorithm import get_display
from pathlib import Path

app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# === Arabic helpers ===
def has_arabic_ratio(s, thresh=0.15):
    ar = re.findall(r'[\u0600-\u06FF]', s)
    return len(ar) / max(1, len(s)) >= thresh

def fix_common_ocr(text):
    text = text.replace("٪","%").replace("﹪","%")
    text = re.sub(r"(\d)\s*%", r"\1%", text)
    return text

def extract_text_from_pdf(pdf_path):
    texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            if len(t) < 40 or not has_arabic_ratio(t):
                # fallback OCR if page weak
                images = convert_from_path(pdf_path)
                text = pytesseract.image_to_string(images[0], lang="ara")
            else:
                text = t
            text = fix_common_ocr(text)
            texts.append(text)
    return "\n\n".join(texts)

def make_readable_arabic(s):
    reshaped = arabic_reshaper.reshape(s)
    return get_display(reshaped)


# === Route to handle uploads ===
@app.route("/upload", methods=["POST"])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "لم يتم رفع أي ملف"}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    text = extract_text_from_pdf(file_path)
    readable = make_readable_arabic(text)

    # Save both versions
    raw_path = file_path.replace(".pdf", "_raw.txt")
    readable_html_path = file_path.replace(".pdf", "_readable.html")

    with open(raw_path, "w", encoding="utf-8") as f:
        f.write(text)

    # create RTL HTML file
    with open(readable_html_path, "w", encoding="utf-8") as f:
        f.write(f"""
        <html lang="ar" dir="rtl">
        <meta charset="UTF-8">
        <body style="font-family: 'Cairo', sans-serif; line-height:1.8; direction:rtl; text-align:right; background:#f8f9fa; padding:2rem;">
        <pre style="white-space: pre-wrap;">{readable}</pre>
        </body>
        </html>
        """)

    return jsonify({
        "message": "✅ تم استخراج النص من الملف بنجاح!",
        "files": {
            "raw": raw_path,
            "html": readable_html_path
        }
    })


if __name__ == "__main__":
    app.run(debug=True)
