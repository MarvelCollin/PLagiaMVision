import zipfile
import os
from pathlib import Path
import io

def read_cpp_from_folder(folder_path):
    """Read all CPP files from a folder recursively"""
    cpp_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.cpp'):
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.readlines()
                        cpp_files.append({
                            'zip_path': folder_path,
                            'file_path': str(file_path.relative_to(folder_path)),
                            'content': content
                        })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    return cpp_files

def extract_submissions(zip_path=None):
    # Get the answer directory
    base_dir = Path(__file__).parent.parent / 'data' / 'answer'
    cpp_files = []
    
    # Process all items in the directory
    for item in base_dir.iterdir():
        try:
            if item.is_file() and item.suffix == '.zip':
                # Handle zip files
                print(f"\nReading zip file: {item.name}")
                with zipfile.ZipFile(item, 'r') as zip_ref:
                    cpp_in_zip = [f for f in zip_ref.namelist() if f.endswith('.cpp')]
                    for cpp_file in cpp_in_zip:
                        cpp_files.append({
                            'zip_path': item,
                            'file_path': cpp_file,
                            'content': zip_ref.read(cpp_file).decode('utf-8').splitlines(True)
                        })
                print(f"Found {len(cpp_in_zip)} .cpp files in {item.name}")
            
            elif item.is_dir():
                # Handle folders
                print(f"\nReading folder: {item.name}")
                folder_files = read_cpp_from_folder(item)
                cpp_files.extend(folder_files)
                print(f"Found {len(folder_files)} .cpp files in {item.name}")
                
        except Exception as e:
            print(f"Error processing {item.name}: {e}")
    
    print(f"\nTotal .cpp files found: {len(cpp_files)}")
    return cpp_files

if __name__ == "__main__":
    files = extract_submissions()
    print("\nFiles found:")
    for file in files:
        print(f"- {file['zip_path'].name}/{file['file_path']}")
