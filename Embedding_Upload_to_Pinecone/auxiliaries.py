# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 11:12:27 2024

@author: olanr
"""


from typing import List, Dict, Tuple, Union, Optional, Generator
from dotenv import load_dotenv
import json
import os
from enum import Enum


class Folders(Enum):
    
    """
    Enum class for standard folder paths used in the package.
    """
    
    EMBEDDINGS = "output_embeddings_step_3"
    VECTORIZER = "vectorizer"
    BOOK_JSON = "book_in_json_step_1"
    REFERENCE_JSON_OBJECTS = "chapter_reference_objects_step_2"
    


class Files(Enum):
    
    """
    Enum class for standard file names used in the package.
    """
    
    REQUEST_NUMBER_JSON = "request_number_to_chapter_map.json"
    CHAPTER_SECTIONS_JSON = "chapter_sections_to_text.json"


def make_directory(directory_name: str) -> str:
    """
    Creates a directory with the given name. If the directory already exists, no action is taken.
    
    Args:
        directory_name (str): Name of the directory to create.

    Returns:
        str: The name of the directory (created or already existing).
    """
    try:
        os.mkdir(directory_name)
        print(f"{directory_name} folder created")
    except FileExistsError:
        print(f"{directory_name} already exists. No creation needed")
    
    return directory_name



def read_json(json_folder: str)-> Dict:
    
    """
    Reads a JSON file from the specified folder or file path.

    Args:
        json_folder (str): Path to the folder or file containing JSON data.

    Returns:
        Dict: The JSON data loaded as a dictionary.

    Raises:
        ValueError: If the provided path is neither a folder nor a file.
    """
    
    if os.path.isdir(json_folder):
        json_file = os.listdir(json_folder)[0]
        json_filepath = os.path.join(json_folder, json_file)
    elif os.path.isfile(json_folder):
        json_filepath = json_folder
        
    else:
        raise ValueError(f"Folderpath inputted {json_folder} is neither a folderpath nor a filepath")
    
    with open(json_filepath, "r") as file:
        json_data = json.load(file)
        
    return json_data
