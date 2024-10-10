# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 23:57:55 2024

@author: olanr
"""



"""
process_pdf.py

This module orchestrates the extraction, chunking, and storage of text from PDF documents.

Modules used:
    - SemanticChunking: For extracting and chunking text from PDFs.
    - Auxiliary functions: For directory creation and JSON file handling.

Workflow:
    1. Define the PDF file and output folder paths.
    2. Initialize the SemanticChunking class with the PDF path.
    3. Extract text from the PDF.
    4. Chunk the extracted content into semantic segments.
    5. Create a mapping of text chunks to their respective page numbers.
    6. Normalize the page mappings for consistency.
    7. Derive final mappings for both chunks and pages.
    8. Create necessary directories for output files.
    9. Save the final mappings to JSON files for later access.
"""




import os

from sematic_chunking import SemanticChunking
from auxillaries import (convert_final_map_to_json, 
                         make_directory, 
                         convert_pages_map_to_json
                         )


# Define constants for file paths
book_name = "babok_guide_v3.pdf" 
BOOK_FOLDER = "Textbooks"
JSON_FOLDER = "book_in_json_step_1"


# Construct the full path to the PDF file
pdf_path = os.path.join("..", BOOK_FOLDER, book_name)

# Initialize the SemanticChunking class
sc = SemanticChunking(pdf_path)

# Extract text from the PDF
pdf_content = sc.extract_book_text()

# Chunk the extracted content
chunks = sc.chunk_pdf_content(pdf_content)

# Create a mapping of text chunks to their corresponding page numbers
text_to_page_map = sc.texts_to_page_mapping(chunks)

# Normalize the page mappings
text_to_page_map = sc.normalize_pages(text_to_page_map)

# Derive final mappings of chunks and pages
final_map, pages_map = sc.derive_final_maps(text_to_page_map)

# Create a directory for JSON outputs
json_directory = os.path.join("..", JSON_FOLDER)
make_directory(json_directory)

# Convert final mappings to JSON files
convert_final_map_to_json(final_map, book_name, json_directory)
convert_pages_map_to_json(pages_map, book_name, json_directory)