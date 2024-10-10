# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 14:47:03 2024

@author: olanr
"""

import os
from typing import Dict, Union
import uuid

from pdf_inspection_and_extraction import (extract_prospective_textbook_chapters, 
                                           derive_chapter_names, 
                                           get_highest_font_size_for_each_chapter, 
                                           get_confirmed_chapter_font_size
                                           )

from pdf_chunkers import chunk_pdf, extract_chapter_text_in_batches
from auxillaries import make_directory, convert_final_map_to_json


from dotenv import load_dotenv


load_dotenv()








def generate_metadata(pdf_name: str, 
                      #authors: Union[List, None] = None, 
                      #publication_year: Union[int, None] = None,
                      #category: Union[str, None] = None,
                      language: Union[str, None] = "English",
                      #edition: Union[str, None] = None,
                      #keywords: List = ["No keywords"],
                      #isbn: Union[str, None]= None,
                      #summary: Union[str, None] = None,
                      #user_ratings: Union[float, None] = None,
                      #availability_status: Union[str, None] = None
                     
                      )-> Dict:
    
    unique_idx = str(uuid.uuid4())
    
    return {
     "document_id": pdf_name + "_" + unique_idx,
     "title": pdf_name,
     #"authors": [*authors],
     #"publication_year": publication_year,
     #"category": category,
     "language": language,
     #"edition": edition,
     #"keywords": [*keywords],
     #"isbn": isbn,
     #"summary": "A comprehensive introduction to the modern study of computer algorithms.",
     #"user_ratings": user_ratings,
     #"availability_status": availability_status
     }



                                           


if __name__ == "__main__":
    parent_folder = ".."
    pdf_folder = "Textbooks"
    pdf_name = "babok_guide_v3.pdf"#"Human Trafficking Around the World_ Hidden in Plain Sight ( PDFDrive ).pdf"#"An Introduction to Statistics with Python  With Applications in the Life Sciences ( PDFDrive ).pdf"#"applied time series econometrics ( PDFDrive ).pdf""Human Trafficking Around the World_ Hidden in Plain Sight ( PDFDrive ).pdf"
    
    pdf_path = os.path.join(parent_folder, pdf_folder, pdf_name)#f"{pdf_folder}/{pdf_name}"
    prospective_chapters = extract_prospective_textbook_chapters(textbook_filepath = pdf_path)
    chapters = derive_chapter_names(textbook_filepath = pdf_path, prospective_chapters = prospective_chapters)
    #word_font_sizes = get_highest_font_size_for_each_word(pdf_path, chapters)
    
    chapter_font_sizes = get_highest_font_size_for_each_chapter(pdf_path, chapters)
    
    confirmed_chapter_font_size = get_confirmed_chapter_font_size(chapter_font_sizes)
    
    dir_name = chunk_pdf(pdf_path, chapters, confirmed_chapter_font_size)
    
    final_map = extract_chapter_text_in_batches(dir_name)
    
    json_folder = "textbook_in_json"
    
    make_directory(json_folder)
    
    convert_final_map_to_json(final_map, pdf_name, json_folder)
    
    #read_map = read_json(json_folder)
    


"""
Code Logic So far:
    1. Open the textbook with fitz and get the table of content using the .toc() method.
    2. Then, we extract all the individual chapter names from the result of the previous step. These are just
    possible chapter names.
    3. If the fitz module fails to get any chapter names, we extract the first 1000 words from the text.
    4. The list of possible chapter names or the 1000-word string (either case) is sent to the LLM to extract the
    chapter names and return them as a string.
    5. These chapter names are then searched through the text using the fitz module. This time, we are searching
    for where these chapter names exist in the text in their largest fonts. THe idea here is that most, if not all
    chapter names will appear in the same font, which will also be the largest font occurrence of the word
    combinations that make up the chapter names.
    6. We take note of the font size from the previous step and then we divide the pdf file by the chapter name with 
    that exact font size. (Crazy step)
    7. After this, we can then chunk the chapter texts into arbitrary text sizes
    

