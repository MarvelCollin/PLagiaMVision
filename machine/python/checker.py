import os
from pathlib import Path
import re
from difflib import SequenceMatcher, Differ
import sys
from pathlib import Path
import ast
import tokenize
from io import StringIO

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent))

from helper.extractor import read_file_content, organize_submissions
import json
from datetime import datetime

def normalize_code(code):
    """Normalize code for comparison by removing irrelevant differences"""
    # Remove comments
    code = re.sub(r'//.*?\n|/\*.*?\*/', '', code, flags=re.S)
    
    # Remove braces and non-essential symbols
    code = re.sub(r'[{}();]', '', code)
    
    # Normalize whitespace
    code = ' '.join(code.split())
    
    # Normalize string literals
    code = re.sub(r'".*?"', '""', code)
    code = re.sub(r'\'.*?\'', '\'\'', code)
    
    # Normalize numbers     
    code = re.sub(r'\b\d+\b', 'N', code)
    
    # Remove preprocessor directives
    code = re.sub(r'#.*?\n', '\n', code)
    
    return code.lower()

def get_similarity(text1, text2):
    """Calculate similarity with improved accuracy"""
    # Use token-based similarity
    tokens1 = set(text1.split())
    tokens2 = set(text2.split())
    
    if not tokens1 or not tokens2:
        return 0.0  # Return 0 similarity if either text is empty
    
    intersection = tokens1.intersection(tokens2)
    union = tokens1.union(tokens2)
    
    return len(intersection) / len(union)

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

def find_exact_matches(code1, code2, min_lines=5):
    """Find exact matching code segments with improved accuracy"""
    if not code1.strip() or not code2.strip():
        return []  # Return empty list if either code is empty
    
    lines1 = code1.splitlines()
    lines2 = code2.splitlines()
    matches = []
    
    # Use sliding window for comparison
    for i in range(len(lines1) - min_lines + 1):
        window1 = lines1[i:i + min_lines]
        window1_str = '\n'.join(window1)
        
        for j in range(len(lines2) - min_lines + 1):
            window2 = lines2[j:j + min_lines]
            window2_str = '\n'.join(window2)
            
            if window1_str == window2_str:
                if window1_str.strip():  # Ensure segment is not empty
                    matches.append({
                        'segment': window1_str,
                        'segment2': window2_str,
                        'line_count': min_lines,
                        'line_number1': i + 1,
                        'line_number2': j + 1
                    })
    
    return matches

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

def merge_overlapping_matches(matches):
    """Merge overlapping plagiarism matches, keeping the largest segments."""
    if not matches:
        return []
    
    # Sort matches by start line
    sorted_matches = sorted(matches, key=lambda x: x['line_number1'])
    merged = []
    
    current = sorted_matches[0]
    
    for match in sorted_matches[1:]:
        current_end = current['line_number1'] + current['line_count'] - 1
        next_start = match['line_number1']
        next_end = match['line_number1'] + match['line_count'] - 1
        
        if next_start <= current_end:
            # Overlapping segments; keep the one with larger line_count
            if match['line_count'] > current['line_count']:
                current = match
        else:
            merged.append(current)
            current = match
    
    merged.append(current)
    return merged

