# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 08:16:28 2024

@author: olanr
"""

import os
from typing import Dict, Union
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


def convert_final_map_to_json(final_map: Dict, 
                              pdf_name: str, 
                              json_folder: str, 
                              )->None:
    
    """
    Converts a final mapping (dictionary) to a JSON file and saves it in the specified folder.

    Args:
        final_map (Dict): The mapping data to convert to JSON.
        pdf_name (str): The name of the PDF file, used to create the JSON filename.
        json_folder (str): The folder where the JSON file will be saved.

    Returns:
        None
    """
    
    pdf_name = pdf_name.split(".")[0]
        
    file_path = os.path.join(json_folder, pdf_name)
    
    with open(file_path, "w") as json_file:
        json.dump(final_map, json_file, indent = 4)
        
    print(f"JSON file saved to {file_path}")
    

def convert_pages_map_to_json(final_map: Dict, 
                              pdf_name: str, 
                              json_folder: str, 
                              )->None:
    
    """
    Converts a mapping of pages (dictionary) to a JSON file and saves it in the specified folder.

    Args:
        final_map (Dict): The mapping data of pages to convert to JSON.
        pdf_name (str): The name of the PDF file, used to create the JSON filename.
        json_folder (str): The folder where the JSON file will be saved.

    Returns:
        None
    """
    
    pdf_name = pdf_name.split(".")[0] + "_pages"
        
    file_path = os.path.join(json_folder, pdf_name)
    
    with open(file_path, "w") as json_file:
        json.dump(final_map, json_file, indent = 4)
        
    print(f"JSON file saved to {file_path}")
    
    

def read_json(json_folder: str)-> Dict:
    
    """
    Reads the first JSON file in the specified folder and returns its contents as a dictionary.

    Args:
        json_folder (str): The folder containing the JSON file.

    Returns:
        Dict: The contents of the JSON file as a dictionary.
    
    Raises:
        FileNotFoundError: If the folder is empty or does not contain a JSON file.
    """
    
    json_file = os.listdir(json_folder)[0]
    
    json_filepath = os.path.join(json_folder, json_file)
    
    with open(json_filepath, "r") as file:
        json_data = json.load(file)
        
    return json_data
