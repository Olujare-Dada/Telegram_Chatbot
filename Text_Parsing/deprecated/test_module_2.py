# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 03:34:49 2024

@author: olanr
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open

import os


# Assume get_first_1000_words is in a module named 'module_2'

from pdf_breakdown_babok_guide_v3 import (get_first_1500_words, 
                                          extract_prospective_textbook_chapters,
                                          get_confirmed_chapter_font_size,
                                          remove_special_characters
                                          )


from pdf_chunkers import (chunk_by_word_count,
                          chunk_by_chapters_only,
                          save_chunk,
                          extract_chapter_text_in_batches,
                          extract_text_in_batches,
                          )





# Assume the function get_first_1500_words is imported here

class TestGetFirst1500Words(unittest.TestCase):
    
    @patch('fitz.open')
    def test_no_toc(self, mock_open):
        # Mock a PDF document with 3 pages of text
        mock_pdf_document = MagicMock()
        mock_pdf_document.get_toc.return_value = []
        mock_pdf_document.load_page.side_effect = [
            MagicMock(get_text=MagicMock(return_value='word1 word2 word3')),
            MagicMock(get_text=MagicMock(return_value='word4 word5 word6')),
            MagicMock(get_text=MagicMock(return_value='word7 word8 word9 word10'))
        ]
        mock_pdf_document.__len__.return_value = 3
        mock_open.return_value = mock_pdf_document
        
        result = get_first_1500_words(pdf_path='dummy_path.pdf')
        expected_result = 'word1 word2 word3 word4 word5 word6 word7 word8 word9 word10'
        
        self.assertEqual(result, expected_result)


    # @patch('fitz.open')
    # def test_with_toc(self, mock_open):
    #     # Mock a PDF document with a TOC and enough content
    #     mock_pdf_document = MagicMock()
    #     mock_pdf_document.get_toc.return_value = [[1, 'Introduction', 2]]
    #     mock_pdf_document.load_page.side_effect = [
    #         MagicMock(get_text=MagicMock(return_value=' '.join([f'word{i}' for i in range(1, 501)]))),  # 500 words
    #         MagicMock(get_text=MagicMock(return_value=' '.join([f'word{i}' for i in range(501, 1001)]))),  # 500 words
    #         MagicMock(get_text=MagicMock(return_value=' '.join([f'word{i}' for i in range(1001, 1501)])))  # 500 words
    #     ]
    #     mock_pdf_document.__len__.return_value = 3
    #     mock_open.return_value = mock_pdf_document
        
    #     result = get_first_1500_words(pdf_path='dummy_path.pdf')
        
    #     # Build the expected result from 1 to 1500 words
    #     expected_result = ' '.join([f'word{i}' for i in range(1, 1501)])  # 1500 words
        
    #     self.assertEqual(result, expected_result)
        
        
    @patch('fitz.open')
    def test_not_enough_words(self, mock_open):
        # Mock a PDF document with not enough words to reach 1500
        mock_pdf_document = MagicMock()
        mock_pdf_document.get_toc.return_value = []
        mock_pdf_document.load_page.side_effect = [
            MagicMock(get_text=MagicMock(return_value='word1 word2')),
            MagicMock(get_text=MagicMock(return_value='word3 word4')),
        ]
        mock_pdf_document.__len__.return_value = 2
        mock_open.return_value = mock_pdf_document
        
        result = get_first_1500_words(pdf_path='dummy_path.pdf')
        expected_result = 'word1 word2 word3 word4'
        
        self.assertEqual(result, expected_result)

    @patch('fitz.open')
    def test_empty_pdf(self, mock_open):
        # Mock an empty PDF document
        mock_pdf_document = MagicMock()
        mock_pdf_document.get_toc.return_value = []
        mock_pdf_document.__len__.return_value = 0
        mock_open.return_value = mock_pdf_document
        
        result = get_first_1500_words(pdf_path='dummy_path.pdf')
        
        self.assertEqual(result, '')
        

