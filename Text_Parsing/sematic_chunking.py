# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 08:58:38 2024

@author: olanr
"""


from collections import Counter
import os
from typing import List, Dict, Tuple

import PyPDF2
import fitz  # PyMuPDF
from semantic_router.encoders import OpenAIEncoder
from semantic_chunkers import StatisticalChunker
from dotenv import load_dotenv



load_dotenv()


EMBEDDING_MODEL = "text-embedding-3-small"
api_key = os.getenv("OPENAI_API_KEY")



class SemanticChunking:
    
    """
    A class for extracting text from a PDF and chunking it into semantic segments.

    Attributes:
        pdf_path (str): The file path to the PDF document to be processed.
    """
    
    
    def __init__(self, pdf_path: str):
        
        """
        Initializes the SemanticChunking instance with the path to a PDF file.

        Args:
            pdf_path (str): The path to the PDF file from which to extract text.
        """
        
        self.pdf_path = pdf_path
        
        
        
    def extract_book_text(self) -> str:
        """
        Extracts all text from the PDF file.

        Returns:
            str: The complete text extracted from the PDF, or an empty string if the file does not exist.
        """
        
        if not self.pdf_path:
            return ""
    
        try:
            with open(self.pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                full_text = ""
                
                # Extract text from all the pages
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    full_text += page.extract_text()
                    
        except FileNotFoundError:
            print(f"PDF Filepath: {self.pdf_path} does not exist")
            return ""
            
        return full_text
    
    

    def chunk_pdf_content(self, pdf_content: str) -> List:
        """
        Divides the provided PDF content into semantic chunks.

        Args:
            pdf_content (str): The text content of the PDF to be chunked.

        Returns:
            List: A list of semantic chunks derived from the PDF content.
        """
        
        if not pdf_content:
            return []
        
        encoder = OpenAIEncoder(name=EMBEDDING_MODEL)  # Placeholder for actual model
        chunker = StatisticalChunker(encoder=encoder)  # Placeholder for actual chunker

        chunks = chunker(docs=[pdf_content])
        return chunks



    def _gather_all_search_texts(self, chunks: List) -> List:
        """
        Collects all subtexts from the provided chunks.

        Args:
            chunks (List): The list of semantic chunks from which to gather subtexts.

        Returns:
            List: A list of all subtexts found in the chunks.
        """
        
        all_search_texts = []
        if chunks:
            for chunk in chunks[0]:
                all_search_texts.append(chunk.splits)  # Assuming `chunk.splits` gives the subtexts
        return all_search_texts



    def _get_text_to_page_mapping(self) -> Dict:
        
        """
        Creates a mapping of page numbers to their respective text content.

        Returns:
            Dict: A dictionary where keys are page numbers and values are the corresponding text.
        """
        
        page_text_map = {}
        
        try:
            with fitz.open(self.pdf_path) as pdf:
                # Loop through all pages and get their text
                for page_num in range(len(pdf)):
                    page = pdf.load_page(page_num)
                    page_text_map[page_num + 1] = page.get_text().replace("\n", "").replace("\t", "")
        except FileNotFoundError:
            print(f"PDF Filepath: {self.pdf_path} does not exist")
            return {}
        
        return page_text_map



    def _get_subtext_to_page_map(self, page_text_map: Dict, search_texts: List) -> Dict:
        
        """
        Maps subtexts to the page numbers where they are found.

        Args:
            page_text_map (Dict): A dictionary mapping page numbers to their text content.
            search_texts (List): A list of subtexts to search for within the page content.

        Returns:
            Dict: A dictionary mapping subtexts to their corresponding page numbers.
        """
        
        search_texts_map = {}
        page_numbers = []
    
        for sentence in search_texts:
            for page_num, page_text in page_text_map.items():
                if sentence.lower() in page_text.lower():  # Case-insensitive search
                    page_numbers.append(page_num)
    
        if page_numbers:
            most_common_page = max(set(page_numbers), key=page_numbers.count)  # Find most common page without Counter
            search_texts_map[" ".join(search_texts)] = most_common_page
        else:
            search_texts_map[" ".join(search_texts)] = -1

        return search_texts_map
    
    

    def texts_to_page_mapping(self, chunks: List) -> Dict:
        
        """
        Creates a mapping of text chunks to the pages they originate from.

        Args:
            chunks (List): A list of semantic chunks from the PDF.

        Returns:
            Dict: A dictionary mapping each chunk to its respective page number.
        """
        
        if not chunks or not chunks[0]:
            return {}
    
        chunk_mapping = {}
        
        all_search_texts = self._gather_all_search_texts(chunks)  # Pre-process search texts
        print(f"Collected {len(all_search_texts)} search texts.")
    
        page_text_map = self._get_text_to_page_mapping()
        print("Page text mapping complete.")
    
        for search_texts in all_search_texts:
            search_texts_map = self._get_subtext_to_page_map(page_text_map, search_texts)
            chunk_mapping.update(search_texts_map)
    
        return chunk_mapping



    @staticmethod
    def normalize_pages(texts_to_page_map: Dict):
        
        """
        Normalizes page numbers in the mapping to ensure they are sequential.

        Args:
            texts_to_page_map (Dict): A mapping of text to page numbers.

        Returns:
            Dict: The updated mapping with normalized page numbers.
        """
        
        previous_page = 0
    
        for text in texts_to_page_map.keys():
            if texts_to_page_map[text] < 0:
                texts_to_page_map[text] = previous_page
            else:
                previous_page = texts_to_page_map[text]
    
        return texts_to_page_map
    
    

    @staticmethod    
    def derive_final_maps(texts_to_page_map: Dict) -> Tuple[Dict, Dict]:
        
        """
        Derives the final mappings of chunks and their corresponding pages.

        Args:
            texts_to_page_map (Dict): A mapping of text to page numbers.

        Returns:
            Tuple[Dict, Dict]: Two dictionaries, one for chunk mappings and one for page mappings.
        """
        
        final_map = {}
        pages_map = {}
        
        for idx, text in enumerate(texts_to_page_map.keys()):
            final_map[f"chunk_{idx}"] = [text]
            pages_map[f"chunk_{idx}"] = texts_to_page_map[text]
    
        return final_map, pages_map

# Example usage



