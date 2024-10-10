# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 21:27:09 2024

@author: olanr
"""


"""
The parse_jsonl.py module provides functionality to convert JSONL files into a Pandas DataFrame, enrich the DataFrame 
with additional metadata, and parse complex data structures. It is primarily used to prepare and manipulate data 
related to text embeddings extracted from documents, including references to chapters and their associated metadata. 

The module includes functions to handle reading JSONL files, extracting relevant information from reference objects, 
and organizing data into a structured format suitable for further analysis or storage.
"""



import fnmatch
import uuid

import pandas as pd

from auxiliaries import os, List, Tuple, Dict
from auxiliaries import read_json, Files



def convert_jsonl_files_to_dataframe(jsonl_file_folder: str)->pd.DataFrame:

    """
    Converts JSONL files in a folder to a Pandas DataFrame.

    Args:
        jsonl_file_folder (str): The folder containing the JSONL files.

    Returns:
        pd.DataFrame: A DataFrame containing the combined data from the JSONL files.
    """
    
    
    list_of_dataframes = []
    list_of_jsonl_files: List[str] = os.listdir(jsonl_file_folder)

    if not list_of_jsonl_files:
        print("Folder {jsonl_file_folder} is empty")
        return pd.DataFrame()

    for jsonl_file in list_of_jsonl_files:
        if not jsonl_file.endswith(".jsonl"):
            print(f"File {jsonl_file} within folder {jsonl_file_folder} not a .jsonl file. Skipping file...")

            continue
        
        jsonl_filepath = os.path.join(jsonl_file_folder, jsonl_file)

        try:
            df = pd.read_json(jsonl_filepath, lines = True)
        except ValueError as e:
            print(f"Failed to read file {jsonl_filepath}.\nPython error: {e}\nSkipping file...")

        if "response" in df.columns:
            df["text_embeddings"] = df["response"].apply(lambda row: row["body"]["data"][0]["embedding"])
        
        list_of_dataframes.append(df)

    final_df = pd.concat(list_of_dataframes)
    
    return final_df



def _get_json_reference_objects(reference_chapter_objects_folder: str)-> Tuple[Dict]:
    
    """
    Retrieves reference objects from JSON files containing chapter mappings.

    Args:
        reference_chapter_objects_folder (str): The folder containing reference JSON objects.

    Returns:
        Tuple[Dict]: A tuple containing:
            - Dict: A mapping of chapter sections to text.
            - Dict: A mapping of request numbers to chapter names.
    """
    
    request_number_fp = os.path.join("..", reference_chapter_objects_folder, Files.REQUEST_NUMBER_JSON.value)
    chapter_sections_fp = os.path.join("..", reference_chapter_objects_folder, Files.CHAPTER_SECTIONS_JSON.value)
    
    request_number_to_chapter_map: Dict = read_json(request_number_fp)
    chapter_sections_to_text_map: Dict = read_json(chapter_sections_fp)
    
    return chapter_sections_to_text_map, request_number_to_chapter_map



def parse_complex_dataframe(df: pd.DataFrame, pages_json_folder: str, reference_chapter_objects_folder: str)-> pd.DataFrame:
    
    """
    Enriches the DataFrame with chapter names, texts, and associated pages.

    Args:
        df (pd.DataFrame): The DataFrame containing embedding data.
        pages_json_folder (str): The folder containing JSON files mapping chapters to pages.
        reference_chapter_objects_folder (str): The folder containing reference JSON objects for chapters.

    Returns:
        pd.DataFrame: The enriched DataFrame with additional columns for chapter texts and pages.
    """
    
    #ESSENTIALLY CHUNKS = CHAPTERS
    
    chunks_to_text_map, request_number_to_chapter_map = _get_json_reference_objects(reference_chapter_objects_folder)
    
    
    df["request_nums"] = df["custom_id"].apply(lambda x: x.split("request-")[-1])
    #print(df["request_nums"].values)
    df["chunk_names"] = df["request_nums"].astype(str).apply(lambda x: request_number_to_chapter_map[str(x)])
    
    df["chapter_texts"] = df["chunk_names"].apply(lambda x: chunks_to_text_map[x])
    
    df["chapter_texts"] = df["chapter_texts"].apply(lambda text: ' '.join(part.strip().strip("'") for part in text.split("'") if part.strip()))
    
    #df["chunk_name"] = df["chapter_texts"].apply(lambda val: reverse_chunk_to_text_map[val])
    
    df["chunk_names"] = df["chunk_names"].str.rpartition("_")[0]
    
    pages_json_folderpath = os.path.join("..", pages_json_folder)
    pages_json_file = fnmatch.filter(os.listdir(pages_json_folderpath), "*_pages")
    
    if pages_json_file:
        
        pages_json_file = pages_json_file[0]
        pages_json_filepath = os.path.join(pages_json_folderpath, pages_json_file)
        
        chunk_to_pages_dict = read_json(pages_json_filepath)
        df["pages"] = df["chunk_names"].apply(lambda val: chunk_to_pages_dict[val])
    else:
        df["pages"] = "No pages detected"
        
    
    df["id"] = [str(uuid.uuid4()) for _ in range(len(df))]
        
    return df
