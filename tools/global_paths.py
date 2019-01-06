import os

from pathlib import Path


MAIN_DIR = str(Path(__file__).parent.parent)
MAPPING_DIR = os.path.join(MAIN_DIR, "mapping/")
MONTHS_NAMES_FILE = os.path.join(MAPPING_DIR, "months_names.json")
BUILDINGS_NAMES_POLISH_FILE = os.path.join(MAPPING_DIR, "buildings_names_polish.json")
BUILDINGS_CODE_FILE = os.path.join(MAPPING_DIR, "buildings_codes.json")
