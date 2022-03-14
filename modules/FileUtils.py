import json
import os
from typing import List


def file_type_search(directory: str, extension: str) -> List[str]:
    working_files: List[str] = []

    # Everything in each directory and subdirectory
    for current_path, directories, files in os.walk(directory):
        for file in files:
            if not file.endswith(extension):
                continue

            working_files.append(
                current_path.replace("\\", "/") + "/" + file
            )

    return working_files


def load_json_file(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        return json.loads(file.read())
