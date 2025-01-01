from pathlib import Path

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def get_template_path(template_path=None):
    if template_path:
        return Path(template_path)
    return Path(__file__).parent.parent.parent / 'data' / 'template' / 'cpp' / 'template.cpp'
