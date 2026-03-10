import os
from typing import List

def get_supported_files(directory: str) -> List[str]:
    supported_extensions = {".pdf", ".docx"}
    files = []
    
    if not os.path.exists(directory):
        return files

    for root, _, filenames in os.walk(directory):
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in supported_extensions:
                files.append(os.path.join(root, filename))
                
    return files
