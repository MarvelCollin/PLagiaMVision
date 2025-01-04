import json
import re

def extract_code_from_ipynb(file_path):
    """Extract Python code from Jupyter notebook"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        code_cells = []
        for cell in notebook['cells']:
            if cell['cell_type'] == 'code':
                # Get source code and join lines
                source = ''.join(cell['source'])
                # Remove magic commands and shell commands
                lines = [line for line in source.split('\n') 
                        if not line.startswith(('%', '!', '$'))]
                code_cells.append('\n'.join(lines))
        
        return '\n\n'.join(code_cells)
    except Exception as e:
        print(f"Error parsing notebook {file_path}: {e}")
        return ""
