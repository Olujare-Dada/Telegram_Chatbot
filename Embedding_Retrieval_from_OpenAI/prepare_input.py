# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 03:13:31 2024

@author: olanr
"""


"""
prepare_input.py

This module prepares input data for OpenAI's embeddings API by creating request objects from chapter data and managing the submission of these requests.

Classes:
    - PrepareInputJsonl: A class to prepare and manage JSONL input for OpenAI's embeddings API.

Usage:
    Create an instance of `PrepareInputJsonl` with an OpenAI client, then use its methods to create request maps, generate JSONL files, and initialize jobs for processing embeddings.
"""


from auxiliaries import Dict, Any, List, json
import os

from auxiliaries import make_directory
from openai_kit import OpenAI, APIConnectionError, RateLimitError


class PrepareInputJsonl:
    
    """
    A class to prepare and manage JSONL input for OpenAI's embeddings API.

    Attributes:
        openai_client (OpenAI): The OpenAI client instance for making requests.
    """
    
    
    
    def __init__(self, openai_client: OpenAI):
        
        """
        Initializes the PrepareInputJsonl instance with the OpenAI client.

        Args:
            openai_client (OpenAI): The OpenAI client instance for making requests.
        """
        
        self.openai_client = openai_client
        
    
    @staticmethod    
    def create_request_number_to_chapter_map(json_file: Dict, )->Dict:
        
        """
        Creates a mapping of request numbers to chapter names from the provided JSON file.

        Args:
            json_file (Dict): A dictionary containing chapter names as keys.

        Returns:
            Dict: A mapping of request numbers to chapter names.
        """
        
        request_number_to_chapter_map = {idx : chapter_name for idx, chapter_name in enumerate(json_file.keys())}
        return request_number_to_chapter_map


    @staticmethod
    def create_chapter_with_number_to_text_map(json_file: Dict[str, List[str]]):
        
        """
        Creates a mapping of chapter names (with section numbers) to their corresponding text.

        Args:
            json_file (Dict[str, List[str]]): A dictionary with chapter names as keys and their sections as values.

        Returns:
            Dict: A mapping of chapter names (with section numbers) to text.
        """
        
        if not json_file:
            print("No value in json file")
            return {}
        
        chapter_sections_to_text_map = {}
        for chapter_name in json_file.keys():
            chapter_sections = json_file[chapter_name]
            
            chapter_sections_to_text = {chapter_name + f"_{section_idx}": chapter_sections[section_idx] for section_idx in range(len(chapter_sections))}
            
            chapter_sections_to_text_map.update(chapter_sections_to_text)
            
        return chapter_sections_to_text_map


    def _create_request_object(self, *, request_number: int, text: str)->Dict[str, Any]:
    
        """
        Creates a request object for the OpenAI embeddings API.
    
        Args:
            request_number (int): The sequential request number.
            text (str): The text to be embedded.
    
        Returns:
            Dict[str, Any]: A dictionary representing the API request object.
        """
        
        request_object = {
            "custom_id": f"request-{request_number}",
            "method": "POST",
            "url": "/v1/embeddings",
            "body": {
                "model": "text-embedding-3-small",
                "input": text,
                "encoding_format": "float",
                
                }
            }
        return request_object



    def create_request_objects(self, request_number_to_chapter_map: Dict, chapter_sections_to_text_map: Dict, request_folder:str):
        
        """
        Creates and saves request objects for the OpenAI embeddings API as JSONL files.

        Args:
            request_number_to_chapter_map (Dict): A mapping of request numbers to chapter names.
            chapter_sections_to_text_map (Dict): A mapping of chapter sections to their text.
            request_folder (str): The folder to save the JSONL file containing request objects.
        """
        
        make_directory(request_folder)
        
        all_request_objects = []
        
        for request_number in request_number_to_chapter_map.keys():
            
            chapter_section = request_number_to_chapter_map[request_number]
            chapter_section_text = chapter_sections_to_text_map[chapter_section]
            
            request_object = self._create_request_object(request_number= request_number, text = chapter_section_text)
            all_request_objects.append(request_object)
        
        with open(request_folder + "/input_jsonl.jsonl", "w") as f:
            for request_object in all_request_objects:
                f.write(json.dumps(request_object) + "\n")
        


    def create_input_files(self, *, request_folder: str)-> List:
    
        """
        Creates input files by uploading JSONL files to OpenAI.

        Args:
            request_folder (str): The folder containing the JSONL files.

        Returns:
            List: A list of batch input file IDs.
        """
        
        input_file_ids = []
        jsonl_files = os.listdir(request_folder)
        if not jsonl_files:
            return []
        
        for jsonl_file in jsonl_files:
            jsonl_filepath = os.path.join(request_folder, jsonl_file)
    
            try:
                input_file = self.openai_client.files.create(
                  file=open(jsonl_filepath, "rb"),
                  purpose="batch"
                )
            except (APIConnectionError, RateLimitError) as e:
                print(f"\nAn error occurred.\n{e}")
                print("Returning an empty List array\n")
                return []
    
            input_file_ids.append(input_file.id)
    
        return input_file_ids



    def _job_starter(self, *,  input_file_id: str)->str:
    
        """
        Starts a job for processing embeddings.

        Args:
            input_file_id (str): The ID of the input file for the job.

        Returns:
            str: The ID of the created batch job.
        """
        
        creation_object = self.openai_client.batches.create(
            input_file_id=input_file_id,
            endpoint="/v1/embeddings",
            completion_window="24h",
            metadata={
              "description": "nightly eval job"
            }
        )
    
        return creation_object.id



    def initialize_jobs(self, *, input_file_ids: List)->List:
    
        """
        Initializes jobs for processing embeddings using the provided input file IDs.

        Args:
            input_file_ids (List): A list of input file IDs to be processed.

        Returns:
            List: A list of job IDs created.
        """
        
        if not input_file_ids:
            print("No Input File IDs generated.\n")
            return []
        
        job_ids = []
        for input_file_id in input_file_ids:
    
            job_id = self._job_starter(input_file_id = input_file_id)
            job_ids.append(job_id)
    
        return job_ids
