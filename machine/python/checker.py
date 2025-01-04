import os
from pathlib import Path
import re
from difflib import SequenceMatcher, Differ
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent))

from helper.extractor import read_file_content, organize_submissions
import json
from datetime import datetime

def normalize_code(code):
    # Remove comments
    code = re.sub(r'//.*?\n|/\*.*?\*/', '', code, flags=re.S)
    # Remove empty lines and whitespace
    code = '\n'.join(line.strip() for line in code.splitlines() if line.strip())
    # Convert to lowercase
    return code.lower()

def get_similarity(text1, text2):
    return SequenceMatcher(None, text1, text2).ratio()

def get_similar_segments(code1, code2):
    """Find similar code segments between two files"""
    differ = Differ()
    lines1 = code1.splitlines()
    lines2 = code2.splitlines()
    
    # Get diff and find matching segments
    diff = list(differ.compare(lines1, lines2))
    similar_segments = []
    current_segment = []
    
    for line in diff:
        if line.startswith('  '): # Matching lines
            current_segment.append(line[2:])
        elif current_segment:
            if len(current_segment) >= 3:  # Only include segments with 3+ lines
                similar_segments.append('\n'.join(current_segment))
            current_segment = []
            
    if current_segment and len(current_segment) >= 3:
        similar_segments.append('\n'.join(current_segment))
        
    return similar_segments

def check_plagiarism():
    base_path = Path('../data/answer')
    result_path = Path('../result/result.json')
    all_files = []
    
    # Collect all .cpp and .zip files
    for folder in base_path.iterdir():
        if folder.is_dir():
            for file in folder.glob('*.*'):
                if file.suffix.lower() in ['.cpp', '.zip']:
                    all_files.append(file)
    
    # Compare each file with every other file
    results = []
    for i, file1 in enumerate(all_files):
        code1 = normalize_code(read_file_content(file1))
            
        for file2 in all_files[i+1:]:
            code2 = normalize_code(read_file_content(file2))
            
            similarity = get_similarity(code1, code2)
            if similarity > 0.7:  # Threshold for suspicious similarity
                similar_segments = get_similar_segments(code1, code2)
                results.append({
                    'file1': str(file1.relative_to(base_path)),
                    'file2': str(file2.relative_to(base_path)),
                    'similarity': float(f"{similarity:.4f}"),
                    'similar_segments': similar_segments
                })
    
    # Create result object
    result_data = {
        "timestamp": datetime.now().isoformat(),
        "results": results
    }
    
    # Save to JSON file
    result_path.parent.mkdir(exist_ok=True)
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result_data, f, indent=4)
    
    # Print results
    if results:
        print(f"\nPotential plagiarism detected. Results saved to {result_path}")
    else:
        print("\nNo suspicious similarities found.")

def check_plagiarism_files(file_paths):
    """Check plagiarism between different user submissions"""
    results = []
    
    # Organize submissions by user
    submissions = organize_submissions(file_paths)
    users = list(submissions.keys())
    
    # Compare each user's submission with other users
    for i, user1 in enumerate(users):
        for user2 in users[i+1:]:
            # Compare all files from user1 with all files from user2
            for idx1, code1 in enumerate(submissions[user1]):
                code1_normalized = normalize_code(code1)
                
                for idx2, code2 in enumerate(submissions[user2]):
                    code2_normalized = normalize_code(code2)
                    
                    similarity = get_similarity(code1_normalized, code2_normalized)
                    if similarity > 0.7:  # Threshold for suspicious similarity
                        similar_segments = get_similar_segments(code1, code2)
                        results.append({
                            'file1': f"{user1}/file_{idx1+1}",
                            'file2': f"{user2}/file_{idx2+1}",
                            'user1': user1,
                            'user2': user2,
                            'similarity': float(f"{similarity:.4f}"),
                            'similar_segments': similar_segments,
                            'originalCode1': code1,
                            'originalCode2': code2
                        })
    
    return {
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

def process_comparison(file1, file2, code1, code2, results):
    similarity = get_similarity(code1, code2)
    if similarity > 0.7:  # Threshold for suspicious similarity
        similar_segments = get_similar_segments(code1, code2)
        results.append({
            'file1': str(file1.name),
            'file2': str(file2.name),
            'directory1': str(file1.parent.name),
            'directory2': str(file2.parent.name),
            'similarity': float(f"{similarity:.4f}"),
            'similar_segments': similar_segments,
            'originalCode1': code1,
            'originalCode2': code2
        })

if __name__ == "__main__":
    check_plagiarism()