class TestExtractProspectiveTextbookChapters(unittest.TestCase):

    @patch('fitz.open')
    def test_extract_chapters_success(self, mock_open):
        # Mock a PDF document with a ToC containing chapters
        mock_pdf_document = MagicMock()
        mock_pdf_document.get_toc.return_value = [
            [1, 'Introduction', 1],
            [2, 'Chapter 1: Getting Started', 2],
            [3, 'Chapter 2: Advanced Topics', 3]
        ]
        mock_open.return_value = mock_pdf_document
        
        # Call the function
        result = extract_prospective_textbook_chapters(textbook_filepath='dummy_path.pdf')
        
        # Expected chapter titles
        expected_result = [
            'Introduction',
            'Chapter 1: Getting Started',
            'Chapter 2: Advanced Topics'
        ]
        
        self.assertEqual(result, expected_result)

    @patch('fitz.open')
    def test_no_chapters(self, mock_open):
        # Mock a PDF document with an empty ToC
        mock_pdf_document = MagicMock()
        mock_pdf_document.get_toc.return_value = []
        mock_open.return_value = mock_pdf_document
        
        # Call the function
        result = extract_prospective_textbook_chapters(textbook_filepath='dummy_path.pdf')
        
        # Expecting an empty list
        expected_result = []
        
        self.assertEqual(result, expected_result)

    @patch('fitz.open')
    def test_file_not_found(self, mock_open):
        # Mock opening a file that raises an exception
        mock_open.side_effect = FileNotFoundError("File not found")
        
        with self.assertRaises(FileNotFoundError):
            extract_prospective_textbook_chapters(textbook_filepath='dummy_path.pdf')

    @patch('fitz.open')
    def test_invalid_toc_structure(self, mock_open):
        # Mock a PDF document with an invalid ToC structure
        mock_pdf_document = MagicMock()
        mock_pdf_document.get_toc.return_value = [
            [1, 'Introduction', 1],
            ['Invalid Chapter Structure']  # Invalid structure
        ]
        mock_open.return_value = mock_pdf_document
        
        # Call the function
        result = extract_prospective_textbook_chapters(textbook_filepath='dummy_path.pdf')
        
        # We expect the valid chapters to be extracted
        expected_result = ['Introduction']
        
        self.assertEqual(result, expected_result)
        
        
class TestGetConfirmedChapterFontSize(unittest.TestCase):

    def test_empty_dictionary(self):
        result = get_confirmed_chapter_font_size({})
        self.assertEqual(result, -1.0)

    def test_no_valid_font_sizes(self):
        chapter_font_sizes = {
            'Chapter 1': -12.0,
            'Chapter 2': 0.0,
            'Chapter 3': -10.5
        }
        result = get_confirmed_chapter_font_size(chapter_font_sizes)
        self.assertEqual(result, -1.0)

    def test_single_font_size(self):
        chapter_font_sizes = {
            'Chapter 1': 12.0
        }
        result = get_confirmed_chapter_font_size(chapter_font_sizes)
        self.assertEqual(result, 12.0)

    def test_multiple_font_sizes_same_value(self):
        chapter_font_sizes = {
            'Chapter 1': 12.0,
            'Chapter 2': 12.0,
            'Chapter 3': 12.0
        }
        result = get_confirmed_chapter_font_size(chapter_font_sizes)
        self.assertEqual(result, 12.0)

    def test_multiple_font_sizes_different_values(self):
        chapter_font_sizes = {
            'Chapter 1': 12.0,
            'Chapter 2': 14.0,
            'Chapter 3': 12.0,
            'Chapter 4': 16.0,
            'Chapter 5': 13.0
        }
        result = get_confirmed_chapter_font_size(chapter_font_sizes)
        self.assertEqual(result, -1.0)  # 12.0 is the most common

    def test_multiple_font_sizes_no_majority(self):
        chapter_font_sizes = {
            'Chapter 1': 12.0,
            'Chapter 2': 14.0,
            'Chapter 3': 16.0
        }
        result = get_confirmed_chapter_font_size(chapter_font_sizes)
        self.assertEqual(result, -1.0)  # No majority



