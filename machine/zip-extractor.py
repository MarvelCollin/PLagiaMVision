import zipfile
import os
from pathlib import Path
import io

def extract_submissions(zip_path=None):
    # Get the answer directory
    base_dir = Path(__file__).parent.parent / 'data' / 'answer'
    
    # Find all zip files in the directory
    zip_files = list(base_dir.glob('*.zip'))
    
    if not zip_files:
        print("No zip files found in", base_dir)
        return []
    
    cpp_files = []
    
    # Read each zip file
    for zip_path in zip_files:
        try:
            print(f"\nReading {zip_path.name}...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # Get list of all cpp files in zip
                cpp_in_zip = [f for f in zip_ref.namelist() if f.endswith('.cpp')]
                
                # Store zip path and file info for each cpp file
                for cpp_file in cpp_in_zip:
                    cpp_files.append({
                        'zip_path': zip_path,
                        'file_path': cpp_file,
                        'content': zip_ref.read(cpp_file).decode('utf-8').splitlines(True)
                    })
                
                print(f"Found {len(cpp_in_zip)} .cpp files in {zip_path.name}")
                
        except Exception as e:
            print(f"Error reading {zip_path.name}: {e}")
    
    print(f"\nTotal .cpp files found: {len(cpp_files)}")
    return cpp_files

if __name__ == "__main__":
    files = extract_submissions()
    print("\nFiles found in zips:")
    for file in files:
        print(f"- {file['zip_path'].name}/{file['file_path']}")
