# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 21:30:18 2024

@author: olanr
"""


"""
The pinecone_operations.py module provides functionalities for managing and interacting with Pinecone's vector 
database, specifically focused on preparing data for insertion, batch processing, and creating an index if it does not 
already exist. 

It utilizes TF-IDF vectorization to transform text data into vectors suitable for insertion into Pinecone.
"""



import pandas as pd

from auxiliaries import List, Union, Generator, json
from vectorizer_kit import TfidfVectorizer, csr_matrix
from vectorizer_kit import SparseMatrixOperations as smo
from pinecone_kit import pinecone_connection as pc
from pinecone_kit import ServerlessSpec





DEFAULT_EMBEDDING_DIMENSION = 1536


class PineconeOperations:
    
    """
    A class to manage operations related to Pinecone, including data preparation,
    writing to the index, and index management.
    """
    
    def __init__(self, pinecone_client: pc, index_name: str):
        
        """
        Initializes the PineconeOperations instance.

        Args:
            pinecone_client (pc): The Pinecone client instance.
            index_name (str): The name of the Pinecone index to use.
        """
        
        self.pinecone_client = pinecone_client
        self.index_name = index_name
        pinecone_index_client: pc.Index = self.pinecone_client.Index(self.index_name)
    
    
    
    def create_pinecone_input(self, df: pd.DataFrame, vectorizer: TfidfVectorizer)-> List:
        
        """
        Prepares the input data for Pinecone by transforming chapter texts into vectors.

        Args:
            df (pd.DataFrame): The DataFrame containing chapter texts and metadata.
            vectorizer (TfidfVectorizer): The vectorizer used to convert texts to vectors.

        Returns:
            List: A list of dictionaries containing vectors and their associated metadata.
        """
        
        vectors_with_metadata = []
        for _, row in df.iterrows():
            chapter_text = row["chapter_texts"]
        
            sparse_matrix: csr_matrix = vectorizer.transform([chapter_text])
    
            sparse_values = smo.csr_matrix_to_sparse_dict(sparse_matrix)
            
            entry = {
                "id": row['id'],
                "sparse_values": sparse_values,
                "values": row['text_embeddings'],
                
                "metadata": {
                    "chapter_names": row['chunk_names'],
                    "chapter_texts": row['chapter_texts'],
                    "page_number": row["pages"]
                }
            }
            vectors_with_metadata.append(entry)
        return vectors_with_metadata




    def batch_pinecone_input_generator(self, pinecone_input: List, pinecone_data_limit: float = 4 * 1e6):
        
        """
        A generator that yields batches of Pinecone input data based on size limits.

        Args:
            pinecone_input (List): The list of input data for Pinecone.
            pinecone_data_limit (float): The maximum size for each batch (default is 4MB).

        Yields:
            List: A batch of Pinecone input data.
        """
        
        batch_size = 0
        batch_entries = []
        for entry in pinecone_input:
            serialized_entry = json.dumps(entry)
            entry_size = len(serialized_entry.encode("utf-8"))
            
            if batch_size + entry_size > pinecone_data_limit:
                yield batch_entries
                batch_entries = []
                batch_size = 0
            
            batch_entries.append(entry)
            batch_size += entry_size
        
        if batch_entries:
            yield batch_entries
    
    
        
    
    def write_to_pinecone_in_batches(self,
                                     pinecone_inputs_generator: Generator[List, List, str],
                                     namespace: Union[str, None] = None
                                     )-> None:
        
        """
        Writes data to Pinecone in batches.

        Args:
            pinecone_inputs_generator (Generator[List, List, str]): The generator yielding batches of input data.
            namespace (Union[str, None]): The namespace to use for the upsert operation (default is None).

        Returns:
            None
        """
        
        for idx, pinecone_input in enumerate(pinecone_inputs_generator):
            if namespace:
                self.pinecone_index_client.upsert(vectors = pinecone_input, namespace = namespace)
                print(f"{len(pinecone_input)} rows of data written successfully to Index: {self.pinecone_index_client} and Namespace: {namespace}")
            else:
                self.pinecone_index_client.upsert(vectors = pinecone_input)
                print(f"{len(pinecone_input)} rows of data written successfully to Index: {self.pinecone_index_client}")
    
                
    
    def create_index_if_not_exists(self, embedding_dimension = DEFAULT_EMBEDDING_DIMENSION)-> None:
        
        """
        Creates a Pinecone index if it does not already exist.

        Args:
            embedding_dimension (int): The dimension of the embeddings (default is 1536).

        Returns:
            None
        """
        
        if not self.index_name in pc.list_indexes().names():
            self.pinecone_client.create_index(
                name= self.index_name,
                dimension=embedding_dimension, # Replace with your model dimensions
                metric="dotproduct", # Replace with your model metric
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                ) 
            )
            
            if self.index_name in self.pinecone_client.list_indexes().names():
                print(f"Index {self.index_name} created")
        else:
            print(f"{self.index_name} index already exists")
        
