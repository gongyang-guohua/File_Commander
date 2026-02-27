import os
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime

IGNORE_DIRS = {'.git', 'node_modules', '$RECYCLE.BIN', 'System Volume Information', '__pycache__'}

def get_file_hash(filepath):
    """Calculates SHA-256 hash of a file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return None

def scan_directory(path, calculate_hash=False):
    """Recursively scans a directory and yields file info with resume capability."""
    root_path = Path(path)
    if not root_path.exists():
        print(f"Error: Path {path} does not exist.")
        return

    print(f"Scanning: {path}...")
    
    file_list = []
    # 建立用于断点续传的本地缓存字典 (Path -> Info)
    cache = {}
    output_file = root_path / "scan_results.json"
    
    # 尝试加载先前的扫描结果
    if output_file.exists():
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                old_results = json.load(f)
                for item in old_results:
                    if "path" in item:
                        cache[item["path"]] = item
            print(f"Loaded {len(cache)} existing records from {output_file} cache.")
        except Exception as e:
            print(f"Failed to load existing cache: {e}")

    try:
        for root, dirs, files in os.walk(root_path):
            # Filter ignored directories in-place
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for name in files:
                file_path = Path(root) / name
                str_path = str(file_path)
                
                try:
                    stat = file_path.stat()
                    modified_iso = datetime.fromtimestamp(stat.st_mtime).isoformat()
                    
                    # 断点续传逻辑判断：如果文件存在于缓存中，且修改时间和大小没变，直接复用
                    if str_path in cache:
                        cached_item = cache[str_path]
                        if cached_item.get("modified") == modified_iso and cached_item.get("size") == stat.st_size:
                            file_list.append(cached_item)
                            continue # 跳过重新构建及后续哈希计算
                            
                    file_info = {
                        "path": str_path,
                        "name": name,
                        "size": stat.st_size,
                        "type": file_path.suffix.lower(),
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "modified": modified_iso
                    }
                    
                    if calculate_hash:
                        file_info["hash"] = get_file_hash(file_path)
                    
                    file_list.append(file_info)
                    
                except Exception as e:
                    print(f"Skipping {name}: {e}")

    except KeyboardInterrupt:
        print("\n[Interrupt] Scan was manually stopped. Saving current progress...")
    
    # Save results (包括正常结束和异常中断都会执行到这里保存结果)
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(file_list, f, indent=2, ensure_ascii=False)
        print(f"Scan complete. Found {len(file_list)} files.")
        print(f"Results saved to: {output_file}")
    except Exception as e:
        # If write fails (e.g. permission), try explicit workspace path
        fallback = Path("F:/File_Commander/scan_results.json")
        with open(fallback, 'w', encoding='utf-8') as f:
            json.dump(file_list, f, indent=2, ensure_ascii=False)
        print(f"Scan complete. Results saved to: {fallback} (due to write error at target)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scan directories for files.")
    parser.add_argument("paths", nargs='+', help="Paths or Drive letters to scan (e.g. J: F:\\Data)")
    parser.add_argument("--hash", action="store_true", help="Calculate SHA-256 hash (slow)")
    
    args = parser.parse_args()
    
    for path in args.paths:
        scan_directory(path, args.hash)
