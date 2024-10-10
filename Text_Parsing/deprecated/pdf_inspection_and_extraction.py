# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 08:09:32 2024

@author: olanr
"""


import re
from typing import Dict, List, Optional
from openai_kit import PromptTemplate, get_gpt_response
from collections import Counter

import PyPDF2
import fitz




def remove_special_characters(text: str) -> str:
    # Define a regex pattern that matches all non-alphanumeric characters and spaces
    pattern = r'[^\w ]'
    # Replace all special characters with a space
    cleaned_text = re.sub(pattern, ' ', text)
    # Replace multiple spaces with a single space and strip leading/trailing spaces
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text



def get_highest_font_size_for_each_word(pdf_path: str, words: List[str]) -> Dict[str, float]:
    """
    Extracts the highest font size for each word from a given list within a PDF document.

    Args:
        pdf_path (str): The file path of the PDF document.
        words (List[str]): A list of words to search for in the PDF (case-insensitive).

    Returns:
        Dict[str, float]: A dictionary where the keys are the words (in lowercase) and the values are their highest font sizes found in the PDF.
    
    Example:
        result = get_highest_font_size_for_each_word("file.pdf", ["Chapter", "Introduction"])
        # result = {'chapter': 16.0, 'introduction': 14.5}
    """
    
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    
    # Initialize a dictionary to store the highest font size for each word
    word_font_sizes = {word.lower(): 0 for word in words}

    # Convert the words to lowercase for case-insensitive comparison
    words_set = set([word.lower() for word in words])

    # Loop through all the pages in the PDF
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        # Loop through all the blocks on each page
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"]
                        font_size = span["size"]

                        # Split the text into individual words and check if any match the list
                        for word in text.split():
                            # Check if the word is in the provided list (case-insensitive)
                            word_lower = word.lower()
                            if word_lower in words_set:
                                # If found, update the font size if it's higher than the current one
                                if font_size > word_font_sizes[word_lower]:
                                    word_font_sizes[word_lower] = font_size

    pdf_document.close()
    return word_font_sizes



def get_highest_font_size_for_each_chapter(pdf_path: str, chapter_titles: List[str]) -> Dict[str, float]:
    """
    Extracts the highest font size for each chapter title within a PDF document.

    Args:
        pdf_path (str): The file path of the PDF document.
        chapter_titles (List[str]): A list of chapter titles to search for in the PDF (case-insensitive).

    Returns:
        Dict[str, float]: A dictionary where the keys are the chapter titles (in lowercase) and the values are their highest font sizes found in the PDF.
    
    Example:
        result = get_highest_font_size_for_each_chapter("file.pdf", ["Chapter 1", "Chapter 2"])
        # result = {'chapter 1': 20.0, 'chapter 2': 18.0}
    """
    
    if not chapter_titles:
        return {}
    
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    
    # Initialize a dictionary to store the highest font size for each chapter title
    chapter_font_sizes = {title.lower(): 0 for title in chapter_titles}

    # Convert the chapter titles to lowercase for case-insensitive comparison
    chapter_titles_set = set([title.lower() for title in chapter_titles])

    # Loop through all the pages in the PDF
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        # Loop through all the blocks on each page
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip().lower()  # Convert to lowercase for case-insensitive matching
                        font_size = span["size"]

                        # Check if the entire text matches any chapter title (multi-word chapters handled here)
                        if text in chapter_titles_set:
                            # If found, update the font size if it's higher than the current one
                            if font_size > chapter_font_sizes[text]:
                                chapter_font_sizes[text] = font_size

    pdf_document.close()
    return chapter_font_sizes



def get_first_1500_words(*, pdf_path: str) -> str:
    def get_table_of_contents_start_page(pdf_document: fitz.Document) -> Optional[int]:
        """
        Extract the table of contents and return the starting page number.
        """
        toc = pdf_document.get_toc()
        if toc:
            # Assuming the first entry in TOC is the main one
            first_entry = toc[0]
            # TOC entries are typically formatted as [level, title, page]
            return first_entry[2] - 1  # Convert to 0-based page number
        return None

    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    
    word_list = []  # List to hold the words
    word_count = 0  # Keep track of how many words we've extracted
    
    # Get the starting page of the TOC, if available
    toc_start_page = get_table_of_contents_start_page(pdf_document)
    
    # Default to the beginning of the PDF if TOC not found
    start_page = toc_start_page if toc_start_page is not None else 0
    print(f"{start_page = }")
    
    # Loop through the pages in the PDF, starting from the determined page
    for page_num in range(start_page, len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text: str = page.get_text("text")  # Extract text from the page
        
        # Split the text into individual words
        words: List[str] = text.split()
        
        # Add words to the list until we reach 1500 words
        for word in words:
            word_list.append(word)
            word_count += 1
            if word_count >= 1500:
                break
        
        # If we have 1500 words, stop extracting
        if word_count >= 1500:
            break
    
    pdf_document.close()
    
    # Return the first 1000 words as a single string
    return ' '.join(word_list)


def extract_prospective_textbook_chapters(*, textbook_filepath: str) -> List[str]:
    """
    Extracts prospective chapter titles from the table of contents (ToC) of a textbook PDF.
    
    Args:
        textbook_filepath (str): Path to the PDF file of the textbook.
    
    Returns:
        List[str]: A list of prospective chapter titles extracted from the ToC. If no chapters are found,
                   an empty list is returned.
    """
    document = fitz.open(textbook_filepath)
    prospective_chapters_list_of_list: List = document.get_toc()
    
    prospective_chapters = []
    for prospective_chapter_list in prospective_chapters_list_of_list:
        
        if len(prospective_chapter_list) >= 2:
            prospective_chapters.append(prospective_chapter_list[1])
    
    if not prospective_chapters:
        print("Fitz could not extract prospective chapters. Extracting the first 1,000 words instead.")
        print("Chunking will be done on a strictly page basis.")
        return []
    
    return prospective_chapters




def derive_chapter_names(*, textbook_filepath: str, prospective_chapters: List[str]) -> List[str]:
    """
    Uses a language model to derive clean chapter names from the list of prospective chapters.

    Args:
        textbook_filepath (str): Path to the PDF file of the textbook.
        prospective_chapters (List[str]): A list of prospective chapter titles extracted from the PDF.

    Returns:
        List[str]: A list of refined chapter names derived from the language model.
    """
    if not prospective_chapters:
        return []

    textbook_name: str = textbook_filepath.split(".")[0]

    # Retrieve the prompts from pre-defined templates
    get_chapters_prompt: str = PromptTemplate.get_chapters_prompt.value
    chapters_instructions: str = PromptTemplate.get_chapter_instructions.value

    # Interact with the language model to derive chapter names
    chapter_names_raw: str = get_gpt_response(
        prompt=get_chapters_prompt.format(
            chapters_instructions=chapters_instructions,
            book_title=textbook_name,
            headers=prospective_chapters
        )
    )

    # Clean up the chapter names and return as a list
    chapter_names = [chapter.strip() for chapter in chapter_names_raw.split("\n")]

    return chapter_names



def get_confirmed_chapter_font_size(chapter_font_sizes: Dict[str, float]) -> float:
    """
    Determines the most common chapter font size in the textbook.

    Args:
        chapter_font_sizes (Dict[str, float]): A dictionary mapping chapter titles to their respective font sizes.

    Returns:
        float: The most common chapter font size. Returns -1.0 if no valid font sizes are found.
    """
    
    if not chapter_font_sizes:
        return -1.0
    
    possible_font_sizes = [font_size for font_size in chapter_font_sizes.values() if font_size > 0]
    
    if not possible_font_sizes:
        return -1.0
    
    font_size_counts = Counter(possible_font_sizes)
    most_common_font_size, count = font_size_counts.most_common(1)[0]
    
    # Check if the most common font size is indeed a majority
    if count > len(possible_font_sizes) / 2:
        return most_common_font_size
    
    return -1.0  # Return -1.0 if no majority found   
