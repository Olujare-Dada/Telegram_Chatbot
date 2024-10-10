
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



from auxiliaries import Dict, Any, Union, List, Tuple, os
import numpy as np
from openai_kit import OpenAI
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix



VECTORIZER_PKL = "tfidf_vectorizer.pkl"
VECTORIZER_FOLDER = "vectorizer"

def load_vectorizer(vectorizer_folder: str, vectorizer_pkl:str)-> TfidfVectorizer:
    
    """
    Loads a TF-IDF vectorizer from a specified folder.

    Args:
        vectorizer_folder (str): The folder containing the vectorizer pickle file.
        vectorizer_pkl (str): The name of the pickle file.

    Returns:
        TfidfVectorizer: The loaded TF-IDF vectorizer.
    """
    
    vectorizer_path = os.path.join("..", vectorizer_folder, vectorizer_pkl)
    with open(vectorizer_path, "rb") as f:
        loaded_vectorizer = pickle.load(f)
        
    print("Vectorizer loaded successfully")
    
    return loaded_vectorizer



def convert_string_query_to_vectors(query: str,
                                    openai_client: OpenAI,
                                    vectorizer: TfidfVectorizer,
                                    openai_model: str = "text-embedding-3-small",
            
                                    ) -> Dict[str, Union[np.ndarray, csr_matrix ]]:
    
    """
    Converts a string query into dense and sparse vector representations.

    Args:
        query (str): The input query string to convert.
        openai_client (OpenAI): An instance of the OpenAI client.
        vectorizer (TfidfVectorizer): The TF-IDF vectorizer to transform the query.
        openai_model (str): The model to use for generating the dense vector. Defaults to "text-embedding-3-small".

    Returns:
        Dict[str, Union[np.ndarray, csr_matrix]]: A dictionary containing the dense and sparse vector representations.
    """
    
    dense_vector: np.ndarray = openai_client.embeddings.create(input = [query],
                                                               model = openai_model,
                                                               ).data[0].embedding

    sparse_vector: csr_matrix = vectorizer.transform([query])

    return {
        "dense": dense_vector,
        "sparse": sparse_vector
        }


def sparse_matrix_to_dict(sparse_matrix: csr_matrix)-> Dict[str, List]:
    
    """
    Converts a sparse matrix into a dictionary containing indices and values.

    Args:
        sparse_matrix (csr_matrix): The sparse matrix to convert.

    Returns:
        Dict[str, List]: A dictionary with 'indices' and 'values' extracted from the sparse matrix.
    """
    
    coo = sparse_matrix.tocoo()  # Convert sparse matrix to COO format (Coordinate list)
    indices = np.vstack((coo.row, coo.col)).T  # Stack row and column indices
    values = coo.data.tolist()  # Extract the non-zero values

    flat_indices = indices[:, 1].astype(int).tolist()
    return {
        "indices": flat_indices,  # Convert to list for compatibility
        "values": values
    }


def hybrid_scale(dense: np.ndarray,
                 sparse_matrix: csr_matrix,
                 alpha: float
                 )-> Tuple[List[float], Dict[str, List]]:
    
   """
    Scales dense and sparse vectors using a convex combination.

    Args:
        dense (np.ndarray): Array of floats representing vector embeddings.
        sparse_matrix (csr_matrix): Sparse matrix to be scaled.
        alpha (float): A float between 0 and 1, where 0 corresponds to sparse only and 1 to dense only.

    Returns:
        Tuple[List[float], Dict[str, List]]: A tuple containing the scaled dense vector and the scaled sparse vector as a dictionary.
    
    Raises:
        ValueError: If alpha is not between 0 and 1.
    """

   if alpha < 0 or alpha > 1:
      raise ValueError("Alpha must be between 0 and 1")

   sparse = sparse_matrix_to_dict(sparse_matrix)
   
   hsparse = {
      "indices" : sparse["indices"],
      "values": [v * (1 - alpha) for v in sparse["values"]]
      }

   hdense = [v * alpha for v in dense]

   return hdense, hsparse

