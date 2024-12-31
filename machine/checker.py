import difflib
import os
from pathlib import Path
import re
import argparse

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

def main():
    # Add command line argument parsing
    parser = argparse.ArgumentParser(description='Code Similarity Checker')
    parser.add_argument('--template', type=str, help='Path to template file')
    parser.add_argument('--file1', type=str, help='Path to first file to compare')
    parser.add_argument('--file2', type=str, help='Path to second file to compare')
    args = parser.parse_args()

    # Get paths
    base_dir = Path(__file__).parent.parent / 'data' / 'answer'
    file1_path = Path(args.file1) if args.file1 else base_dir / 'answer_1.cpp'
    file2_path = Path(args.file2) if args.file2 else base_dir / 'answer_2.cpp'
    
    try:
        # Get template content
        template_path = Path(args.template) if args.template else Path(__file__).parent.parent / 'data' / 'template' / 'cpp' / 'template.cpp'
        if template_path.exists():
            template_lines = read_file(template_path)
            print("\n=== Template File Content ===")
            print(f"Template Path: {template_path}")
            print("Content:")
            print(''.join(template_lines))
            print("="* 30)
        
        file1_lines = read_file(file1_path)
        file2_lines = read_file(file2_path)
        
        similarity_ratio, unique1, unique2, excluded1, excluded2 = calculate_similarity(
            file1_lines, 
            file2_lines,
            template_path=args.template
        )
        
        print("\n=== Code Similarity Analysis ===")
        print(f"Template: {args.template if args.template else 'Default template'}")
        print(f"Similarity (excluding template code): {similarity_ratio}%")
        
        print("\nTemplate Lines Excluded from File 1:")
        for line in excluded1:
            print(f"[-] {line.strip()}")
            
        print("\nTemplate Lines Excluded from File 2:")
        for line in excluded2:
            print(f"[-] {line.strip()}")
            
        print("\nUnique Lines in File 1:")
        for line in unique1:
            if line.strip():
                print(f"[+] {line.strip()}")
                
        print("\nUnique Lines in File 2:")
        for line in unique2:
            if line.strip():
                print(f"[+] {line.strip()}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure all files exist in the correct directory.")

if __name__ == "__main__":
    main()
