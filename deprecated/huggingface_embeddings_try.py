# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 14:04:29 2024

@author: olanr
"""

import requests

API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
headers = {"Authorization": "Bearer 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"}

def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()


data = {
    "inputs": {
        "source_sentence": "This is a sample sentence to generate embeddings."
        }
}


embedding = query(data)
print(embedding)


output = query({
 	"inputs": {
 	"source_sentence": "Sales Representative",
 	"sentences": [
		"Marketer",
		"Market Researcher",
		"Influencer",
                "Waiter",
                "Customer care representative"
 	]
},
})