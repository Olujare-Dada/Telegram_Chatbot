# -*- coding: utf-8 -*-
"""
Created on Fri Sep  6 06:42:45 2024

@author: olanr
"""

import fitz  # PyMuPDF

def extract_text_by_fontsize(pdf_path, min_font_size=12):
    doc = fitz.open(pdf_path)
    text_blocks = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # Load each page
        blocks = page.get_text("dict")["blocks"]  # Get text blocks

        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span["size"] >= min_font_size:
                        text_blocks.append({
                            "page": page_num + 1,
                            "font_size": span["size"],
                            "text": span["text"]
                        })
    return text_blocks


def split_pdf_by_chapters(input_pdf, font_threshold=15):
    doc = fitz.open(input_pdf)
    chapter_pages = []
    chapter_start = 0

    # Identify chapter pages based on font size
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    # Check if this span contains large font (chapter title)
                    if span["size"] >= font_threshold:
                        if chapter_start != page_num:
                            chapter_pages.append(chapter_start)
                        chapter_start = page_num
                        break

    # Add the last chapter if any
    chapter_pages.append(chapter_start)

    # Split and save each chapter into a separate PDF
    for i in range(len(chapter_pages) - 1):
        chapter_pdf = fitz.open()  # Create a new PDF for each chapter
        for page_num in range(chapter_pages[i], chapter_pages[i+1]):
            chapter_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)
        chapter_pdf.save(f'chapter_{i+1}.pdf')
        print(f'chapter_{i+1}.pdf saved.')

    doc.close()


# Usage Example:
input_pdf = 'babok_guide_v3.pdf'
font_threshold = 48  # Customize based on the font size of chapter titles
tb = extract_text_by_fontsize(input_pdf, font_threshold)
split_pdf_by_chapters(input_pdf, font_threshold)


import easyocr
from PIL import Image
import fitz  # PyMuPDF

# Initialize EasyOCR reader (supports multiple languages, e.g., 'en' for English)
reader = easyocr.Reader(['en'])

def extract_images_and_text_with_easyocr(pdf_path):
    doc = fitz.open(pdf_path)
    image_data = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        images = page.get_images(full=True)
        print(len(images))
    #     for img_index, img in enumerate(images):
    #         xref = img[0]
    #         base_image = doc.extract_image(xref)
    #         image_bytes = base_image["image"]
    #         image_ext = base_image["ext"]
    #         image_filename = f"image_page_{page_num+1}_{img_index+1}.{image_ext}"

    #         # Save the image
    #         with open(image_filename, "wb") as img_file:
    #             img_file.write(image_bytes)

    #         # Open the image and perform OCR
    #         image_pil = Image.open(image_filename)
    #         ocr_result = reader.readtext(image_filename)

    #         # Extract and concatenate text from OCR result
    #         ocr_text = " ".join([text[1] for text in ocr_result])
            
    #         # Store the result
    #         image_data.append({
    #             "page": page_num + 1,
    #             "image_filename": image_filename,
    #             "ocr_text": ocr_text
    #         })

    #         print(f"Image extracted on page {page_num+1} and saved as {image_filename}")
    #         if ocr_text.strip():
    #             print(f"Text extracted from the image on page {page_num+1}: \n{ocr_text}\n")

    # return image_data


doc7 = fitz.open("Human Trafficking Around the World_ Hidden in Plain Sight ( PDFDrive ).pdf")
e = doc4.load_page(5).get_text("dict")["blocks"][1].get("lines")
f = doc7.get_toc()


# Example usage:
pdf_path = "chapter_3.pdf"
image_data = extract_images_and_text_with_easyocr(pdf_path)
