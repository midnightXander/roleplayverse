from pathlib import Path
import os
import json

BASE_DIR = Path(__file__).resolve().parent.parent

def get_characters():
    characters_file = os.path.join(BASE_DIR,"characters/playable_characters.json")
    with open(characters_file,"r") as f:
        characters = json.load(f)
    return characters