Later logic:
    When you have retrieved the text from pinecone, we take the scores and use only text within the 95% percentile
    leaving a small room for failure
"""
# y = break_pdf_into_chapters(pdf_path, x)

# word_font_sizes = get_highest_font_size_for_each_word(pdf_path, x)



# def break_pdf_into_chapters(pdf_file, chapter_titles):
#     """
#     Splits the content of a PDF into chapters based on an array of chapter titles.
    
#     Args:
#     - pdf_file (str): Path to the input PDF file.
#     - chapter_titles (list): List of strings representing the chapter titles.
    
#     Returns:
#     - chapters (dict): Dictionary containing chapter titles as keys and their respective content as values.
#     """
    
#     # Open the PDF file
#     with open(pdf_file, 'rb') as file:
#         reader = PyPDF2.PdfReader(file)
#         num_pages = len(reader.pages)

#         chapters = {}
#         current_chapter = None
#         title_index = 0

#         # Initialize the first chapter as the starting point
#         if chapter_titles:
#             current_chapter = chapter_titles[title_index]
#             chapters[current_chapter] = ""

#         # Loop through each page to extract text
#         for idx, page_num in enumerate(range(num_pages-1, 0, -1)):
#             page = reader.pages[page_num]
#             text = page.extract_text()
#             print(text.find("Index"))
            
            # # Split the text by lines
            # for line in text.split('\n'):
            #     line = remove_special_characters(line)
                
            #     if title_index < len(chapter_titles) and line.strip() == chapter_titles[title_index]:
            #         # Move to the next chapter when a title is found
            #         current_chapter = chapter_titles[title_index]
            #         chapters[current_chapter] = ""
            #         title_index += 1
            #     elif current_chapter:
            #         # Add content to the current chapter
            #         chapters[current_chapter] += line + '\n'
            
            
#    return chapters


# doc7 = fitz.open("Human Trafficking Around the World_ Hidden in Plain Sight ( PDFDrive ).pdf")
# e = doc7.load_page(5).get_text("dict")["blocks"][1].get("lines")
# f = doc7.get_toc()

# Example usage
# pdf_file = 'your_pdf_file.pdf'
# chapter_titles = [
#     "Chapter 1: Introduction", 
#     "Chapter 2: Methodology", 
#     "Chapter 3: Results", 
#     "Chapter 4: Discussion"
# ]

# chapters = break_pdf_into_chapters(pdf_file, chapter_titles)

# # Print the first few characters of each chapter
# for chapter_title, content in chapters.items():
#     print(f"Chapter: {chapter_title}")
#     print(content[:200])  # print first 200 characters of each chapter content
#     print("------")




# def split_pdf_by_chapters(input_pdf, font_threshold=15):
#     doc = fitz.open(input_pdf)
#     chapter_pages = []
#     chapter_start = 0

#     # Identify chapter pages based on font size
#     for page_num in range(len(doc)):
#         page = doc.load_page(page_num)
#         blocks = page.get_text("dict")["blocks"]
#         for block in blocks:
#             for line in block.get("lines", []):
#                 for span in line.get("spans", []):
#                     # Check if this span contains large font (chapter title)
#                     if span["size"] >= font_threshold:
#                         if chapter_start != page_num:
#                             chapter_pages.append(chapter_start)
#                         chapter_start = page_num
#                         break

#     # Add the last chapter if any
#     chapter_pages.append(chapter_start)

#     # Split and save each chapter into a separate PDF
#     for i in range(len(chapter_pages) - 1):
#         chapter_pdf = fitz.open()  # Create a new PDF for each chapter
#         for page_num in range(chapter_pages[i], chapter_pages[i+1]):
#             chapter_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)
#         chapter_pdf.save(f'chapter_{i+1}.pdf')
#         print(f'chapter_{i+1}.pdf saved.')

