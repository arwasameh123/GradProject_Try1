import pytesseract
from pdf2image import convert_from_path

pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"
custom_config = r'--tessdata-dir "/opt/homebrew/share/tessdata" -l ara'

pages = convert_from_path("/Users/amorayasser/Downloads/pdf12017.pdf")

text = ""
for page in pages:
    text += pytesseract.image_to_string(page, config=custom_config)

with open("output.txt", "w", encoding="utf-8") as f:
    f.write(text)

import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import os


pdf_path = "/Users/amorayasser/Downloads/pdf12017.pdf"


output_path = "/Users/amorayasser/Downloads/output.txt"


text = ""

# try to read text
try:
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:  #if there is a text
                text += extracted + "\n"
except Exception as e:
    print("⚠️ Error reading with pdfplumber:", e)

#if we r using only photos (no text) arabic OCR
if not text.strip():
    print("🧠 No text found using pdfplumber, switching to OCR...")
    try:
        pages = convert_from_path(pdf_path)
        for page in pages:
            text += pytesseract.image_to_string(page, lang="ara")
    except Exception as e:
        print("⚠️ OCR failed:", e)

#save changes in  a file 
with open(output_path, "w", encoding="utf-8") as f:
    f.write(text)

print("✅ File saved at:", output_path)
print("📄 Preview:")
print(text[:1000])


articles = text.split("المادة")