class TestRemoveSpecialCharacters(unittest.TestCase):

    def test_empty_string(self):
        # Test with an empty string
        result = remove_special_characters("")
        self.assertEqual(result, "")

    def test_no_special_characters(self):
        # Test with a string that has no special characters
        result = remove_special_characters("Hello World")
        self.assertEqual(result, "Hello World")

    def test_special_characters(self):
        # Test with a string that contains special characters
        result = remove_special_characters("Hello, World! This is a test.")
        self.assertEqual(result, "Hello World This is a test")

    def test_multiple_spaces(self):
        # Test with a string that contains multiple spaces
        result = remove_special_characters("Hello    World!!!  This is   a test.")
        self.assertEqual(result, "Hello World This is a test")

    def test_only_special_characters(self):
        # Test with a string that contains only special characters
        result = remove_special_characters("!!!@@@###$$$")
        self.assertEqual(result, "")

    def test_numbers_and_special_characters(self):
        # Test with a string that contains numbers and special characters
        result = remove_special_characters("123 Main St. #1")
        self.assertEqual(result, "123 Main St 1")

    def test_leading_and_trailing_special_characters(self):
        # Test with leading and trailing special characters
        result = remove_special_characters("!!!Hello World!!!")
        self.assertEqual(result, "Hello World")


class TestChunkByWordCount(unittest.TestCase):

    @patch('module_2.fitz.open')
    @patch('module_2.remove_special_characters')
    @patch('module_2.make_directory')
    @patch('module_2.save_chunk')
    def test_chunk_by_word_count(self, mock_save_chunk, mock_make_directory, mock_remove_special_characters, mock_fitz_open):
        # Set up the mock for fitz.open
        mock_doc = MagicMock()
        mock_fitz_open.return_value = mock_doc
        
        # Mock the number of pages in the PDF
        mock_doc.__len__.return_value = 5  # Simulating a PDF with 5 pages
        mock_doc.load_page.return_value.get_text.return_value = "word " * 250  # 250 words per page

        # Set up mocks for other functions
        mock_remove_special_characters.return_value = "Test_PDF"
        mock_make_directory.return_value = "pdf_breakdown_Test_PDF"

        # Call the function under test
        result = chunk_by_word_count("dummy_path/Textbooks/test.pdf", word_limit=1000)

        # Check that the correct directory was returned
        self.assertEqual(result, "pdf_breakdown_Test_PDF")

        # Check that the save_chunk function is called twice (two chunks of 1000 words each)
        self.assertEqual(mock_save_chunk.call_count, 2)

        # Verify the arguments passed to save_chunk
        self.assertEqual(mock_save_chunk.call_args_list[0][0][1], 0)  # chapter_start for first chunk
        self.assertEqual(mock_save_chunk.call_args_list[0][0][2], 4)  # page_num for first chunk (up to page 4)
        self.assertEqual(mock_save_chunk.call_args_list[1][0][1], 4)  # chapter_start for second chunk (next page)
        self.assertEqual(mock_save_chunk.call_args_list[1][0][2], 5)  # page_num for second chunk (end of the document)

        # Check that the document is closed after processing
        mock_doc.close.assert_called_once()