#     doc.close()


# def break_pdf_into_chapters(pdf_path, chapter_titles):
    
#     doc = fitz.open(pdf_path)
    
#     for page_num in range(len(doc)):
#         page_content_object = doc.load_page(page_num)
#         pag_text = page_content_object.get_text()
#         blocks = page_content_object.get_text("dict")["blocks"]



# Helper function to save each chunk
# def save_chunk(doc, start_page, end_page, title, pdf_name):
#     chunk_pdf = fitz.open()
#     for page_num in range(start_page, end_page):
#         chunk_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)
    
#     pdf_name = remove_special_characters(pdf_name)
#     title = remove_special_characters(title)
#     chunk_pdf.save(f'pdf_breakdown_{pdf_name}/{title}.pdf')
#     chunk_pdf.close()
#     print(f'{title}.pdf saved.')


# def split_pdf_by_chapters(input_pdf, chapter_names, font_threshold):
#     doc = fitz.open(input_pdf)
#     pdf_name = input_pdf.split(".")[0] if len(input_pdf) < 40 else input_pdf.split(".")[0][:40]
#     make_directory(f"pdf_breakdown_{pdf_name}")
#     chapter_pages = []
#     chapter_titles = []
#     chapter_start = None
#     current_chapter_title = None
#     chapter_names_lower = [name.lower() for name in chapter_names]  # Make chapter names case-insensitive

#     # Identify chapter pages based on font size and chapter names
#     for page_num in range(len(doc)):
#         page = doc.load_page(page_num)
#         blocks = page.get_text("dict")["blocks"]
#         for block in blocks:
#             for line in block.get("lines", []):
#                 for span in line.get("spans", []):
#                     text = span["text"].strip().lower()  # Convert the text to lowercase for case-insensitive matching
#                     font_size = span["size"]

#                     # Check if the span contains large font (chapter title) and matches a chapter name
#                     for chapter_name in chapter_names_lower:
#                         if font_size >= font_threshold and chapter_name in text:
#                             if chapter_start is not None:
#                                 # Save the current chapter
#                                 chapter_pages.append(chapter_start)
#                                 chapter_titles.append(current_chapter_title)
#                             chapter_start = page_num  # Start of a new chapter
#                             current_chapter_title = chapter_name  # Save the current chapter name
#                             break

#     # Add the last chapter's starting page if any
#     if chapter_start is not None:
#         chapter_pages.append(chapter_start)
#         chapter_titles.append(current_chapter_title)
    
#     # Now we need to process the chapter pages and titles
#     for i in range(len(chapter_pages) - 1):
#         chapter_pdf = fitz.open()  # Create a new PDF for each chapter
#         chapter_title = chapter_titles[i].replace(" ", "_")  # Clean the chapter name for use in a file name
#         for page_num in range(chapter_pages[i], chapter_pages[i+1]):
#             chapter_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)
        
#         chapter_pdf.save(f'pdf_breakdown_{pdf_name}/{chapter_title}.pdf')  # Save the PDF with the chapter name
#         print(f'{chapter_title}.pdf saved in Folder pdf_breakdown_{pdf_name}.')
        
#     # Process the last chapter (since the loop doesn't capture the last one)
#     if len(chapter_pages) > 1:
#         last_chapter_pdf = fitz.open()
#         last_chapter_title = chapter_titles[-1].replace(" ", "_")
#         for page_num in range(chapter_pages[-1], len(doc)):
#             last_chapter_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)
        
#         chapter_pdf.save(f'pdf_breakdown_{pdf_name}/{chapter_title}.pdf')  # Save the PDF with the chapter name
#         print(f'{chapter_title}.pdf saved in Folder pdf_breakdown_{pdf_name}.')

