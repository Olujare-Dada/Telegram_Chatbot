
"""
auxiliaries.py

This module contains utility functions and type definitions to support various operations within the chatbot. It includes type hints for clarity and ensures compatibility with different data structures used throughout the package.

Functions:
- load_dotenv: Loads environment variables from a .env file.
- Additional utility functions can be added here as needed.

Type Aliases:
- List: A generic type for lists.
- Dict: A generic type for dictionaries.
- Any: Represents any type.
- Tuple: A type for tuples.
- Union: Represents a type that can be one of several types.
"""

from typing import List, Dict, Any, Tuple, Union
import os
from dotenv import load_dotenv
import numpy as np