class TestChunkByChaptersOnly(unittest.TestCase):

    @patch('module_2.fitz.open')
    @patch('module_2.remove_special_characters')
    @patch('module_2.make_directory')
    @patch('module_2.save_chunk')
    def test_chunk_by_chapters_only(self, mock_save_chunk, mock_make_directory, mock_remove_special_characters, mock_fitz_open):
        # Set up the mock for fitz.open
        mock_doc = MagicMock()
        mock_fitz_open.return_value = mock_doc
        
        # Mock the number of pages in the PDF
        mock_doc.__len__.return_value = 5  # Simulating a PDF with 5 pages
        mock_doc.load_page.return_value.get_text.side_effect = [
            "This is the introduction.",  # Page 0
            "Chapter 1: Basics",          # Page 1
            "Content of chapter 1.",       # Page 2
            "Chapter 2: Advanced Topics",  # Page 3
            "Content of chapter 2."         # Page 4
        ]

        # Set up mocks for other functions
        mock_remove_special_characters.side_effect = lambda x: x.replace(" ", "_")  # Simple mock for demonstration
        mock_make_directory.return_value = "pdf_breakdown_Test_PDF"

        # Define the chapter names we're searching for
        chapter_names = ["Chapter 1: Basics", "Chapter 2: Advanced Topics"]

        # Call the function under test
        result = chunk_by_chapters_only("dummy_path/Textbooks/test.pdf", chapter_names)

        # Check that the correct directory was returned
        self.assertEqual(result, "pdf_breakdown_Test_PDF")

        # Check that save_chunk was called twice (once for each chapter)
        self.assertEqual(mock_save_chunk.call_count, 2)

        # Verify the arguments passed to save_chunk for Chapter 1
        self.assertEqual(mock_save_chunk.call_args_list[0][0][1], 1)  # chapter_start for Chapter 1
        self.assertEqual(mock_save_chunk.call_args_list[0][0][2], 3)  # page_num for Chapter 1 (up to Page 3)
        self.assertEqual(mock_save_chunk.call_args_list[0][0][3], "Chapter_1:_Basics")  # title for Chapter 1

        # Verify the arguments passed to save_chunk for Chapter 2
        self.assertEqual(mock_save_chunk.call_args_list[1][0][1], 3)  # chapter_start for Chapter 2
        self.assertEqual(mock_save_chunk.call_args_list[1][0][2], 5)  # page_num for Chapter 2 (end of the document)
        self.assertEqual(mock_save_chunk.call_args_list[1][0][3], "Chapter_2:_Advanced_Topics")  # title for Chapter 2

        # Check that the document is closed after processing
        mock_doc.close.assert_called_once()
        

class TestSaveChunk(unittest.TestCase):
    
    @patch('fitz.open')
    def test_save_chunk_success(self, mock_open):
        # Arrange
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_open.return_value = mock_page
        
        # Mock the behavior of loading pages
        mock_doc.load_page.side_effect = [MagicMock(), MagicMock()]  # Simulate two pages being loaded
        mock_page.insert_pdf = MagicMock()
        
        # Assume that we want to save pages from 0 to 2
        chapter_start = 0
        page_num = 2
        title = "Chapter 1"
        pdf_name = "sample.pdf"
        save_dir = "test_directory"
        
        # Act
        save_chunk(mock_doc, chapter_start, page_num, title, pdf_name, save_dir)

        # Assert
        mock_page.insert_pdf.assert_called()
        #mock_page.save.assert_called_once_with(f'test_directory/Chapter_1.pdf')
        #mock_page.close.assert_called_once()

    @patch('fitz.open')
    def test_save_chunk_no_pages(self, mock_open):
        # Arrange
        mock_doc = MagicMock()
        mock_open.return_value = mock_doc
        
        # Mock the behavior of loading pages
        mock_doc.load_page.side_effect = []
        
        chapter_start = 0
        page_num = 0  # No pages to save
        title = "Empty Chapter"
        pdf_name = "sample.pdf"
        save_dir = "test_directory"

        # Act
        save_chunk(mock_doc, chapter_start, page_num, title, pdf_name, save_dir)

        # Assert
        mock_doc.load_page.assert_not_called()  # No pages should be loaded
        #mock_open.assert_not_called()  # No PDF should be created