#         last_chapter_pdf.save(f'pdf_breakdown_{pdf_name}/{last_chapter_title}.pdf')
#         print(f'{last_chapter_title}.pdf saved in Folder pdf_breakdown_{pdf_name}.')

#     doc.close()

# def split_pdf_by_chapters(input_pdf, chapter_names, font_threshold):
#     doc = fitz.open(input_pdf)
#     pdf_name = input_pdf.split(".")[0] if len(input_pdf) < 40 else input_pdf.split(".")[0][:40]
#     make_directory(f"pdf_breakdown_{pdf_name}")
#     chapter_pages = []
#     chapter_titles = []
#     chapter_start = None
#     current_chapter_title = None
#     chapter_names_lower = [name.lower() for name in chapter_names]  # Make chapter names case-insensitive

#     # Identify chapter pages based on font size and chapter names
#     for page_num in range(len(doc)):
#         page = doc.load_page(page_num)
#         blocks = page.get_text("dict")["blocks"]
#         for block in blocks:
#             for line in block.get("lines", []):
#                 for span in line.get("spans", []):
#                     text = span["text"].strip().lower()  # Convert the text to lowercase for case-insensitive matching
#                     font_size = span["size"]

#                     # Check if the span contains large font (chapter title) and matches a chapter name
#                     for chapter_name in chapter_names_lower:
#                         if (font_threshold == 0 or font_size >= font_threshold) and chapter_name in text:
#                             if chapter_start is not None:
#                                 # Save the current chapter
#                                 chapter_pages.append(chapter_start)
#                                 chapter_titles.append(current_chapter_title)
#                             chapter_start = page_num  # Start of a new chapter
#                             current_chapter_title = chapter_name  # Save the current chapter name
#                             break

#     # Add the last chapter's starting page if any
#     if chapter_start is not None:
#         chapter_pages.append(chapter_start)
#         chapter_titles.append(current_chapter_title)
    
#     # Now we need to process the chapter pages and titles
#     for i in range(len(chapter_pages) - 1):
#         chapter_pdf = fitz.open()  # Create a new PDF for each chapter
#         chapter_title = chapter_titles[i].replace(" ", "_")  # Clean the chapter name for use in a file name
#         for page_num in range(chapter_pages[i], chapter_pages[i+1]):
#             chapter_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)

#         if chapter_pdf.page_count > 0:  # Check if the PDF has pages before saving
#             chapter_pdf.save(f'pdf_breakdown_{pdf_name}/{chapter_title}.pdf')  # Save the PDF with the chapter name
#             print(f'{chapter_title}.pdf saved in Folder pdf_breakdown_{pdf_name}.')
#         else:
#             print(f'Skipped saving {chapter_title}.pdf as it has no pages.')

#     # Process the last chapter (since the loop doesn't capture the last one)
#     if len(chapter_pages) > 1:
#         last_chapter_pdf = fitz.open()
#         last_chapter_title = chapter_titles[-1].replace(" ", "_")
#         for page_num in range(chapter_pages[-1], len(doc)):
#             last_chapter_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)
        
#         if last_chapter_pdf.page_count > 0:  # Check if the last PDF has pages before saving
#             last_chapter_pdf.save(f'pdf_breakdown_{pdf_name}/{last_chapter_title}.pdf')
#             print(f'{last_chapter_title}.pdf saved in Folder pdf_breakdown_{pdf_name}.')
#         else:
#             print(f'Skipped saving {last_chapter_title}.pdf as it has no pages.')

#     doc.close()




# def get_chapter_pages_by_names(doc, chapter_names_lower):
#     """
#     Get the start pages of chapters by matching chapter names in the text.
#     """
#     chapter_pages = []
#     chapter_titles = []
#     chapter_start = None
#     current_chapter_title = None

