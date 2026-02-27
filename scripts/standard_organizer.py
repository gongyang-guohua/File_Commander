import os
import shutil
import hashlib
import pathlib
import argparse
import re
from openai import OpenAI
import pypdf
import time

# 配置本地 LLM 客户端
client = OpenAI(
    base_url="http://localhost:8001/v1",
    api_key="sk-no-key-required"
)

def calculate_file_hash(file_path, algorithm='md5'):
    """Calculate file hash for deduplication."""
    hash_func = hashlib.new(algorithm)
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        print(f"Error calculating hash for {file_path}: {e}")
        return None

def read_file_content(file_path):
    """读取文件内容 (优先 PDF)"""
    file_path = pathlib.Path(file_path)
    suffix = file_path.suffix.lower()
    
    try:
        if suffix == '.pdf':
            try:
                reader = pypdf.PdfReader(file_path)
                text = ""
                # 读取前几页通常包含标准号和标题
                for page in reader.pages[:3]: 
                    text += page.extract_text()
                return text[:5000] # 限制长度
            except Exception as e:
                print(f"Error reading PDF {file_path}: {e}")
                return None
        elif suffix in ['.txt', '.md']:
             with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()[:2000]
        else:
            return None # 暂不支持其他格式
            
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def analyze_standard(file_path, content):
    """Use LLM to extract Standard Number, Year, and Full Title."""
    filename = os.path.basename(file_path)
    
    prompt = f"""
    You are a professional documentation specialist. Extract the Standard Number, Year, Full Title, and Organization from the following document content or filename.
    
    Current Filename: {filename}
    Document Content Snippet:
    {content}
    
    Rules:
    1. Reply ONLY with a JSON object. No markdown formatting.
    2. JSON format: {{"organization": "API", "number": "API 650", "year": "2020", "title": "Welded Tanks for Oil Storage"}}
    3. Organization should be one of: API, ASME, ISO, GB, ASTM, NACE, NFPA, HG, SH, etc. If unknown, use "Others".
    4. "number" should be comprehensive (e.g., "GB/T 1234.5").
    5. "title" should be the full descriptive title, excluding the number and year.
    6. If year is not found, use "Unknown".
    
    JSON:
    """

    try:
        response = client.chat.completions.create(
            model="local-model",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts structured data from text."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1, # Low temperature for consistency
            response_format={"type": "json_object"}
        )
        
        import json
        result = json.loads(response.choices[0].message.content)
        return result
    except Exception as e:
        print(f"LLM extraction failed for {file_path}: {e}")
        return None

def standardize_name(info):
    """Format: StandardNumber_Year_FullTitle"""
    # Clean up fields
    number = re.sub(r'[\\/:*?"<>|]', '_', info.get('number', 'Unknown'))
    year = re.sub(r'[\\/:*?"<>|]', '', str(info.get('year', 'Unknown')))
    title = re.sub(r'[\\/:*?"<>|]', '_', info.get('title', 'UnknownTitle'))
    
    # 限制标题长度防止文件名过长
    if len(title) > 100:
        title = title[:100] + "..."
        
    return f"{number}_{year}_{title}"

def main():
    parser = argparse.ArgumentParser(description="Organize Standard Documents")
    parser.add_argument("directory", help="Target directory (e.g., J:\\规范(kk))")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes")
    args = parser.parse_args()
    
    root_dir = args.directory
    if not os.path.exists(root_dir):
        print(f"Directory not found: {root_dir}")
        return

    # 1. Deduplication using Hash
    print("Step 1: Scanning for duplicates...")
    file_hashes = {}
    duplicates = []
    
    # 遍历所有文件 (包括子目录)
    all_files = []
    for root, dirs, files in os.walk(root_dir):
        # 排除已整理的文件夹以防止重复处理 (如果需要可以调整)
        # 这里建议全部扫描一遍，统一整理
        for file in files:
            path = os.path.join(root, file)
            all_files.append(path)
            
    print(f"Found {len(all_files)} files. Calculating hashes...")
    
    count = 0
    for path in all_files:
        count += 1
        if count % 100 == 0:
            print(f"Processed {count}/{len(all_files)} hashes...")
            
        file_hash = calculate_file_hash(path)
        if not file_hash:
            continue
            
        if file_hash in file_hashes:
            duplicates.append((path, file_hashes[file_hash])) # (duplicate, original)
        else:
            file_hashes[file_hash] = path
            
    print(f"Found {len(duplicates)} duplicates.")
    
    # Handle duplicates
    dup_dir = os.path.join(root_dir, "_Duplicates")
    if not args.dry_run and duplicates:
        os.makedirs(dup_dir, exist_ok=True)
        
    for dup_path, orig_path in duplicates:
        print(f"[Duplicate] {dup_path} is a copy of {orig_path}")
        if not args.dry_run:
            try:
                # 移动到 _Duplicates 而不是直接删除，比较安全
                fname = os.path.basename(dup_path)
                shutil.move(dup_path, os.path.join(dup_dir, f"{int(time.time())}_{fname}"))
            except Exception as e:
                print(f"Failed to move duplicate {dup_path}: {e}")

    # 2. Organize remaining files
    print("\nStep 2: Organizing files...")
    organized_files = list(file_hashes.values()) # Only unique files
    
    for file_path in organized_files:
        # 跳过我们刚刚创建的 _Duplicates 文件夹
        if "_Duplicates" in file_path:
            continue
            
        # 跳过非文档 (Images, etc. if needed)
        suffix = pathlib.Path(file_path).suffix.lower()
        if suffix not in ['.pdf', '.doc', '.docx', '.txt']:
             # 对于不支持的文件，可以暂时跳过或移动到 Others
             continue

        content = read_file_content(file_path)
        if not content:
            print(f"[Skip] No content extracted: {file_path}")
            continue
            
        print(f"Analyzing: {os.path.basename(file_path)}...")
        info = analyze_standard(file_path, content)
        
        if not info:
            print(f"[Fail] LLM analysis failed for {file_path}")
            continue
            
        org_name = info.get('organization', 'Others').upper()
        # 简单的标准化组织名
        if 'API' in org_name: org_name = 'API'
        elif 'ASME' in org_name: org_name = 'ASME'
        elif 'ISO' in org_name: org_name = 'ISO'
        elif 'GB' in org_name: org_name = 'GB'
        elif 'ASTM' in org_name: org_name = 'ASTM'
        
        new_filename = standardize_name(info) + suffix
        
        # Target path
        target_folder = os.path.join(root_dir, org_name)
        target_path = os.path.join(target_folder, new_filename)
        
        print(f"[Move] {os.path.basename(file_path)} -> {org_name}/{new_filename}")
        
        if not args.dry_run:
            os.makedirs(target_folder, exist_ok=True)
            if file_path != target_path: # 防止原地移动
                try:
                    # 处理目标文件名冲突
                    if os.path.exists(target_path) and calculate_file_hash(target_path) != calculate_file_hash(file_path):
                         base, ext = os.path.splitext(target_path)
                         target_path = f"{base}_{int(time.time())}{ext}"
                    
                    shutil.move(file_path, target_path)
                except Exception as e:
                    print(f"Error moving {file_path}: {e}")

if __name__ == "__main__":
    main()
