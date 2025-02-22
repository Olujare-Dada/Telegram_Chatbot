"""
openai_kit.py

This module serves as a wrapper around OpenAI's API functionalities, enabling the retrieval of embeddings and responses from the ChatGPT model. It abstracts away the complexity of direct API calls and provides helper functions for common operations.

Usage:
    This module can be imported into other scripts or modules to leverage OpenAI's API capabilities for generating embeddings and chat responses.

Main Functions:
- get_embedding: Takes a text input and retrieves its embedding from OpenAI's API.
- get_chatgpt_response: Sends a user instruction to the ChatGPT model and returns the model's response.
  
Enums:
- PromptTemplate: Defines various prompt templates used in the interaction with the chatbot, aiding in the structuring of queries and responses.
"""


from openai import OpenAI
from openai import OpenAI, APIConnectionError, RateLimitError
from auxiliaries import np
from auxiliaries import load_dotenv
from enum import Enum


load_dotenv()
openai_client = OpenAI()


def get_embedding(text: str, openai_client: OpenAI, model: str ="text-embedding-3-small")-> np.ndarray:
    
    """
    Retrieves the embedding for a given text input using OpenAI's API.

    Args:
        text (str): The input text to embed.
        openai_client (OpenAI): An instance of the OpenAI client.
        model (str): The model to use for embedding. Defaults to "text-embedding-3-small".

    Returns:
        np.ndarray: The embedding vector for the input text.
    """
    
    text = text.replace("\n", " ")
    return openai_client.embeddings.create(input = [text], model=model).data[0].embedding


def get_chatgpt_response(instruction: str, openai_client: OpenAI, temperature: float = 0.0)-> str:
    
    """
    Sends an instruction to the ChatGPT model and retrieves the response.

    Args:
        instruction (str): The instruction or question to send to ChatGPT.
        openai_client (OpenAI): An instance of the OpenAI client.
        temperature (float): Controls the randomness of the output. Lower values make the output more focused and deterministic. Defaults to 0.0.

    Returns:
        str: The response generated by the ChatGPT model.
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
    
    """
    Enum for defining various prompt templates used in the interaction with the chatbot.

    Attributes:
        answer_from_first_text (str): Template for answering questions based on retrieved text.
        answer_from_alternative_text (str): Placeholder for an alternative text response (currently empty).
        default_no_pinecone_text (str): Template for when the provided PDF is insufficient to answer the query.
        default_pinecone_text_irrelevant (str): Template for when no relevant answers are found in the retrieved text.
    """

    answer_from_first_text = """You are a helpful assistant. Below is information retrieved from relevant sources. Use this information to answer the following question as accurately as possible.

    Retrieved Document:
    {pinecone_text}

    Question: {query}

    Answer the question using only the information from the document. Explain your line of thought on why that answer is correct if and only if you find the answer.

    If the information is insufficient but contains some clues about completely answering the question, explain your reasoning but end with the following statement:
    The result is inconclusive.

    If the answer is not present at all, return an empty string. i.e. ''.
    """

    answer_from_alternative_text = """"""

    default_no_pinecone_text = """PDF provided is insufficient to answer your question: {query}.\nPinecone Text: {pinecone_text}""" #Equivalent to: Pinecone did not return any text or your text on pinecone contains empty strings
 
    default_pinecone_text_irrelevant = """I could not find any relevant answers to your query from the PDF provided.\nYour query:\n{query}"""