#     for page_num in range(len(doc)):
#         page = doc.load_page(page_num)
#         blocks = page.get_text("dict")["blocks"]
#         for block in blocks:
#             for line in block.get("lines", []):
#                 for span in line.get("spans", []):
#                     text = span["text"].strip().lower()  # Convert to lowercase for case-insensitive matching
#                     for chapter_name in chapter_names_lower:
#                         if chapter_name in text:
#                             if chapter_start is not None:
#                                 chapter_pages.append(chapter_start)
#                                 chapter_titles.append(current_chapter_title)
#                             chapter_start = page_num
#                             current_chapter_title = chapter_name
#                             break

#     if chapter_start is not None:
#         chapter_pages.append(chapter_start)
#         chapter_titles.append(current_chapter_title)

#     return chapter_pages, chapter_titles

# def get_chapter_pages_by_font(doc, font_threshold):
#     """
#     Get the start pages of chapters by detecting large fonts.
#     """
#     chapter_pages = []
#     chapter_titles = []
#     chapter_start = None

#     for page_num in range(len(doc)):
#         page = doc.load_page(page_num)
#         blocks = page.get_text("dict")["blocks"]
#         for block in blocks:
#             for line in block.get("lines", []):
#                 for span in line.get("spans", []):
#                     font_size = span["size"]
#                     if font_size >= font_threshold:
#                         if chapter_start is not None:
#                             chapter_pages.append(chapter_start)
#                             chapter_titles.append(f"chapter_{len(chapter_titles) + 1}")
#                         chapter_start = page_num

#     if chapter_start is not None:
#         chapter_pages.append(chapter_start)
#         chapter_titles.append(f"chapter_{len(chapter_titles) + 1}")

#     return chapter_pages, chapter_titles

# # def get_pages_by_word_count(doc, word_limit=1000):
# #     """
# #     Chunk the PDF by word count (every 1000 words).
# #     """
# #     chapter_pages = []
# #     chapter_titles = []
# #     chapter_start = None
# #     word_count = 0

# #     for page_num in range(len(doc)):
# #         page = doc.load_page(page_num)
# #         text = page.get_text("text")
# #         word_count += len(text.split())

# #         if chapter_start is None:
# #             chapter_start = page_num

# #         if word_count >= word_limit:  # Chunk by word limit
# #             chapter_pages.append(chapter_start)
# #             chapter_titles.append(f"chunk_{len(chapter_titles) + 1}")
# #             chapter_start = page_num
# #             word_count = 0  # Reset word count for next chunk

# #     if chapter_start is not None:
# #         chapter_pages.append(chapter_start)
# #         chapter_titles.append(f"chunk_{len(chapter_titles) + 1}")

# #     return chapter_pages, chapter_titles

# def get_pages_by_word_count(doc, word_limit=1000):
#     """
#     Chunk the PDF by word count (every 1000 words) and include the starting page number in the chunk file name.
#     """
#     chapter_pages = []
#     chapter_titles = []
#     chapter_start = None
#     word_count = 0

#     for page_num in range(len(doc)):
#         page = doc.load_page(page_num)
#         text = page.get_text("text")
#         word_count += len(text.split())

#         if chapter_start is None:
#             chapter_start = page_num

#         if word_count >= word_limit:  # Chunk by word limit
#             chapter_pages.append(chapter_start)
#             chapter_titles.append(f"chunk_{len(chapter_titles) + 1}_pg_{chapter_start + 1}")
#             chapter_start = page_num
#             word_count = 0  # Reset word count for next chunk

#     # Add the last chunk if any remaining words
#     if chapter_start is not None:
#         chapter_pages.append(chapter_start)
#         chapter_titles.append(f"chunk_{len(chapter_titles) + 1}_pg_{chapter_start + 1}")

#     return chapter_pages, chapter_titles



# def save_split_pdf(doc, chapter_pages, chapter_titles, pdf_name):
#     """
#     Save the split PDFs based on the identified chapter pages and titles.
#     """
#     for i in range(len(chapter_pages) - 1):
#         chapter_pdf = fitz.open()  # Create a new PDF for each chapter
#         chapter_title = chapter_titles[i].replace(" ", "_")  # Clean title for file names
#         for page_num in range(chapter_pages[i], chapter_pages[i+1]):
#             chapter_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)

