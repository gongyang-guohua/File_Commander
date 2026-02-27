import os
import glob
from pathlib import Path
import win32com.client as win32

def convert_to_docx(folder_path):
    word = win32.gencache.EnsureDispatch('Word.Application')
    word.Visible = False
    
    folder = Path(folder_path)
    doc_files = list(folder.glob("*.doc"))
    
    print(f"Found {len(doc_files)} .doc files in {folder_path}")
    
    count = 0
    for doc_file in doc_files:
        if doc_file.suffix.lower() != '.doc': # Skip .docx potentially caught if glob is weird
            continue
            
        docx_path = doc_file.with_suffix('.docx')
        if docx_path.exists():
            print(f"Skipping (already exists): {doc_file.name}")
            continue
            
        print(f"Converting: {doc_file.name}...")
        try:
            doc = word.Documents.Open(str(doc_file.resolve()))
            doc.SaveAs2(str(docx_path.resolve()), FileFormat=16) # 16 = wdFormatXMLDocument (docx)
            doc.Close()
            count += 1
        except Exception as e:
            print(f"Failed to convert {doc_file.name}: {e}")

    print(f"Conversion complete. Converted {count} files.")
    word.Quit()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, help="Directory containing .doc files")
    args = parser.parse_args()
    convert_to_docx(args.dir)
