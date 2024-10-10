# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 21:13:08 2024

@author: olanr
"""

import pandas as pd
import pickle
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer


class SparseMatrixOperations:
    
    """
    Class for performing operations related to sparse matrices 
    and TF-IDF vectorization on text data.
    """
    
    def create_sparse_input(df: pd.DataFrame):
        
        """
        Creates a sparse matrix from the text data using TF-IDF vectorization.

        Args:
            df (pd.DataFrame): DataFrame containing the text data with a "chapter_texts" column.

        Returns:
            Tuple[csr_matrix, TfidfVectorizer]: The sparse matrix and the fitted vectorizer.
        """
        
        # Initialize the TF-IDF Vectorizer
        vectorizer = TfidfVectorizer()
    
        # Fit the vectorizer on the text data and transform into a sparse matrix
        sparse_matrix = vectorizer.fit_transform(df["chapter_texts"])
    
        return sparse_matrix, vectorizer  # Return the sparse matrix and the vectorizer (optional)
    
    
    def save_vectorizer(vectorizer: TfidfVectorizer, vectorizer_folder: str):
        
        """
        Saves the TF-IDF vectorizer to a specified folder.

        Args:
            vectorizer (TfidfVectorizer): The vectorizer to save.
            vectorizer_folder (str): Folder where the vectorizer will be saved.
        """
        
        with open(f"{vectorizer_folder}/tfidf_vectorizer.pkl", "wb") as f:
            pickle.dump(vectorizer, f)
    
        print(f"Vectorizer saved in {vectorizer_folder}")


    def csr_matrix_to_sparse_dict(sparse_matrix):
        
        """
        Converts a CSR matrix to a dictionary with indices and values.

        Args:
            sparse_matrix (csr_matrix): The sparse matrix to convert.

        Returns:
            Dict[str, List]: A dictionary containing 'indices' and 'values' lists.
        """
        
        """Convert a CSR matrix to a dictionary with indices and values."""
        coo_matrix = sparse_matrix.tocoo()  # Convert to COO format for easier indexing
        return {
            "indices": coo_matrix.col.tolist(),
            "values": coo_matrix.data.tolist()
        }
