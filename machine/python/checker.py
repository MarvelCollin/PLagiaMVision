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

def normalize_variables(code):
    """Replace all variable names with generic placeholders"""
    try:
        # First, try parsing as Python code
        tree = ast.parse(code)
        var_map = {}
        var_counter = 1

        class VariableNormalizer(ast.NodeTransformer):
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Store):
                    if node.id not in var_map:
                        var_map[node.id] = f'var_{var_counter}'
                        var_counter += 1
                return ast.Name(id=var_map.get(node.id, node.id), ctx=node.ctx)

        # Transform the AST
        normalized = VariableNormalizer().visit(tree)
        return ast.unparse(normalized)
    except:
        # If Python parsing fails, try C++-style normalization
        try:
            result = []
            var_map = {}
            var_counter = 1
            
            # Tokenize the code
            tokens = tokenize.generate_tokens(StringIO(code).readline)
            
            for token in tokens:
                if token.type == tokenize.NAME:
                    # Check if it's likely a variable name (not a keyword or type)
                    if not token.string in ['int', 'float', 'double', 'char', 'void', 'for', 'while', 'if', 'else']:
                        if token.string not in var_map:
                            var_map[token.string] = f'var_{var_counter}'
                            var_counter += 1
                        result.append(var_map[token.string])
                    else:
                        result.append(token.string)
                else:
                    result.append(token.string)
            
            return ''.join(result)
        except:
            # If all parsing fails, return original code
            return code

def normalize_code(code):
    # First normalize variables
    normalized = normalize_variables(code)
    # Then apply existing normalizations
    normalized = re.sub(r'//.*?\n|/\*.*?\*/', '', normalized, flags=re.S)
    normalized = '\n'.join(line.strip() for line in normalized.splitlines() if line.strip())
    return normalized.lower()

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

def find_exact_matches(code1, code2, min_lines=4):
    """Find exact matching code segments with variable name normalization"""
    # Normalize both codes first
    norm_code1 = normalize_variables(code1)
    norm_code2 = normalize_variables(code2)
    
    lines1 = norm_code1.splitlines()
    lines2 = norm_code2.splitlines()
    orig_lines1 = code1.splitlines()
    orig_lines2 = code2.splitlines()
    matches = []
    
    for i in range(len(lines1)):
        for j in range(len(lines2)):
            match_length = 0
            while (i + match_length < len(lines1) and 
                   j + match_length < len(lines2) and 
                   lines1[i + match_length].strip() == lines2[j + match_length].strip()):
                match_length += 1
            
            if match_length >= min_lines:
                # Get both normalized and original code segments
                norm_segment = '\n'.join(lines1[i:i + match_length])
                orig_segment1 = '\n'.join(orig_lines1[i:i + match_length])
                orig_segment2 = '\n'.join(orig_lines2[j:i + match_length])
                
                if norm_segment.strip():
                    matches.append({
                        'segment': orig_segment1,
                        'segment2': orig_segment2,  # Add the second version to show variable differences
                        'normalized_segment': norm_segment,
                        'line_count': match_length,
                        'line_number1': i + 1,
                        'line_number2': j + 1,
                        'has_variable_changes': orig_segment1 != orig_segment2
                    })
                i += match_length - 1
                break
    
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

def check_plagiarism_files(file_paths, progress_queue=None, similarity_threshold=0.7, batch_size=1000, callback=None):
    """Check plagiarism between all files across all submissions"""
    results = []
    
    if progress_queue:
        progress_queue.put({"status": "processing", "stage": "Organizing submissions", "progress": 0})
    
    # Organize submissions
    submissions = organize_submissions(file_paths)
    users = list(submissions.keys())
    
    # Create a flat list of all files with their metadata
    all_files = []
    for user, files in submissions.items():
        for filename, content in files:
            all_files.append({
                'user': user,
                'filename': filename,
                'content': content,
                'normalized': normalize_code(content)
            })
    
    total_comparisons = (len(all_files) * (len(all_files) - 1)) // 2
    comparisons_done = 0
    
    # Compare each file with every other file
    for i, file1 in enumerate(all_files):
        for j, file2 in enumerate(all_files[i+1:], i+1):
            # Skip comparison if files are from the same user
            if file1['user'] == file2['user']:
                if callback:
                    callback({
                        "type": "skip",
                        "message": f"Skipping comparison of files from same user: {file1['user']}",
                        "files": [file1['filename'], file2['filename']]
                    })
                continue
                
            comparisons_done += 1
            
            # For very low thresholds, skip exact match check to improve performance
            if similarity_threshold > 0.4:
                exact_matches = find_exact_matches(file1['content'], file2['content'])
                
                if exact_matches:
                    if callback:
                        callback({
                            "type": "warning",
                            "message": "Exact match found!",
                            "files": [file1['filename'], file2['filename']],
                            "matches": len(exact_matches),
                            "details": [
                                f"Lines {m['line_number1']}-{m['line_number1'] + m['line_count']}"
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
                # For very low thresholds, only get segments for higher similarities
                if similarity > 0.3:
                    similar_segments = get_similar_segments(file1['content'], file2['content'])
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
                        "user2": file2['user'],
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

if __name__ == "__main__":
    check_plagiarism()
