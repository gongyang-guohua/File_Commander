from pathlib import Path
import os
import argparse

def cleanup_docs(folder_path):
    folder = Path(folder_path)
    doc_files = list(folder.glob("*.doc"))
    
    print(f"Found {len(doc_files)} .doc files in {folder_path}")
    
    deleted_count = 0
    for doc_file in doc_files:
        if doc_file.suffix.lower() != '.doc': 
            continue
            
        # Check if .docx exists
        docx_path = doc_file.with_suffix('.docx')
        if docx_path.exists():
            print(f"Deleting {doc_file.name} (replaced by .docx)...")
            try:
                os.remove(doc_file)
                deleted_count += 1
            except Exception as e:
                print(f"Failed to delete {doc_file.name}: {e}")
        else:
            print(f"Skipping {doc_file.name} (no .docx found)")

    print(f"Cleanup complete. Deleted {deleted_count} files.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, help="Directory containing .doc files")
    args = parser.parse_args()
    cleanup_docs(args.dir)
