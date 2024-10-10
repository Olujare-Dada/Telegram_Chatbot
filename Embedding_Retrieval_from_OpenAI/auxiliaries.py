# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 03:19:31 2024

@author: olanr
"""


"""
auxiliaries.py

This module provides utility functions for file handling and JSON operations, including creating directories and reading/writing JSON files.

Functions:
    - make_directory: Creates a directory if it does not already exist.
    - read_json: Reads the first JSON file from a specified folder and returns its contents as a dictionary.
    - write_dict_to_json: Writes a given dictionary to a specified JSON file in a designated folder.

Usage:
    Import the module and call the functions as needed for file and JSON operations.
"""

import os
from typing import Dict, List, Tuple, Union, Any, Optional
from dotenv import load_dotenv
import json



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
    Reads the first JSON file from a specified folder and returns its contents as a dictionary.

    Args:
        json_folder (str): The path to the folder containing the JSON file.

    Returns:
        Dict: The contents of the JSON file as a dictionary.
    """
    
    json_file = os.listdir(json_folder)[0]
    
    json_filepath = os.path.join(json_folder, json_file)
    
    with open(json_filepath, "r") as file:
        json_data = json.load(file)
        
    return json_data



def write_dict_to_json(dictionary: dict, folder_path: str, filename: str) -> None:
    """
    Writes a dictionary to a JSON file.
    
    Args:
        dictionary (dict): The dictionary to write to the JSON file.
        folder_path (str): The folder path where the JSON file will be saved.
        filename (str): The name of the JSON file.
    """
    
    file_path = os.path.join(folder_path, filename)
    
    try:
        with open(file_path, 'w') as json_file:
            json.dump(dictionary, json_file, indent=4)
        print(f"Dictionary successfully written to {file_path}")
    except Exception as e:
        print(f"An error occurred while writing to {file_path}: {e}")
