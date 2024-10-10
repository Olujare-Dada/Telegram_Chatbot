# -*- coding: utf-8 -*-
"""
Created on Wed Sep 25 04:10:45 2024

@author: olanr
"""


"""
get_embeddings.py

This module orchestrates the process of retrieving embeddings from OpenAI's API. It reads input JSON files, prepares requests, sends them to OpenAI, and retrieves the output embeddings. It utilizes the PrepareInputJsonl and MonitorAndRetrieveEmbeddings classes to handle the various steps of this workflow.

Usage:
    This script should be run as the main program. It sets up the paths for input and output directories, processes the input files, and retrieves embeddings.

Main Steps:
    1. Read JSON input files containing chapter data.
    2. Prepare request objects for the OpenAI API.
    3. Send requests to OpenAI and monitor their progress.
    4. Write the retrieved embeddings to output files.
"""



from auxiliaries import os, Dict, List
from auxiliaries import read_json, write_dict_to_json
from openai_kit import openai_client
from prepare_input import PrepareInputJsonl
from retrieve_embeddings import MonitorAndRetrieveEmbeddings


# Initialize classes for preparing input and monitoring embeddings retrieval
pij = PrepareInputJsonl(openai_client)
mre = MonitorAndRetrieveEmbeddings(openai_client)


# > Input_Jsonl -> OpenAI for Embeddings -> Output_Jsonl in output_embedding folder
if __name__ == "__main__":
    
    """
    Main execution block that orchestrates the embedding retrieval process.

    Steps:
        - Define paths for input and output folders.
        - Read JSON data from the specified path.
        - Create mappings for chapter sections and requests.
        - Prepare request objects for the OpenAI API.
        - Create input files for the OpenAI API.
        - Initialize jobs for processing embeddings.
        - Monitor job statuses and retrieve output file IDs.
        - Write retrieved embeddings to output files.
    """
    
    input_request_folder = "input_batch_step_2"
    input_request_folder_path: os.PathLike = os.path.join("..", input_request_folder)
    
    embeddings_folder = "output_embeddings_step_3"
    embedding_folder_path: os.PathLike = os.path.join("..", embeddings_folder)
    
    json_folder = "book_in_json_step_1"
    json_path: os.PathLike = os.path.join("..", json_folder)
    
    reference_objects_folder = "chapter_reference_objects_step_2"
    reference_objects_path: os.PathLike = os.path.join("..", reference_objects_folder)
    reference_objects_filenames = "chapter_sections_to_text.json", "request_number_to_chapter_map.json"
    
    # Read input JSON data
    json_file: Dict = read_json(json_path)
    
    # Create mappings and write them to reference files
    chapter_sections_to_text_map: Dict = pij.create_chapter_with_number_to_text_map(json_file)# e.g. "chunk_0_0": "A Guide to the..."
    write_dict_to_json(chapter_sections_to_text_map, reference_objects_path, reference_objects_filenames[0])
    
    request_number_to_chapter_map: Dict = pij.create_request_number_to_chapter_map(chapter_sections_to_text_map)# e.g. 0: "chunk_0_0", 1: "chunk_1_0"...
    write_dict_to_json(request_number_to_chapter_map, reference_objects_path, reference_objects_filenames[1])
    
    
    # Create request objects and input files
    pij.create_request_objects(request_number_to_chapter_map, chapter_sections_to_text_map, input_request_folder_path)
    input_file_ids: List = pij.create_input_files(request_folder = input_request_folder_path)
    
    # Initialize jobs for embedding processing
    job_ids: List = pij.initialize_jobs(input_file_ids = input_file_ids)
    
    # Monitor jobs and retrieve output file IDs
    output_file_ids: List = mre.run_async(mre.monitor_multiple_jobs, job_ids)
    
    #output_file_ids = asyncio.run(monitor_multiple_jobs(client, job_ids))  # Get the output file IDs
    
    
    print(f"Retrieved Ouptut File IDs:\n{output_file_ids}")
    
    # Write embeddings to files
    mre.write_enbeddings_to_file(output_file_ids = output_file_ids, output_folder = embedding_folder_path)
    
