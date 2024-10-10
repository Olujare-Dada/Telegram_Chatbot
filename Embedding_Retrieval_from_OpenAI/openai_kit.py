# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 14:38:41 2024

@author: olanr
"""


"""
openai_kit.py

This module interfaces with OpenAI's API to retrieve text responses and define prompt templates for querying.

Functions:
    - get_chatgpt_response: Sends a query to the OpenAI GPT model and returns the response.
    
Classes:
    - PromptTemplate: An enumeration defining various prompt templates for generating responses based on different contexts.

Usage:
    Import the module and use the `get_chatgpt_response` function along with the prompt templates as needed for querying OpenAI's API.
"""


from openai import OpenAI, APIConnectionError, RateLimitError
from auxiliaries import load_dotenv
from enum import Enum


load_dotenv()
openai_client = OpenAI()



def get_chatgpt_response(instruction: str, openai_client: OpenAI, temperature: float = 0.0)-> str:
    
    """
    Sends a query to the OpenAI GPT model and returns the generated response.

    Args:
        instruction (str): The instruction or question to send to the model.
        openai_client (OpenAI): The initialized OpenAI client for making requests.
        temperature (float, optional): Controls the randomness of the response. Defaults to 0.0.

    Returns:
        str: The response generated by the GPT model.
    """
    
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": instruction},
        ],
        temperature = temperature
        )
    return response.choices[0].message.content



class PromptTemplate(Enum):
    answer_from_first_text = """You are a helpful assistant. Below is information retrieved from relevant sources. Use this information to answer the following question as accurately as possible.

       Retrieved Document:
       {pinecone_text}
    
       Question: {query}
    
       Answer the question using only the information from the document. Explain your line of thought on why that answer is correct if and only if you find the answer.
    
       If the information is insufficient or not present, return an empty string. i.e. ''.
       """

    answer_from_alternative_text = """"""

    default_no_pinecone_text = """PDF provided is insufficient to answer your question: {query}.\nPinecone Text: {pinecone_text}""" #Equivalent to: Pinecone did not return any text or your text on pinecone contains empty strings

    default_pinecone_text_irrelevant = """I could not find any relevant answers to your query from the PDF provided.\nYour query:\n{query}"""