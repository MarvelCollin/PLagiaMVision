import zipfile
import io
from pathlib import Path

def read_file_content(file_path: Path) -> str:
    """Read content from regular file or zip file"""
    if zipfile.is_zipfile(file_path):
        cpp_contents = []
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            for file_info in zip_ref.filelist:
                if file_info.filename.endswith('.cpp'):
                    with zip_ref.open(file_info.filename) as f:
                        cpp_contents.append(f.read().decode('utf-8', errors='ignore'))
        return '\n'.join(cpp_contents)
    else:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