#         if chapter_pdf.page_count > 0:
#             chapter_pdf.save(f'pdf_breakdown_{pdf_name}/{chapter_title}.pdf')
#             print(f'{chapter_title}.pdf saved in Folder pdf_breakdown_{pdf_name}.')
#         else:
#             print(f'Skipped saving {chapter_title}.pdf as it has no pages.')

#     # Handle the last chunk/chapter
#     last_chapter_pdf = fitz.open()
#     last_chapter_title = chapter_titles[-1].replace(" ", "_")
#     for page_num in range(chapter_pages[-1], len(doc)):
#         last_chapter_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)

#     if last_chapter_pdf.page_count > 0:
#         last_chapter_pdf.save(f'pdf_breakdown_{pdf_name}/{last_chapter_title}.pdf')
#         print(f'{last_chapter_title}.pdf saved in Folder pdf_breakdown_{pdf_name}.')
#     else:
#         print(f'Skipped saving {last_chapter_title}.pdf as it has no pages.')

# def split_pdf_by_chapters(input_pdf, chapter_names=None, font_threshold=0):
#     """
#     Main function to split the PDF based on chapter names, font size, or word count.
#     """
#     doc = fitz.open(input_pdf)
#     pdf_name = input_pdf.split(".")[0] if len(input_pdf) < 80 else input_pdf.split(".")[0][:80]
#     make_directory(f"pdf_breakdown_{pdf_name}")

#     chapter_pages = []
#     chapter_titles = []

#     # Case 1: Chunk by chapter names if font_threshold is 0 and chapter names exist
#     if font_threshold == 0 and chapter_names:
#         chapter_pages, chapter_titles = get_pages_by_word_count(doc)
#         # chapter_names_lower = [name.lower() for name in chapter_names]  # Case-insensitive
#         # chapter_pages, chapter_titles = get_chapter_pages_by_names(doc, chapter_names_lower)

#     # Case 2: Chunk by font size if chapter_names is empty and font_threshold > 0
#     elif not chapter_names and font_threshold > 0:
#         chapter_pages, chapter_titles = get_chapter_pages_by_font(doc, font_threshold)

#     # Case 3: Chunk by word count if both chapter_names and font_threshold are invalid
#     else:
#         chapter_pages, chapter_titles = get_pages_by_word_count(doc)

#     # Save the split PDFs
#     save_split_pdf(doc, chapter_pages, chapter_titles, pdf_name)

#     doc.close()



# def split_pdf_by_chapters(input_pdf, chapter_names, font_threshold):
#     doc = fitz.open(input_pdf)
#     pdf_name = input_pdf.split(".")[0] if len(input_pdf) < 40 else input_pdf.split(".")[0][:40]
#     os.mkdir(f"pdf_breakdown_{pdf_name}")
#     chapter_pages = []
#     chapter_titles = []
#     chapter_start = 0
#     chapter_names_lower = [name.lower() for name in chapter_names]  # Make chapter names case-insensitive

#     # Identify chapter pages based on font size and chapter names
#     for page_num in range(len(doc)):
#         page = doc.load_page(page_num)
#         blocks = page.get_text("dict")["blocks"]
#         for block in blocks:
#             for line in block.get("lines", []):
#                 for span in line.get("spans", []):
#                     text = span["text"].strip().lower()  # Convert the text to lowercase for case-insensitive matching
#                     font_size = span["size"]

#                     # Check if the span contains large font (chapter title) and matches a chapter name
#                     for chapter_name in chapter_names_lower:
#                         if font_size >= font_threshold and chapter_name in text:
#                             if chapter_start != page_num:
#                                 chapter_pages.append(chapter_start)  # Mark the start of a new chapter
#                                 chapter_titles.append(text)  # Append the chapter title
#                             chapter_start = page_num
#                             break