def check_plagiarism_files(file_paths, progress_queue=None, similarity_threshold=0.7, batch_size=1000, callback=None):
    """Check plagiarism between all files across all submissions without redundant comparisons"""
    results = []
    checked_lines = {}  # Dictionary to track checked lines per file pair

    if progress_queue:
        progress_queue.put({"status": "processing", "stage": "Organizing submissions", "progress": 0})
    
    # Organize submissions
    submissions = organize_submissions(file_paths)
    users = list(submissions.keys())
    
    # Create a flat list of all files with their metadata
    all_files = []
    for user, files in submissions.items():
        for filename, content in files:
            normalized_content = normalize_code(content)
            all_files.append({
                'user': user,
                'filename': filename,
                'content': content,
                'normalized': normalized_content
            })
    
    total_comparisons = (len(all_files) * (len(all_files) - 1)) // 2
    comparisons_done = 0
    
    # Compare each file with every other file without redundancy
    for i, file1 in enumerate(all_files):
        for j in range(i + 1, len(all_files)):
            file2 = all_files[j]
            file_pair = (file1['filename'], file2['filename'])
            
            # Initialize checked lines for this file pair if not already done
            if file_pair not in checked_lines:
                checked_lines[file_pair] = set()
            
            # Skip comparison if files are from the same user
            if file1['user'] == file2['user']:
                if callback:
                    callback({
                        "type": "skip",
                        "message": f"Skipping comparison of files from same user: {file1['user']}",
                        "files": [file1['filename'], file2['filename']]
                    })
                continue
            
            # Skip comparison if either file is empty
            if not file1['content'].strip() or not file2['content'].strip():
                if callback:
                    callback({
                        "type": "info",
                        "message": "Skipping comparison due to empty file.",
                        "files": [file1['filename'], file2['filename']]
                    })
                comparisons_done += 1
                continue
                
            comparisons_done += 1
            
            # For thresholds above 0.4, perform exact match checks
            if similarity_threshold > 0.4:
                exact_matches = find_exact_matches(file1['content'], file2['content'])
                
                # Filter out matches that have already been checked
                exact_matches = [
                    match for match in exact_matches
                    if (match['line_number1'], match['line_number2']) not in checked_lines[file_pair]
                ]
                
                if exact_matches:
                    exact_matches = merge_overlapping_matches(exact_matches)
                    
                    # Mark these lines as checked
                    for match in exact_matches:
                        checked_lines[file_pair].add((match['line_number1'], match['line_number2']))
                    
                    if callback:
                        callback({
                            "type": "warning",
                            "message": "Exact match found!",
                            "files": [file1['filename'], file2['filename']],
                            "matches": len(exact_matches),
                            "details": [
                                f"Lines {m['line_number1']}-{m['line_number1'] + m['line_count'] - 1}"
                                for m in exact_matches
                            ]
                        })
                    results.append({
                        'file1': f"{file1['filename']}",
                        'file2': f"{file2['filename']}",
                        'user1': file1['user'],
                        'user2': file2['user'],
                        'similarity': 1.0,
                        'similar_segments': [match['segment'] for match in exact_matches],
                        'match_details': exact_matches,
                        'originalCode1': file1['content'],
                        'originalCode2': file2['content'],
                        'is_exact_match': True
                    })
                    continue

            # Similarity check
            similarity = get_similarity(file1['normalized'], file2['normalized'])
            
            if similarity > similarity_threshold:
                # For thresholds above 0.3, get similar segments
                if similarity > 0.3:
                    similar_segments = get_similar_segments(file1['content'], file2['content'])
                    
                    # Mark these segments as checked
                    for segment in similar_segments:
                        lines1 = segment.split('\n')
                        for idx, line in enumerate(lines1, start=1):
                            checked_lines[file_pair].add((idx, idx))
                else:
                    similar_segments = []  # Skip detailed analysis for very low similarities
                
                if callback:
                    callback({
                        "type": "detection",
                        "message": f"Similarity detected: {similarity:.1%}",
                        "files": [file1['filename'], file2['filename']],
                        "similarity": similarity,
                        "segmentCount": len(similar_segments),
                        "reason": (
                            "High similarity in code structure" if similarity > 0.8
                            else "Moderate code similarity detected"
                        )
                    })
                results.append({
                    'file1': f"{file1['filename']}",
                    'file2': f"{file2['filename']}",
                    'user1': file1['user'],
                    'user2': file2['user'],
                    'similarity': float(f"{similarity:.4f}"),
                    'similar_segments': similar_segments,
                    'originalCode1': file1['content'],
                    'originalCode2': file2['content'],
                    'is_exact_match': False
                })
            else:
                if callback:
                    callback({
                        "type": "info",
                        "message": f"Low similarity: {similarity:.1%}",
                        "files": [file1['filename'], file2['filename']],
                        "reason": "Below threshold"
                    })

            # Update progress
            if progress_queue and comparisons_done % 100 == 0:
                progress_queue.put({
                    "status": "processing",
                    "stage": f"Comparing files ({comparisons_done}/{total_comparisons})",
                    "progress": (comparisons_done / total_comparisons) * 100,
                    "currentComparison": {
                        "user1": file1['user'],
                        "user2": file2['user'],  # Fixed mismatched quotation
                        "file1": file1['filename'],
                        "file2": file2['filename']
                    }
                })
    
    # Sort results: exact matches first, then by similarity
    results.sort(key=lambda x: (-int(x.get('is_exact_match', False)), 
                               -x['similarity'],
                               len(x.get('similar_segments', []))))
    
    # Limit results more aggressively for very low thresholds
    max_results = min(batch_size, 100 if similarity_threshold < 0.3 else batch_size)
    
    return {
        "timestamp": datetime.now().isoformat(),
        "results": results[:max_results],
        "summary": {
            "total_submissions": len(users),
            "total_files": len(all_files),
            "total_comparisons": comparisons_done,
            "significant_matches": len(results),
            "threshold_used": similarity_threshold
        }
    }

