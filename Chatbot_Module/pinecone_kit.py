
"""
pinecone_kit.py

This module provides functions to interact with Pinecone, a vector database service, for managing and querying embeddings. It facilitates the creation of index clients, querying for results, and parsing the responses for further processing.

Usage:
    This module can be imported into other scripts to perform operations on Pinecone, such as retrieving data based on vector embeddings and handling results effectively.

Main Functions:
- get_pinecone_index_client: Retrieves the index client for a specified index name, handling cases where the index may not exist.
- get_pinecone_query_result: Queries the Pinecone index with dense and sparse vectors to retrieve relevant results based on the embeddings.
- parse_texts_from_pinecone: Extracts chapter texts and associated page numbers from the query results returned by Pinecone.

Constants:
- pinecone_connection: Establishes a connection to the Pinecone service using an API key.
- index_name: Stores the name of the Pinecone index to be used for queries.
"""



from pinecone import Pinecone, ServerlessSpec

from auxiliaries import List, Dict, Union, Tuple, os
from auxiliaries import load_dotenv
from pinecone import Pinecone
from pinecone.exceptions import NotFoundException



load_dotenv()


pinecone_key = os.getenv("PINECONE_KEY")
pinecone_connection = Pinecone(api_key=pinecone_key)

index_name = os.getenv("INDEX_NAME")


def get_pinecone_index_client(pinecone_client: Pinecone,
                              index_name: str
                              )-> Union[Pinecone.Index, None]:
    
    """
    Retrieves the Pinecone index client for a specified index name.

    Args:
        pinecone_client (Pinecone): The Pinecone client used to access the index.
        index_name (str): The name of the index to retrieve.

    Returns:
        Union[Pinecone.Index, None]: The index client if found; otherwise, None.
    
    Raises:
        NotFoundException: If the specified index does not exist.
    """

    try:
        index_client: Pinecone.Index = pinecone_client.Index(index_name)
    except NotFoundException:
        print(f"Could not find index with name {index_name}")
        print(f"List of indexes available: {pinecone_client.list_indexes().names()}")

    else:
        return index_client

def get_pinecone_query_result(pinecone_index_client: pinecone_connection.Index, 
                              hdense: List[float], 
                              hsparse: Dict[str, List], 
                              num_results: int = 3
                              )-> Dict:
    
    """
    Queries the Pinecone index using dense and sparse vectors to retrieve results.

    Args:
        pinecone_index_client (pinecone_connection.Index): The Pinecone index client to query.
        hdense (List[float]): The dense vector representation of the query.
        hsparse (Dict[str, List]): The sparse vector representation of the query.
        num_results (int, optional): The number of top results to return. Defaults to 3.

    Returns:
        Dict: The query results as a dictionary, including metadata and matches.
    """
    
    if hsparse["values"]:
        query_result = pinecone_index_client.query(
        namespace= "sisikepo",
        vector= hdense,
        sparse_vector= hsparse,
        top_k= num_results,
        include_metadata = True
        )
        
    else:
        query_result = pinecone_index_client.query(
        namespace= "sisikepo",
        vector= hdense,
        top_k= num_results,
        include_metadata = True
        )
        
    return query_result.to_dict()



def parse_texts_from_pinecone(query_result: Dict)-> Tuple[List]:
    
    """
    Extracts chapter texts and associated page numbers from the query results.

    Args:
        query_result (Dict): The results returned from a Pinecone query.

    Returns:
        Tuple[List]: A tuple containing two lists: chapter texts and page references.
    """
    
    pinecone_texts = []
    text_pages = []
    if query_result["matches"]:
        for result_index in range(len(query_result)):
            text = query_result["matches"][result_index]["metadata"]["chapter_texts"]
            page_number = query_result["matches"][result_index]["metadata"]["page_number"]
            text_pages.append(f"Reference: Babok, page {int(page_number)}")
            pinecone_texts.append(text)
      
    return pinecone_texts, text_pages
