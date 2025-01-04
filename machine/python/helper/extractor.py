import zipfile
import io
from pathlib import Path
from typing import Dict, List
from .ipynb_parser import extract_code_from_ipynb

def extract_zip_contents(zip_path: Path) -> List[tuple]:
    """Extract all code files from a zip file, returns list of (filename, content)"""
    contents = []
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file_info in zip_ref.filelist:
                if file_info.filename.endswith(('.cpp', '.py', '.ipynb')):
                    with zip_ref.open(file_info.filename) as f:
                        content = f.read().decode('utf-8', errors='ignore')
                        contents.append((file_info.filename, content))
    except Exception as e:
        print(f"Error extracting zip {zip_path}: {e}")
    return contents

def read_file_content(file_path: Path) -> str:
    """Read content from file"""
    try:
        if file_path.suffix.lower() == '.zip':
            return "\n".join([content for _, content in extract_zip_contents(file_path)])
        elif file_path.suffix.lower() == '.ipynb':
            return extract_code_from_ipynb(file_path)
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def organize_submissions(file_paths: List[Path]) -> Dict[str, List[tuple]]:
    """Organize submissions returning dict of user -> [(filename, content)]"""
    submissions = {}
    
    for path in file_paths:
        if path.suffix.lower() == '.zip':
            user_id = path.stem
            submissions[user_id] = extract_zip_contents(path)
    
    return submissions
