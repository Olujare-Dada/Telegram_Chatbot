
"""
query_processor.py

This module processes user queries by interacting with the OpenAI API and Pinecone embedding service. It takes user input, converts it into vector representations, queries Pinecone for relevant text, and generates a response using GPT-4. The module handles different alpha scaling values to balance between dense and sparse vectors in query processing.

Usage:
    This module can be imported into other scripts to leverage its query processing capabilities for a chatbot, integrating both OpenAI responses and context from Pinecone.

Main Functions:
- get_gpt_response_from_pinecone_text: Generates a response from GPT-4 based on a single piece of text retrieved from Pinecone and the user's query.
- get_gpt_response_from_pinecone_texts: Processes multiple texts from Pinecone, generating responses and appending page information when relevant.
- process_query: Takes a user query, retrieves relevant texts from Pinecone, and generates an appropriate response using OpenAI's API.

"""


from enum import Enum
from auxiliaries import List, Dict
from openai_kit import (OpenAI, 
                        PromptTemplate, 
                        get_chatgpt_response
                        )

from pinecone_kit import (get_pinecone_query_result, 
                          parse_texts_from_pinecone
                          )

from embedding_matrix_loader import (TfidfVectorizer,
                                     convert_string_query_to_vectors,
                                     hybrid_scale
                                     )



class AlphaValues(Enum):
   HIGH = 1.0
   MEDIUM = 0.5
   LOW = 0.0


def get_gpt_response_from_pinecone_text(pinecone_text: str, query: str, openai_client: OpenAI)-> str:
    
    """
    Generates a response from GPT-4 based on a single piece of text retrieved from Pinecone and the user's query.

    Args:
        pinecone_text (str): The text retrieved from Pinecone.
        query (str): The user's query to be answered.
        openai_client (OpenAI): An instance of the OpenAI client to interact with the API.

    Returns:
        str: The generated response from GPT-4.
    """
    
    if pinecone_text:
        instruction = PromptTemplate.answer_from_first_text.value.format(pinecone_text = pinecone_text, query = query)
        gpt_response = get_chatgpt_response(instruction, openai_client)
    else:
        gpt_response = PromptTemplate.default_no_pinecone_text.value.format(query = query)

    return gpt_response


def get_gpt_response_from_pinecone_texts(pinecone_texts: List,
                                         text_pages: List,
                                         query: str,
                                         openai_client: OpenAI
                                         )-> str:
    
    """
    Processes multiple texts from Pinecone, generating responses and appending page information when relevant.

    Args:
        pinecone_texts (List): A list of texts retrieved from Pinecone.
        text_pages (List): A list of page numbers corresponding to the texts.
        query (str): The user's query to be answered.
        openai_client (OpenAI): An instance of the OpenAI client to interact with the API.

    Returns:
        str: The generated response, or an indication that no relevant answer was found.
    """
    
    if not pinecone_texts:
        return ""
    
    for idx, (pinecone_text, text_page) in enumerate(zip(pinecone_texts, text_pages)):
        
        #print(f"Going through pinecone text {idx + 1}")
        gpt_response = get_gpt_response_from_pinecone_text(pinecone_text, query, openai_client)
        
        #print(f"{gpt_response = }")
        if gpt_response not in ['',"'", '"', "", "''", '""'] and gpt_response != PromptTemplate.default_no_pinecone_text.value.format(query = query, pinecone_text = pinecone_text):
            gpt_response += f"\n\n{text_page}"
            return gpt_response
      
    if gpt_response in ['',"'", '"', "", "''", '""']:
        gpt_response = PromptTemplate.default_pinecone_text_irrelevant.value.format(query = query)
        return gpt_response

    else:
        raise ValueError(f"Unexpected behavior detected in function: {get_gpt_response_from_pinecone_texts.__name__}()")




def process_query(query: str,
                  pinecone_index_client,
                  openai_client: OpenAI,
                  vectorizer: TfidfVectorizer,
                  )-> str:
    
    """
    Takes a user query, retrieves relevant texts from Pinecone, and generates an appropriate response using OpenAI's API.

    Args:
        query (str): The user's query.
        pinecone_index_client: The Pinecone index client to perform queries.
        openai_client (OpenAI): An instance of the OpenAI client to interact with the API.
        vectorizer (TfidfVectorizer): The vectorizer used to transform the query into vector representations.

    Returns:
        str: The generated response based on the user's query and relevant texts from Pinecone.
    """
    
    search_query_dense_sparse: Dict = convert_string_query_to_vectors(query, openai_client, vectorizer)
    #print(f"{search_query_dense_sparse = }")

    possible_alpha_values: List[float] = [AlphaValues.HIGH.value,
                                         AlphaValues.MEDIUM.value,
                                         AlphaValues.LOW.value
                                         ]
   
    for alpha_value in possible_alpha_values:
        
        print(f"{alpha_value = }")
        hdense, hsparse = hybrid_scale(search_query_dense_sparse.get("dense"),
                                     search_query_dense_sparse.get("sparse"),
                                     alpha = alpha_value
                                     )
        #print(f"{len(hdense) = }\n{len(hsparse) = }")
      
        query_result: Dict = get_pinecone_query_result(pinecone_index_client, hdense, hsparse)
        #print(f"{query_result = }")

        pinecone_texts: List
        text_pages: List
        pinecone_texts, text_pages = parse_texts_from_pinecone(query_result)
        #print(f"{pinecone_texts = }")

        answer: str = get_gpt_response_from_pinecone_texts(pinecone_texts, text_pages, query, openai_client)
        #print(f"{answer = }")

        if answer in ['', "", "''", '""'] or answer == PromptTemplate.default_pinecone_text_irrelevant.value.format(query = query):
            continue

        else:
            return answer

    if answer in ['', "", "''", '""'] or answer == PromptTemplate.default_pinecone_text_irrelevant.value.format(query = query):
        return PromptTemplate.default_pinecone_text_irrelevant.value.format(query = query)

    else:
        raise ValueError(f"Answer returned an unknown value.\n{answer = }")
