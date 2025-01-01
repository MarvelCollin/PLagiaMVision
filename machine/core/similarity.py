import difflib
import re
from pathlib import Path
from .file_utils import read_file

def preprocess_code(lines):
    text = ''.join(lines)
    text = re.sub(r'//.*?\n|/\*.*?\*/', '', text, flags=re.DOTALL)
    text = re.sub(r'\s+', '', text)
    text = re.sub(r'[{}]', '', text)
    return text.lower()

def get_unique_code(code_lines, template_lines):
    template_lines = [line.strip() for line in template_lines]
    template_set = set(template_lines)
    
    unique_lines = []
    excluded_lines = []
    
    for line in code_lines:
        stripped_line = line.strip()
        if stripped_line and stripped_line in template_set:
            excluded_lines.append(line)
        else:
            unique_lines.append(line)
    
    return unique_lines, excluded_lines

def calculate_similarity(file1_lines, file2_lines, template_path=None):
    try:
        if template_path:
            template_path = Path(template_path)
        else:
            template_path = Path(__file__).parent.parent.parent / 'data' / 'template' / 'cpp' / 'template.cpp'
        
        template_lines = read_file(template_path) if template_path.exists() else []
        
        unique_lines1, excluded1 = get_unique_code(file1_lines, template_lines)
        unique_lines2, excluded2 = get_unique_code(file2_lines, template_lines)
        
        text1 = preprocess_code(unique_lines1)
        text2 = preprocess_code(unique_lines2)
        
        matcher = difflib.SequenceMatcher(None, text1, text2)
        similarity_ratio = round(matcher.ratio() * 100, 2)
        
        return similarity_ratio, unique_lines1, unique_lines2, excluded1, excluded2
        
    except Exception as e:
        print(f"Warning: Template processing error - {e}")
        return 0.0, [], [], [], []

def find_matching_lines(lines1, lines2):
    matching = []
    for line1 in lines1:
        line1_stripped = line1.strip()
        if not line1_stripped:
            continue
        for line2 in lines2:
            if line1_stripped == line2.strip():
                if line1_stripped not in matching:
                    matching.append(line1_stripped)
    return matching
