# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 04:58:33 2024

@author: olanr
"""



from auxiliaries import Dict, List
import json
import os


    
def read_json(json_folder: str)-> Dict:
    json_file = os.listdir(json_folder)[0]
    
    json_filepath = os.path.join(json_folder, json_file)
    
    with open(json_filepath, "r") as file:
        json_data = json.load(file)
        
    return json_data



def create_request_number_to_chapter_map(json_file: Dict, )->Dict:
    request_number_to_chapter_map = {idx : chapter_name for idx, chapter_name in enumerate(json_file.keys())}
    return request_number_to_chapter_map



def create_chapter_with_number_to_text_map(json_file: Dict[str, List[str]]):
    if not json_file:
        print("No value in json file")
        return {}
    
    chapter_sections_to_text_map = {}
    for chapter_name in json_file.keys():
        chapter_sections = json_file[chapter_name]
        
        chapter_sections_to_text = {chapter_name + f"_{section_idx}": chapter_sections[section_idx] for section_idx in range(len(chapter_sections))}
        
        chapter_sections_to_text_map.update(chapter_sections_to_text)
        
    return chapter_sections_to_text_map



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


if __name__ == "__main__":
    input_request_folder = "input_batch"
    input_request_folder_path = os.path.join("..", input_request_folder)
    
    embeddings_folder = "output_embeddings"
    embedding_folder_path = os.path.join("..", embeddings_folder)
    
    json_folder = "book_in_json_step_1"
    json_path = os.path.join("..", json_folder)
    
    json_file = read_json(json_path)
    
    chapter_sections_to_text_map = create_chapter_with_number_to_text_map(json_file)
    
    request_number_to_chapter_map = create_request_number_to_chapter_map(chapter_sections_to_text_map)