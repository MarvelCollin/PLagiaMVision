import difflib
import os
from pathlib import Path
import re
import argparse
import importlib.util

# Add dynamic import for zip-extractor
def import_zip_extractor():
    module_path = Path(__file__).parent / 'zip-extractor.py'
    spec = importlib.util.spec_from_file_location("zip_extractor", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.extract_submissions

# Get the extract_submissions function
extract_submissions = import_zip_extractor()

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def preprocess_code(lines):
    # Join lines and clean code
    text = ''.join(lines)
    # Remove comments, whitespace, and braces
    text = re.sub(r'//.*?\n|/\*.*?\*/', '', text, flags=re.DOTALL)
    text = re.sub(r'\s+', '', text)
    text = re.sub(r'[{}]', '', text)
    return text.lower()

def get_unique_code(code_lines, template_lines):
    # Process template lines
    template_lines = [line.strip() for line in template_lines]
    template_set = set(template_lines)  # For exact line matching
    
    # Filter out template lines and track excluded lines
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
        # Load template
        if template_path:
            template_path = Path(template_path)
        else:
            template_path = Path(__file__).parent.parent / 'data' / 'template' / 'cpp' / 'template.cpp'
        
        template_lines = read_file(template_path) if template_path.exists() else []
        
        # Get unique code and excluded lines
        unique_lines1, excluded1 = get_unique_code(file1_lines, template_lines)
        unique_lines2, excluded2 = get_unique_code(file2_lines, template_lines)
        
        # Process remaining code for similarity
        text1 = preprocess_code(unique_lines1)
        text2 = preprocess_code(unique_lines2)
        
        # Calculate similarity only on non-template code
        matcher = difflib.SequenceMatcher(None, text1, text2)
        similarity_ratio = round(matcher.ratio() * 100, 2)
        
        return similarity_ratio, unique_lines1, unique_lines2, excluded1, excluded2
        
    except Exception as e:
        print(f"Warning: Template processing error - {e}")
        return 0.0, [], [], [], []

def find_matching_lines(lines1, lines2):
    """Find identical lines between two files"""
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

def check_all_submissions(template_path=None):
    submissions = extract_submissions()
    results = []
    total_files = len(submissions)
    
    for i in range(total_files):
        for j in range(total_files):
            if i == j:
                continue
                
            file1 = submissions[i]
            file2 = submissions[j]
            
            try:
                similarity_ratio, unique1, unique2, _, _ = calculate_similarity(
                    file1['content'],
                    file2['content'],
                    template_path
                )
                
                if similarity_ratio >= 80:
                    matching_lines = find_matching_lines(unique1, unique2)
                    results.append({
                        'file1': f"{file1['zip_path'].name}/{file1['file_path']}",
                        'file2': f"{file2['zip_path'].name}/{file2['file_path']}",
                        'similarity': similarity_ratio,
                        'matching_lines': matching_lines
                    })
                
            except Exception as e:
                pass
    
    return results

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    parser = argparse.ArgumentParser(description='Code Similarity Checker')
    parser.add_argument('--template', type=str, help='Path to template file')
    args = parser.parse_args()
    
    # Clear screen before showing results
    clear_screen()
    
    results = check_all_submissions(args.template)
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    print("=" * 50)
    print("CODE SIMILARITY ANALYSIS")
    print("=" * 50)
    
    for result in results:
        print(f"\n{'-' * 50}")
        print(f"{result['file1']} <-> {result['file2']}")
        print(f"Similarity: {result['similarity']}%")
        if result['matching_lines']:
            print("\nMatching code:")
            for line in result['matching_lines']:
                print(f"  {line}")
        print(f"{'-' * 50}")

if __name__ == '__main__':
    main()
