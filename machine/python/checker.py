import os
from pathlib import Path
import re
from difflib import SequenceMatcher

def normalize_code(code):
    # Remove comments
    code = re.sub(r'//.*?\n|/\*.*?\*/', '', code, flags=re.S)
    # Remove empty lines and whitespace
    code = '\n'.join(line.strip() for line in code.splitlines() if line.strip())
    # Convert to lowercase
    return code.lower()

def get_similarity(text1, text2):
    return SequenceMatcher(None, text1, text2).ratio()

def check_plagiarism():
    base_path = Path('../data/answer')
    all_files = []
    
    # Collect all .cpp files
    for folder in base_path.iterdir():
        if folder.is_dir():
            for file in folder.glob('*.cpp'):
                all_files.append(file)
    
    # Compare each file with every other file
    results = []
    for i, file1 in enumerate(all_files):
        with open(file1, 'r', encoding='utf-8') as f1:
            code1 = normalize_code(f1.read())
            
        for file2 in all_files[i+1:]:
            with open(file2, 'r', encoding='utf-8') as f2:
                code2 = normalize_code(f2.read())
            
            similarity = get_similarity(code1, code2)
            if similarity > 0.7:  # Threshold for suspicious similarity
                results.append({
                    'file1': str(file1.relative_to(base_path)),
                    'file2': str(file2.relative_to(base_path)),
                    'similarity': similarity
                })
    
    # Print results
    if results:
        print("\nPotential plagiarism detected:")
        for result in results:
            print(f"\nSimilarity: {result['similarity']*100:.2f}%")
            print(f"File 1: {result['file1']}")
            print(f"File 2: {result['file2']}")
    else:
        print("\nNo suspicious similarities found.")

if __name__ == "__main__":
    check_plagiarism()