#     # Add the last chapter's starting page if any
#     chapter_pages.append(chapter_start)

#     # Split and save each chapter into a separate PDF using chapter titles
#     for i in range(len(chapter_pages) - 1):
#         chapter_pdf = fitz.open()  # Create a new PDF for each chapter
#         chapter_title = chapter_titles[i].replace(" ", "_")  # Clean the chapter name for use in a file name
#         for page_num in range(chapter_pages[i], chapter_pages[i+1]):
#             chapter_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)
            
#         chapter_pdf.save(f'pdf_breakdown_{pdf_name}/{chapter_title}.pdf')  # Save the PDF with the chapter name
#         print(f'{chapter_title}.pdf saved in Folder pdf_breakdown_{pdf_name}.')

#     doc.close()



# def get_first_1000_words(*, pdf_path: str)-> str:
#     # Open the PDF file
#     pdf_document = fitz.open(pdf_path)
    
#     word_list = []  # List to hold the words
#     word_count = 0  # Keep track of how many words we've extracted
    
#     # Loop through the pages in the PDF
#     for page_num in range(len(pdf_document)):
#         page = pdf_document.load_page(page_num)
#         text: str = page.get_text("text")  # Extract text from the page
        
#         # Split the text into individual words
#         words: List = text.split()
        
#         # Add words to the list until we reach 1000 words
#         for word in words:
#             word_list.append(word)
#             word_count += 1
#             if word_count >= 1000:
#                 break
        
#         # If we have 1000 words, stop extracting
#         if word_count >= 1000:
#             break
    
#     pdf_document.close()
    
#     # Return the first 1000 words as a single string
#     return ' '.join(word_list)



# class PromptTemplate(Enum):
    
#     get_chapter_prompt = """
#     I have a list of headers from a textbook. Which of them are chapter of the textbook? Give me only the chapter names, nothing else, not even a numbering. I only want a the chapter names separated by a newline character
#     I don't want any kind of numbering whatsoever. Remove all section labels or numbering as well. You can keep the section names.
#     Things like 'PART 1: Writing' is a section label with a chapter name. Remove the section label so that we have only 'Writing'. 
#     The title of the book is: {book_title}
#     The list of headers are given below:
#     {headers}
#     """
    

# # 1. Chunk by both chapter names and font threshold
# def chunk_by_chapters_and_font(input_pdf, chapter_names, font_threshold):
#     doc = fitz.open(input_pdf)
#     pdf_name = input_pdf.split(".")[0] if len(input_pdf) < 80 else input_pdf.split(".")[0][:80]
#     foldername = remove_special_characters(pdf_name)
#     make_directory(f"pdf_breakdown_{foldername}")

#     chapter_pages = []
#     current_chapter_title = None
#     chapter_start = None

#     for page_num in range(len(doc)):
#         page = doc.load_page(page_num)
#         blocks = page.get_text("dict")["blocks"]

#         for block in blocks:
#             for line in block.get("lines", []):
#                 for span in line.get("spans", []):
#                     text = span["text"].strip().lower()
#                     font_size = span["size"]

#                     # Check if span matches chapter name and font size
#                     for chapter_name in chapter_names:
#                         if font_size >= font_threshold and chapter_name.lower() in text:
#                             if chapter_start is not None:
#                                 page_text = page.get_text()
                                
#                                 save_chunk(doc, chapter_start, page_num, current_chapter_title, pdf_name, f"pdf_breakdown_{foldername}")
#                             chapter_start = page_num
#                             current_chapter_title = chapter_name
#                             break

#     # Save the last chunk
#     if chapter_start is not None:
#         save_chunk(doc, chapter_start, len(doc), current_chapter_title, pdf_name, f"pdf_breakdown_{foldername}")
#     doc.close()
