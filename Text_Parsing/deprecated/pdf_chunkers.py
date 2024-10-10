# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 08:17:11 2024

@author: olanr
"""


from typing import List, Dict
import os

import fitz
import PyPDF2

from pdf_inspection_and_extraction import remove_special_characters, get_highest_font_size_for_each_word
from auxillaries import make_directory


def chunk_by_chapters_and_font(input_pdf: str, chapter_names: List[str], font_threshold: float) -> str:
    """
    Splits the PDF into chunks based on chapter names and font size.

    Args:
        input_pdf (str): Path to the input PDF file.
        chapter_names (List[str]): List of chapter names for identifying chunks.
        font_threshold (float): Minimum font size to be considered a chapter.

    Returns:
        str: The directory where the chunked PDF files are saved.
    """
    doc = fitz.open(input_pdf)
    pdf_name = input_pdf.split("Textbooks")[-1].split(".")[0]
    foldername = remove_special_characters(pdf_name)
    dir_name = make_directory(f"pdf_breakdown_{foldername}")

    current_chapter_title = None
    chapter_start = None

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = span["text"].strip().lower()
                    font_size = span["size"]

                    for chapter_name in chapter_names:
                        if font_size >= font_threshold and chapter_name.lower() in text:
                            if chapter_start is not None and page_num > chapter_start:
                                current_chapter_title = remove_special_characters(current_chapter_title)
                                save_chunk(doc, chapter_start, page_num, current_chapter_title, pdf_name, dir_name)

                            chapter_start = page_num
                            current_chapter_title = chapter_name
                            break

    if chapter_start is not None and len(doc) > chapter_start:
        save_chunk(doc, chapter_start, len(doc), current_chapter_title, pdf_name, dir_name)

    doc.close()
    return dir_name




# 2. Chunk by chapter names only (font_threshold is 0)
def chunk_by_chapters_only(input_pdf: str, chapter_names: List[str]) -> str:
    """
    Splits the PDF into chunks based on chapter names, without considering font size.

    Args:
        input_pdf (str): Path to the input PDF file.
        chapter_names (List[str]): List of chapter names for identifying chunks.

    Returns:
        str: The directory where the chunked PDF files are saved.
    """
    doc = fitz.open(input_pdf)
    pdf_name = input_pdf.split("Textbooks")[-1].split(".")[0]
    foldername = remove_special_characters(pdf_name)
    dir_name = make_directory(f"pdf_breakdown_{foldername}")

    chapter_start = None
    current_chapter_title = None

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text").lower()

        for chapter_name in chapter_names:
            if chapter_name.lower() in text:
                if chapter_start is not None:
                    current_chapter_title = remove_special_characters(current_chapter_title)
                    chapter_name = chapter_name.replace(" ", "_")
                    current_chapter_title = current_chapter_title.replace(" ", "_")
    
                    save_chunk(doc, chapter_start, page_num, current_chapter_title, pdf_name, dir_name)
                chapter_start = page_num
                current_chapter_title = chapter_name
                break

    if chapter_start is not None:
        save_chunk(doc, chapter_start, len(doc), current_chapter_title, pdf_name, dir_name)
    
    doc.close()
    return dir_name

# 3. Chunk by font_threshold only (chapter names list is empty)
def chunk_by_font_threshold(input_pdf: str, font_threshold: float) -> str:
    """
    Splits the PDF into chunks based on font size threshold, ignoring chapter names.

    Args:
        input_pdf (str): Path to the input PDF file.
        font_threshold (float): Minimum font size to create a new chunk.

    Returns:
        str: The directory where the chunked PDF files are saved.
    """
    doc = fitz.open(input_pdf)
    pdf_name = input_pdf.split("Textbooks")[-1].split(".")[0]
    foldername = remove_special_characters(pdf_name)
    dir_name = make_directory(f"pdf_breakdown_{foldername}")

    chapter_start = None
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    font_size = span["size"]
                    if font_size >= font_threshold:
                        if chapter_start is not None:
                            save_chunk(doc, chapter_start, page_num, f"Chunk_{page_num}_Pg_{chapter_start+1}", pdf_name, dir_name)
                        chapter_start = page_num
                        break

    if chapter_start is not None:
        save_chunk(doc, chapter_start, len(doc), f"Chunk_{page_num}_Pg_{chapter_start+1}", pdf_name, dir_name)
    
    doc.close()
    return dir_name

    
# 4. Chunk by word count (default to 1000 words)
def chunk_by_word_count(input_pdf: str, word_limit: int = 1000) -> str:
    """
    Splits the PDF into chunks based on word count.

    Args:
        input_pdf (str): Path to the input PDF file.
        word_limit (int, optional): Number of words per chunk. Defaults to 1000.

    Returns:
        str: The directory where the chunked PDF files are saved.
    """
    doc = fitz.open(input_pdf)
    pdf_name = input_pdf.split("Textbooks")[-1].split(".")[0]
    foldername = remove_special_characters(pdf_name)
    dir_name = make_directory(f"pdf_breakdown_{foldername}")

    word_count = 0
    chapter_start = 0

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        words = text.split()

        word_count += len(words)

        if word_count >= word_limit:
            save_chunk(doc, chapter_start, page_num + 1, f"Chunk_{page_num}_Words_{word_count}", pdf_name, dir_name)
            chapter_start = page_num + 1
            word_count = 0

    if chapter_start < len(doc):
        save_chunk(doc, chapter_start, len(doc), f"Chunk_{page_num}_Words_{word_count}", pdf_name, dir_name)
    
    doc.close()
    return dir_name


def save_chunk(doc, chapter_start, page_num, title, pdf_name, save_dir):
    """
    Save the extracted chunk of the PDF based on chapters or fonts.
    Ensures that the chunk has pages before saving it.
    """
    chunk_pdf = fitz.open()  # Create a new empty PDF

    # Add pages from the chapter_start to the current page (exclusive)
    for i in range(chapter_start, page_num):
        page = doc.load_page(i)
        chunk_pdf.insert_pdf(doc, from_page=i, to_page=i)

    # Ensure the chunk has at least one page before saving
    if len(chunk_pdf) > 0:
        
        # Save the chunk with the chapter title as the file name
        #safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
        safe_title = title.replace(" ", "_")
        chunk_pdf.save(f'{save_dir}/{safe_title}.pdf')
        print(f"{safe_title}.pdf saved in folder {save_dir}")
        chunk_pdf.close()
    else:
        print(f"Skipping save: no pages in the chunk for chapter '{title}'.")


# The main function to determine which chunking strategy to use
def chunk_pdf(input_pdf, chapter_names=[], font_threshold=0, word_limit=1000):
    if chapter_names and font_threshold > 0:
        print("Chunking by chapter names and font threshold...")
        #dir_name = chunk_by_chapters_and_font(input_pdf, chapter_names, font_threshold)
        dir_name = chunk_by_word_count(input_pdf, word_limit)
    elif chapter_names and font_threshold == 0:
        print("Chunking by chapter names only...")
        dir_name = chunk_by_chapters_only(input_pdf, chapter_names)
    elif not chapter_names and font_threshold > 0:
        print("Chunking by font threshold only...")
        dir_name = chunk_by_font_threshold(input_pdf, font_threshold)
    else:
        print(f"Chunking by word count (limit: {word_limit} words)...")
        dir_name = chunk_by_word_count(input_pdf, word_limit)
    
    return dir_name



def extract_text_in_batches(pdf_path: str, batch_size: int = 1500) -> Dict[str, List[str]]:
    """
    Extracts text from a PDF file and splits it into batches of a specified size.

    Args:
        pdf_path (str): The file path to the PDF.
        batch_size (int, optional): The number of words per batch. Defaults to 1500.

    Returns:
        Dict[str, List[str]]: A dictionary where the key is the textbook name (derived from the file name),
                              and the value is a list of text batches, each containing a maximum of `batch_size` words.
    """
    # Get the textbook name from the file path (without the extension)
    textbook_name = os.path.basename(pdf_path).replace('.pdf', '')
    
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        full_text = ""
        
        # Extract text from all the pages
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            full_text += page.extract_text()
    
    if not full_text:
        return {textbook_name: ['']}
    
    # Split the text into words
    words = full_text.split()
    
    # Create batches of `batch_size` words
    batches = [" ".join(words[i:i + batch_size]) for i in range(0, len(words), batch_size)]
    
    # Return the result as a dictionary with the textbook name as the key
    return {textbook_name: batches}



def extract_chapter_text_in_batches(dir_name: str) -> Dict[str, List[str]]:
    """
    Extracts text in batches from all chapters in a given directory, where each file represents a chapter.

    Args:
        dir_name (str): The directory containing chapter files (PDFs).

    Returns:
        Dict[str, List[str]]: A dictionary mapping each chapter name to its corresponding text batches.
    """
    # List all files (chapters) in the directory
    list_of_chapters = os.listdir(dir_name)
    
    # Dictionary to store chapter names and their respective text batches
    chapter_to_text_mappings = {}
    
    # Process each chapter file
    for chapter_name in list_of_chapters:
        full_path = os.path.join(dir_name, chapter_name)
        chapter_to_text_mapping = extract_text_in_batches(full_path)
        chapter_to_text_mappings.update(chapter_to_text_mapping)
    
    return chapter_to_text_mappings
