import os
import argparse
from core.similarity import calculate_similarity, find_matching_lines
from utils.extractor import extract_submissions
from ai.model import PlagiarismModel

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_all_submissions(template_path=None):
    submissions = extract_submissions()
    results = []
    total_files = len(submissions)
    model = PlagiarismModel()
    
    for i in range(total_files):
        for j in range(i + 1, total_files):  # Optimized to avoid duplicate comparisons
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
                    
                    result = {
                        'file1': f"{file1['zip_path'].name}/{file1['file_path']}",
                        'file2': f"{file2['zip_path'].name}/{file2['file_path']}",
                        'similarity': similarity_ratio,
                        'matching_lines': matching_lines
                    }
                    
                    if model.has_model:
                        ai_result = model.check_similarity(
                            ''.join(file1['content']),
                            ''.join(file2['content'])
                        )
                        if ai_result:
                            result.update(ai_result)
                    
                    results.append(result)
                
            except Exception as e:
                print(f"Error comparing files: {e}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Code Similarity Checker')
    parser.add_argument('--template', type=str, help='Path to template file')
    args = parser.parse_args()
    
    clear_screen()
    results = check_all_submissions(args.template)
    results.sort(key=lambda x: x['similarity'], reverse=True)
    
    print("=" * 50)
    print("CODE SIMILARITY ANALYSIS")
    print("=" * 50)
    
    for result in results:
        print(f"\n{'-' * 50}")
        print(f"{result['file1']} <-> {result['file2']}")
        print(f"Basic Similarity: {result['similarity']}%")
        
        if 'is_plagiarism' in result:
            print(f"AI Prediction: {'Plagiarism' if result['is_plagiarism'] else 'No Plagiarism'}")
            print(f"AI Confidence: {result['confidence']}%")
            print(f"Features: {result['features']}")
            
        print("\nMatching code patterns:")
        for line in result['matching_lines']:
            print(f"  {line}")
        print(f"{'-' * 50}")

if __name__ == '__main__':
    main()
