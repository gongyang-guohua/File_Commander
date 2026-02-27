import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime
import logging

def setup_logging(path):
    logging.basicConfig(
        filename=os.path.join(path, 'organize.log'),
        level=logging.INFO,
        format='%(asctime)s - %(message)s',
        encoding='utf-8'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    logging.getLogger('').addHandler(console)

def safe_move(src, dst_folder):
    if not os.path.exists(dst_folder):
        os.makedirs(dst_folder)
    
    src_path = Path(src)
    dst_path = Path(dst_folder) / src_path.name
    
    # Avoid overwriting
    counter = 1
    while dst_path.exists():
        stem = src_path.stem
        suffix = src_path.suffix
        dst_path = Path(dst_folder) / f"{stem}_{counter}{suffix}"
        counter += 1
        
    try:
        shutil.move(str(src_path), str(dst_path))
        logging.info(f"Moved: {src_path.name} -> {dst_folder}")
    except Exception as e:
        logging.error(f"Error moving {src_path.name}: {e}")

def organize_by_extension(path):
    EXT_MAP = {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
        'Documents': ['.pdf', '.docx', '.doc', '.txt', '.md', '.xlsx', '.csv', '.pptx'],
        'Code': ['.py', '.js', '.html', '.css', '.json', '.java', '.cpp', '.sql'],
        'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
        'Audio': ['.mp3', '.wav', '.flac', '.m4a'],
        'Video': ['.mp4', '.avi', '.mkv', '.mov']
    }
    
    path_obj = Path(path)
    for item in path_obj.iterdir():
        if item.is_file() and item.name != 'organize.py' and item.name != 'organize.log':
            ext = item.suffix.lower()
            dest_folder = 'Others'
            
            for folder, exts in EXT_MAP.items():
                if ext in exts:
                    dest_folder = folder
                    break
            
            safe_move(item, os.path.join(path, dest_folder))

def organize_by_date(path):
    path_obj = Path(path)
    for item in path_obj.iterdir():
        if item.is_file() and item.name != 'organize.py' and item.name != 'organize.log':
            try:
                mtime = item.stat().st_mtime
                date = datetime.fromtimestamp(mtime)
                folder_name = date.strftime('%Y-%m')
                safe_move(item, os.path.join(path, folder_name))
            except Exception as e:
                logging.error(f"Error processing {item.name}: {e}")

def analyze_directory(path):
    stats = {}
    path_obj = Path(path)
    count = 0
    for item in path_obj.iterdir():
        if item.is_file():
            ext = item.suffix.lower() or 'no_extension'
            stats[ext] = stats.get(ext, 0) + 1
            count += 1
            
    print(f"Total files: {count}")
    print("File types:")
    for ext, num in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        print(f"  {ext}: {num}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organize files in a directory.")
    parser.add_argument("--path", required=True, help="Path to the directory to organize")
    parser.add_argument("--by-extension", action="store_true", help="Organize by file extension")
    parser.add_argument("--by-date", action="store_true", help="Organize by modification date")
    parser.add_argument("--analyze", action="store_true", help="Analyze directory content")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.path):
        print(f"Error: Path {args.path} does not exist.")
        exit(1)
        
    setup_logging(args.path)
    
    if args.analyze:
        analyze_directory(args.path)
    elif args.by_extension:
        organize_by_extension(args.path)
    elif args.by_date:
        organize_by_date(args.path)
    else:
        print("Please specify an action: --analyze, --by-extension, or --by-date")