class TestExtractTextInBatches(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data='This is a test PDF content. ' * 200)
    @patch('PyPDF2.PdfReader')
    def test_extract_text_in_batches_success(self, mock_pdf_reader, mock_open):
        # Arrange
        mock_pdf_reader.return_value.pages = [mock_pdf_reader.return_value] * 10  # Simulate 10 pages
        mock_pdf_reader.return_value.pages[0].extract_text.return_value = 'This is a test PDF content. ' * 200
        
        pdf_path = 'test_book.pdf'
        batch_size = 15  # Small batch size for easy verification

        # Act
        result = extract_text_in_batches(pdf_path, batch_size)

        # Assert
        textbook_name = os.path.basename(pdf_path).replace('.pdf', '')
        expected_batches = [' '.join(['This', 'is', 'a', 'test', 'PDF', 'content.', 'This', 'is', 'a', 'test', 'PDF', 'content.'] * 5)] * 10  # Simplified expected result for brevity
        #self.assertEqual(len(result[textbook_name]), len(expected_batches))
        self.assertTrue(all(len(batch.split()) <= batch_size for batch in result[textbook_name]))

    @patch('builtins.open', new_callable=mock_open, read_data='Test')
    @patch('PyPDF2.PdfReader')
    def test_extract_text_single_batch(self, mock_pdf_reader, mock_open):
        # Arrange
        mock_pdf_reader.return_value.pages = [mock_pdf_reader.return_value] * 1
        mock_pdf_reader.return_value.pages[0].extract_text.return_value = 'Test'

        pdf_path = 'single_batch.pdf'
        batch_size = 10  # Larger batch size than the number of words

        # Act
        result = extract_text_in_batches(pdf_path, batch_size)

        # Assert
        textbook_name = os.path.basename(pdf_path).replace('.pdf', '')
        self.assertEqual(result[textbook_name], ['Test'])  # Expect one batch with the single word

    @patch('builtins.open', new_callable=mock_open, read_data='')
    @patch('PyPDF2.PdfReader')
    def test_extract_text_empty_pdf(self, mock_pdf_reader, mock_open):
        # Arrange
        mock_pdf_reader.return_value.pages = [mock_pdf_reader.return_value] * 1
        mock_pdf_reader.return_value.pages[0].extract_text.return_value = ''

        pdf_path = 'empty_pdf.pdf'
        batch_size = 5

        # Act
        result = extract_text_in_batches(pdf_path, batch_size)

        # Assert
        textbook_name = os.path.basename(pdf_path).replace('.pdf', '')
        self.assertEqual(result[textbook_name], [''])  # Expect an empty batch

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_extract_text_file_not_found(self, mock_open):
        # Arrange
        pdf_path = 'non_existent.pdf'
        batch_size = 1500

        # Act & Assert
        with self.assertRaises(FileNotFoundError):
            extract_text_in_batches(pdf_path, batch_size)


