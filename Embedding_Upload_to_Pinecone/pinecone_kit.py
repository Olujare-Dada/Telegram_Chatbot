"""
The pinecone_kit.py module provides an interface to interact with the Pinecone vector database. 
It includes functions to query the database and extract relevant text information based on input vectors. 
The module handles API key loading and initializes the Pinecone client connection.
"""



from pinecone import Pinecone, ServerlessSpec

from auxiliaries import List, Dict
from auxiliaries import load_dotenv
import os


load_dotenv()


pinecone_key = os.getenv("PINECONE_KEY")
pinecone_connection = Pinecone(api_key=pinecone_key)

index_name = os.getenv("INDEX_NAME")



def get_pinecone_query_result(pinecone_index_client: pinecone_connection.Index, 
                              hdense: List[float], 
                              hsparse: Dict[str, List], 
                              num_results: int = 3
                              )-> Dict:
    
    """
    Queries the Pinecone index with a dense and sparse vector and retrieves results.

    Args:
        pinecone_index_client (pinecone_connection.Index): The Pinecone index client to query.
        hdense (List[float]): The dense vector to use in the query.
        hsparse (Dict[str, List]): The sparse vector representation.
        num_results (int): The number of top results to retrieve (default is 3).

    Returns:
        Dict: The query results as a dictionary.
    """
    
    query_result = pinecone_index_client.query(
        vector= hdense,
        sparse_vector= hsparse,
        top_k= num_results,
        include_metadata = True
        )
    return query_result.to_dict()



def parse_texts_from_pinecone(query_result: Dict)-> List:
    
    """
    Extracts chapter texts from the query results returned by Pinecone.

    Args:
        query_result (Dict): The result of the Pinecone query.

    Returns:
        List: A list of chapter texts extracted from the query results.
    """
    
    pinecone_texts = []
    if query_result["matches"]:
        for result_index in range(len(query_result)):
            text = query_result["matches"][result_index]["metadata"]["chapter_texts"]
            pinecone_texts.append(text)
    
    return pinecone_texts
