import difflib
import os
from pathlib import Path
import re

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.readlines()

def preprocess_code(lines):
    # Join lines and remove ALL whitespace and braces
    text = ''.join(lines)
    # Remove all whitespace, newlines, and braces
    text = re.sub(r'\s+', '', text)
    text = re.sub(r'[{}]', '', text)
    return text.lower()  # Convert to lowercase for case-insensitive comparison

def calculate_similarity(file1_lines, file2_lines):
    # Preprocess both files
    text1 = preprocess_code(file1_lines)
    text2 = preprocess_code(file2_lines)
    
    # Direct string comparison after preprocessing
    if text1 == text2:
        return 100.0, 100.0
    
    # If not exactly equal, calculate similarity
    matcher = difflib.SequenceMatcher(None, text1, text2)
    similarity_ratio = round(matcher.ratio() * 100, 2)
    
    # Clean lines for line-based comparison
    cleaned_lines1 = [re.sub(r'\s+', '', line.strip()) for line in file1_lines if line.strip() and not line.strip().startswith('//')]
    cleaned_lines2 = [re.sub(r'\s+', '', line.strip()) for line in file2_lines if line.strip() and not line.strip().startswith('//')]
    
    # Remove empty lines and brace-only lines
    cleaned_lines1 = [line for line in cleaned_lines1 if line and line != '{' and line != '}']
    cleaned_lines2 = [line for line in cleaned_lines2 if line and line != '{' and line != '}']
    
    if cleaned_lines1 == cleaned_lines2:
        return 100.0, 100.0
        
    # Calculate line similarity only if needed
    differ = difflib.Differ()
    diff = list(differ.compare(cleaned_lines1, cleaned_lines2))
    similar_lines = len([d for d in diff if d.startswith('  ')])
    total_lines = max(len(cleaned_lines1), len(cleaned_lines2))
    line_similarity = round((similar_lines / total_lines) * 100, 2) if total_lines > 0 else 0
    
    return similarity_ratio, line_similarity

def main():
    # Get the absolute path to the answer directory
    base_dir = Path(__file__).parent.parent / 'data' / 'answer'
    
    # Correct path construction for the answer files
    file1_path = base_dir / 'answer_1.cpp'
    file2_path = base_dir / 'answer_2.cpp'
    
    try:
        file1_lines = read_file(file1_path)
        file2_lines = read_file(file2_path)
        
        similarity_ratio, line_similarity = calculate_similarity(file1_lines, file2_lines)
        
        print("\n=== Code Similarity Analysis ===")
        print(f"Overall Similarity: {similarity_ratio}%")
        print(f"Line-based Similarity: {line_similarity}%")
        print("\nDetailed Analysis:")
        print(f"File 1: {file1_path.name}")
        print(f"File 2: {file2_path.name}")
        print(f"File 1 Lines: {len(file1_lines)}")
        print(f"File 2 Lines: {len(file2_lines)}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure both files exist in the correct directory.")

if __name__ == "__main__":
    main()