class TestExtractChapterTextInBatches(unittest.TestCase):

    @patch('os.listdir')
    @patch('os.path.join')
    @patch('module_2.extract_text_in_batches')  # Update with your actual import path
    def test_extract_chapter_text_in_batches_success(self, mock_extract, mock_path_join, mock_listdir):
        # Arrange
        dir_name = 'test_directory'
        chapter_files = ['chapter1.pdf', 'chapter2.pdf']
        
        mock_listdir.return_value = chapter_files
        mock_path_join.side_effect = lambda dir, file: f"{dir}/{file}"
        
        # Mock the return value of extract_text_in_batches
        mock_extract.side_effect = [
            { 'chapter1': ['batch 1.1', 'batch 1.2'] },
            { 'chapter2': ['batch 2.1', 'batch 2.2'] }
        ]

        # Act
        result = extract_chapter_text_in_batches(dir_name)

        # Assert
        expected_result = {
            'chapter1': ['batch 1.1', 'batch 1.2'],
            'chapter2': ['batch 2.1', 'batch 2.2']
        }
        self.assertEqual(result, expected_result)

    @patch('os.listdir')
    @patch('os.path.join')
    @patch('module_2.extract_text_in_batches')  # Update with your actual import path
    def test_extract_chapter_text_in_batches_empty_directory(self, mock_extract, mock_path_join, mock_listdir):
        # Arrange
        dir_name = 'empty_directory'
        mock_listdir.return_value = []  # No files in the directory
        
        # Act
        result = extract_chapter_text_in_batches(dir_name)

        # Assert
        self.assertEqual(result, {})

    @patch('os.listdir')
    @patch('os.path.join')
    @patch('module_2.extract_text_in_batches')  # Update with your actual import path
    def test_extract_chapter_text_in_batches_with_missing_files(self, mock_extract, mock_path_join, mock_listdir):
        # Arrange
        dir_name = 'test_directory'
        chapter_files = ['chapter1.pdf', 'chapter2.pdf']
        
        mock_listdir.return_value = chapter_files
        mock_path_join.side_effect = lambda dir, file: f"{dir}/{file}"
        
        # Simulate that one of the chapters fails to extract text
        mock_extract.side_effect = [
            { 'chapter1': ['batch 1.1', 'batch 1.2'] },
            Exception("Failed to read chapter")
        ]

        # Act
        with self.assertRaises(Exception) as context:
            extract_chapter_text_in_batches(dir_name)

        # Assert
        self.assertEqual(str(context.exception), "Failed to read chapter")


# class TestChunkByWordCount(unittest.TestCase):

#     @patch('fitz.open')
#     @patch('module_2.remove_special_characters')
#     @patch('module_2.make_directory')
#     @patch('module_2.save_chunk')
#     def test_chunk_by_word_count(self, mock_save_chunk, mock_make_directory, mock_remove_special_characters, mock_fitz_open):
#         # Set up the mock for fitz.open
#         mock_doc = MagicMock()
#         mock_fitz_open.return_value = mock_doc
        
#         # Mock the number of pages in the PDF
#         mock_doc.__len__.return_value = 5  # Simulating a PDF with 5 pages
#         mock_doc.load_page.return_value.get_text.return_value = "word " * 250  # 250 words per page

#         # Set up mocks for other functions
#         mock_remove_special_characters.return_value = "Test_PDF"
#         mock_make_directory.return_value = "pdf_breakdown_Test_PDF"

#         # Call the function under test
#         result = chunk_by_word_count("dummy_path/Textbooks/test.pdf", word_limit=1000)

#         # Check that the correct directory was returned
#         self.assertEqual(result, "pdf_breakdown_Test_PDF")

#         # Check that the save_chunk function is called twice (two chunks of 1000 words each)
#         self.assertEqual(mock_save_chunk.call_count, 2)

#         # Verify the arguments passed to save_chunk
#         self.assertEqual(mock_save_chunk.call_args_list[0][0][1], 0)  # chapter_start for first chunk
#         self.assertEqual(mock_save_chunk.call_args_list[0][0][2], 4)  # page_num for first chunk (up to page 4)
#         self.assertEqual(mock_save_chunk.call_args_list[1][0][1], 5)  # chapter_start for second chunk (last page)

#         # Check that the document is closed after processing
#         mock_doc.close.assert_called_once()

# class TestGetFirst1000Words(unittest.TestCase):

#     @patch('fitz.open')  # Mock the fitz.open method
#     def test_get_first_1500_words(self, mock_fitz_open):
#         # Create a mock PDF document and pages
#         mock_pdf = MagicMock()
#         mock_page = MagicMock()

#         # Mock the text for the pages
#         mock_page.get_text.return_value = "word " * 750  # 500 "word" entries per page
#         mock_pdf.load_page.side_effect = [mock_page, mock_page]  # Two pages with 500 words each
#         mock_pdf.__len__.return_value = 2  # Assume PDF has two pages
        
#         # Mock the fitz.open return value
#         mock_fitz_open.return_value = mock_pdf

#         # Call the function
#         result = get_first_1500_words(pdf_path="dummy_path.pdf")

