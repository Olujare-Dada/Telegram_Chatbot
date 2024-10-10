# -*- coding: utf-8 -*-
"""
Created on Tue Sep 24 23:57:02 2024

@author: olanr
"""



"""
upload_to_pinecone.py

This module orchestrates the process of uploading chapter embeddings to Pinecone. It reads embeddings from JSONL files, transforms them into a suitable format, and uploads them to the Pinecone vector database. The module utilizes various utility functions for data processing and the PineconeOperations class to handle the interaction with Pinecone.

Usage:
    This script should be run as the main program. It sets up the necessary paths for directories, processes the embedding data, and performs the upload to Pinecone.

Main Steps:
    1. Create directories for storing the vectorizer and embeddings.
    2. Load embeddings from JSONL files into a DataFrame.
    3. Parse the DataFrame to associate chapter texts and metadata.
    4. Create a TF-IDF vectorizer and transform the text data into a sparse matrix.
    5. Save the vectorizer for future use.
    6. Prepare the input data for Pinecone.
    7. Create a Pinecone index if it does not already exist.
    8. Upload the embeddings to Pinecone in batches.
"""



import pandas as pd


from auxiliaries import List, os, Dict
from auxiliaries import load_dotenv, make_directory, Folders

from vectorizer_kit import TfidfVectorizer, csr_matrix
from vectorizer_kit import SparseMatrixOperations as smo

from pinecone_kit import index_name
from pinecone_kit import pinecone_connection as pc

from parse_jsonl import convert_jsonl_files_to_dataframe, parse_complex_dataframe

from pinecone_operations import PineconeOperations




load_dotenv()



    

if __name__ == "__main__":
    
    """
    Main script to convert chapter embeddings from JSONL files to a Pinecone index.
    
    The script performs the following steps:
    1. Sets up directories for the vectorizer and embeddings.
    2. Loads embeddings from JSONL files into a DataFrame.
    3. Parses the embeddings DataFrame to associate chapter texts and metadata.
    4. Creates a TF-IDF vectorizer and transforms the text data into a sparse matrix.
    5. Saves the vectorizer for future use.
    6. Prepares the Pinecone input data.
    7. Creates a Pinecone index if it does not exist.
    8. Writes the embeddings to Pinecone in batches.
    """
    
    vectorizer_folderpath: os.PathLike = os.path.join("..", Folders.VECTORIZER.value)
    make_directory(vectorizer_folderpath)
    
    embeddings_folderpath: os.PathLike = os.path.join("..", Folders.EMBEDDINGS.value)
    embeddings_df: pd.DataFrame = convert_jsonl_files_to_dataframe(embeddings_folderpath)
    
    chapter_embeddings_df: pd.DataFrame = parse_complex_dataframe(embeddings_df, 
                                                                  Folders.BOOK_JSON.value, 
                                                                  Folders.REFERENCE_JSON_OBJECTS.value
                                                                  )
    
    vectorizer: TfidfVectorizer
    sparse_matrix: csr_matrix
    sparse_matrix, vectorizer = smo.create_sparse_input(chapter_embeddings_df)

    smo.save_vectorizer(vectorizer, vectorizer_folderpath)
    
    
    po = PineconeOperations(pc, index_name)

    pinecone_input: List[Dict] = po.create_pinecone_input(chapter_embeddings_df, vectorizer)
    
    embedding_dimension: int = len(embeddings_df.text_embeddings.head(1).values[0])
    
    embeddings = embeddings_df["text_embeddings"]
    
    po.create_index_if_not_exists()
    
    po.write_to_pinecone_in_batches(po.batch_pinecone_input_generator(pinecone_input), "sisikepo")

