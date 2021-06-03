import os
from pathlib import Path
from os.path import dirname, join



def load_env():
    "Get the path to the .env file and load it."
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.path.join(BASE_DIR, '.env')
    