def get_detailed_comparison(code1, code2, normalized1, normalized2):
    """Get detailed comparison information between two code snippets"""
    lines1 = code1.splitlines()
    lines2 = code2.splitlines()
    norm_lines1 = normalized1.splitlines()
    norm_lines2 = normalized2.splitlines()
    
    matching_segments = []
    current_match = None
    
    for i in range(len(norm_lines1)):
        for j in range(len(norm_lines2)):
            if norm_lines1[i] == norm_lines2[j]:
                if current_match and current_match['start2'] + current_match['length'] == j:
                    # Continue existing match
                    current_match['length'] += 1
                    current_match['code'] += '\n' + lines1[i]
                else:
                    # Start new match
                    if current_match:
                        matching_segments.append(current_match)
                    current_match = {
                        'start1': i,
                        'start2': j,
                        'length': 1,
                        'code': lines1[i]
                    }
                break
        else:
            if current_match:
                matching_segments.append(current_match)
                current_match = None
    
    if current_match:
        matching_segments.append(current_match)
    
    return {
        'lineMatches': sum(segment['length'] for segment in matching_segments),
        'totalLines': max(len(lines1), len(lines2)),
        'matchingSegments': matching_segments
    }

def process_comparison(file1, file2, code1, code2, results):
    # Use normalized comparison for similarity check
    normalized1 = normalize_code(code1)
    normalized2 = normalize_code(code2)
    similarity = get_similarity(normalized1, normalized2)
    
    if similarity > 0.7:
        exact_matches = find_exact_matches(code1, code2)
        if exact_matches:
            comparison_details = get_detailed_comparison(code1, code2, normalized1, normalized2)
            
            results.append({
                'file1': str(file1.name),
                'file2': str(file2.name),
                'directory1': str(file1.parent.name),
                'directory2': str(file2.parent.name),
                'similarity': float(f"{similarity:.4f}"),
                'match_details': exact_matches,
                'originalCode1': code1,
                'originalCode2': code2,
                'normalizedCode1': normalized1,
                'normalizedCode2': normalized2,
                'comparisonDetails': comparison_details,
                'is_exact_match': bool(exact_matches)
            })
        elif exact_matches:
            # Handle cases with exact matches but no variable changes
            results.append({
                'file1': str(file1.name),
                'file2': str(file2.name),
                'directory1': str(file1.parent.name),
                'directory2': str(file2.parent.name),
                'similarity': float(f"{similarity:.4f}"),
                'match_details': exact_matches,
                'originalCode1': code1,
                'originalCode2': code2,
                'normalizedCode1': normalized1,
                'normalizedCode2': normalized2,
                'comparisonDetails': {},
                'is_exact_match': False  # Set to False to prevent false plagiarism flags
            })

if __name__ == "__main__":
    check_plagiarism()
