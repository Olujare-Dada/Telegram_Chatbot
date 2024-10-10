# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 08:02:32 2024

@author: olanr
"""

from openai import OpenAI
from dotenv import load_dotenv
from enum import Enum


load_dotenv()

openai_client = OpenAI()





def get_gpt_response(*, prompt: str, client: OpenAI = openai_client, model: str = "gpt-4o-mini", temperature: float = 0) -> str:
    """
    Sends a prompt to a GPT model and returns the model's response.

    Args:
        prompt (str): The input prompt for the GPT model.
        model (str, optional): The GPT model to use. Defaults to "gpt-4o-mini".
        temperature (float, optional): The temperature to control the randomness of the response. Defaults to 0.

    Returns:
        str: The generated response from the GPT model.
    
    Example:
        response = get_gpt_response(prompt="Tell me a joke.")
        # response = "Why don't scientists trust atoms? Because they make up everything!"
    """
    
    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content


class PromptTemplate(Enum):
    
    """
    Enum class containing predefined templates for generating prompts for chapter extraction.

    Attributes:
        get_chapters_prompt (str): Prompt template for extracting chapter names from headers.
        alternate_get_chapters_prompt (str): Prompt template for extracting chapter names from text.
        get_chapter_instructions (str): Instructions for the AI on how to extract chapter names.
    """
    

    get_chapters_prompt = """
    I have a list of headers from a textbook. Your task is to extract only the chapter names. Follow these instructions closely:
    {chapters_instructions}
    
    Here is the title of the book: {book_title}

    The list of headers from the textbook is provided below:
    {headers}
    """

    
    alternate_get_chapters_prompt = """
    
    I have a bunch of text extracted from the first 1000 words of a textbook. Your task is to extract the possible chapter names of the book using this extracted text.
    Follow these instructions closely:
    
    {chapters_instructions}
    
    Here is the title of the book: {book_title}

    The list of headers from the textbook is provided below:
    {headers}
    
    Finally, if the text does not contain enough or any information about textbook headers, return an empty string
    """
    
    
    get_chapter_instructions = """
    1. **Return only chapter names**: Provide only the chapter names, each on a new line. Do not include any numbering or section labels. 
    - Example: If you encounter "Chapter 1: Introduction," return only "Introduction."
    
    2. Return only main chapter titles: Extract and return only the main chapter names, without any numbering, section labels, or subsections. Each chapter name should be on a new line.

    - Example: If you see "Chapter 2: Python" and subsections like "2.1 Getting Started," return only "Python."
    
    3. Ignore subsections: Do not return any subsections, even if they have additional headings. Only return the highest-level chapter.

    - Example: From "2.1 Getting Started," "2.5 Pandas," and "2 Python," return only "Python."
    
    4. Remove section labels: If a chapter is preceded by a section label, ignore the section label but return the chapter title.
    - Example: "Part I. Writing" → "Writing"
    - Example: "Part I. Python and Statistics" → "Python and Statistics"
    
    
    5. **Keep non-chapter headers**: Do NOT Omit non-chapter headers such as "Introduction," "Conclusion," "Appendix," "Index," "Notes," "References," etc. I need them even though they are not chapter names.
    
    6. **Format**: Output the chapter names as a plain list with one chapter per line, no extra spaces, numbering, or punctuation.
    
    """
