# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 05:40:36 2024

@author: olanr
"""

"""
1. Receive query as text
2. Send query to OpenAI to convert to embeddings
3. Send embeddings as query to Pinecone DB
4. Extract chapter_text and chapter_names metadata from pinecone response
5. Extract the best responses via outlier or mean
6. Send the initial query and extracted text to OpenAI. If there are more than 1 good text from Pinecone,
send text, one after the other to get response from OpenAI 
6. Feed the response(s) to telegram

"""

from pinecone_kit import pinecone_connection as pc
from pinecone_kit import index_name, Pinecone
from pinecone_kit import get_pinecone_index_client
from embedding_matrix_loader import load_vectorizer, TfidfVectorizer
from embedding_matrix_loader import VECTORIZER_PKL, VECTORIZER_FOLDER
from openai_kit import openai_client
from query_processor import process_query
from test_queries import SampleQueries




"=================================RUN============================================="


def get_chatbot_response(query: str)-> str:
    vectorizer: TfidfVectorizer = load_vectorizer(VECTORIZER_FOLDER, VECTORIZER_PKL)
    pinecone_index_client: Pinecone.Index = get_pinecone_index_client(pc, index_name)
    answer: str = process_query(query, pinecone_index_client,openai_client, vectorizer)
    print(answer)
    return answer

if __name__ == "__main__":
    query = SampleQueries.query1.value
    answer: str = get_chatbot_response("Hello")
    









"""
1. send query
2. convert query to embedding
3. query the pineconedb and get result
4. parse result and send to gpt
5. If empyt string is returned, send next result to gpt (X3)
6. If empty string still, change alpha to 0.5 (X3), then change to 0.0
7. If empty string still, return a default message
8. Integrate with bot father
"""