#         # Check if the result contains exactly 1500 words
#         self.assertEqual(len(result.split()), 1500)
#         self.assertEqual(result.split()[0], "word")  # First word should be "word"
#         self.assertEqual(result.split()[-1], "word")  # Last word should be "word"

#         # Ensure the mock methods were called
#         mock_fitz_open.assert_called_once_with("dummy_path.pdf")
#         self.assertEqual(mock_pdf.load_page.call_count, 2)  # Ensure both pages were processed




# class TestGetHighestFontSizeForEachChapter(unittest.TestCase):

#     @patch("fitz.open")
#     def test_get_highest_font_size_for_each_chapter(self, mock_fitz_open):
#         # Mock the PDF document and pages
#         mock_pdf = MagicMock()
#         mock_page = MagicMock()

#         # Set the mock PDF to have 1 page
#         mock_fitz_open.return_value = mock_pdf
#         mock_pdf.__len__.return_value = 1
#         mock_pdf.load_page.return_value = mock_page

#         # Mock the text and font size data from the PDF
#         mock_page.get_text.return_value = {
#             "blocks": [
#                 {
#                     "lines": [
#                         {"spans": [{"text": "Chapter One", "size": 12}]},
#                         {"spans": [{"text": "Introduction", "size": 10}]}
#                     ]
#                 }
#             ]
#         }

#         # Define the chapter titles
#         chapter_titles = ["Chapter One", "Introduction"]

#         # Call the function
#         result = get_highest_font_size_for_each_chapter("dummy_path.pdf", chapter_titles)

#         # Assert the results
#         expected = {"chapter one": 12, "introduction": 10}
#         self.assertEqual(result, expected)




# class TestGetGptResponse(unittest.TestCase):

#     @patch("openai.ChatCompletion.create")
#     def test_get_gpt_response(self, mock_gpt):
#         # Mock the GPT API response
#         mock_response = MagicMock()
#         mock_gpt.return_value = mock_response
#         mock_response.choices = [MagicMock(message=MagicMock(content="Chapter 1: Introduction"))]

#         # Call the function
#         result = get_gpt_response(prompt="Give me the chapters of the book")

#         # Assert the response
#         self.assertEqual(result, "Chapter 1: Introduction")





# class TestExtractProspectiveTextbookChapters(unittest.TestCase):

#     @patch("fitz.open")
#     @patch("module_2.get_first_1500_words")
#     def test_extract_prospective_textbook_chapters_with_chapters(self, mock_get_first_1500_words, mock_fitz_open):
#         # Mock the PDF document
#         mock_pdf = MagicMock()
#         mock_fitz_open.return_value = mock_pdf

#         # Simulate the Table of Contents (TOC)
#         mock_pdf.get_toc.return_value = [[1, "Chapter 1", 1], [1, "Chapter 2", 5]]

#         # Call the function
#         result = extract_prospective_textbook_chapters(textbook_filepath="dummy_path.pdf")

#         # Assert the chapters are returned
#         expected = (["Chapter 1", "Chapter 2"], "")
#         self.assertEqual(result, expected)



#     @patch("fitz.open")
#     @patch("module_2.get_first_1500_words")
#     def test_extract_prospective_textbook_chapters_without_toc(self, mock_get_first_1500_words, mock_fitz_open):
#         # Mock the PDF document
#         mock_pdf = MagicMock()
#         mock_fitz_open.return_value = mock_pdf

#         # Simulate an empty Table of Contents
#         mock_pdf.get_toc.return_value = []

#         # Mock the first 1000 words extraction
#         mock_get_first_1500_words.return_value = "Some text from the first 1000 words"

#         # Call the function
#         result = extract_prospective_textbook_chapters(textbook_filepath="dummy_path.pdf")

#         # Assert that the function returns the first 1000 words
#         expected = ([], "Some text from the first 1000 words")
#         self.assertEqual(result, expected)





if __name__ == '__main__':
    unittest.main()
