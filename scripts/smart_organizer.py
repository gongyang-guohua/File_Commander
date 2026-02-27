import os
import shutil
import pathlib
import argparse
from openai import OpenAI
import pypdf
import docx

# 配置本地 LLM 客户端
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="sk-no-key-required"
)

def read_file_content(file_path):
    """读取文件内容 (支持 .txt, .md, .py, .pdf, .docx)"""
    file_path = pathlib.Path(file_path)
    suffix = file_path.suffix.lower()
    
    try:
        if suffix in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.yml', '.yaml']:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()[:2000]  # 读取前 2000 字符用于分析
        
        elif suffix == '.pdf':
            try:
                reader = pypdf.PdfReader(file_path)
                text = ""
                for page in reader.pages[:2]: # 只读前2页
                    text += page.extract_text()
                return text[:2000]
            except Exception as e:
                print(f"Error reading PDF {file_path}: {e}")
                return None
                
        elif suffix == '.docx':
            try:
                doc = docx.Document(file_path)
                text = "\n".join([para.text for para in doc.paragraphs])
                return text[:2000]
            except Exception as e:
                print(f"Error reading DOCX {file_path}: {e}")
                return None
        
        else:
            return None # 不支持的格式
            
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def analyze_and_rename(file_path, dry_run=False):
    """分析文件内容并返回建议的分类与文件名"""
    content = read_file_content(file_path)
    if not content:
        print(f"Skipping {file_path}: Unsupported content or empty.")
        return

    original_name = os.path.basename(file_path)
    
    prompt = f"""
    You are a professional file organizer. Analyze the following file content and suggest a category folder and a new descriptive filename.
    
    Rules:
    1. Reply ONLY in the format: category/new_filename.ext
    2. Keep the original extension.
    3. Use English or Chinese for names, but keep it concise.
    4. Category should be a short noun (e.g., Finance, Code, Research, Personal).
    5. Filename should be descriptive but concise, using underscores for spaces (e.g., invoice_2023.pdf).
    
    File Content (snippet):
    {content}
    """

    try:
        response = client.chat.completions.create(
            model="local-model", # 模型名在这里不重要，因为是本地单模型服务
            messages=[
                {"role": "system", "content": "You are a helpful file organization assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        suggestion = response.choices[0].message.content.strip()
        
        # 简单的清理与验证
        if "/" not in suggestion:
            # 如果 LLM 没按格式返回，尝试修复
            category = "Uncategorized"
            new_name = suggestion
        else:
            parts = suggestion.split('/')
            category = parts[0].strip()
            new_name = parts[-1].strip()
            
        # 确保文件名安全
        safe_name = "".join([c for c in new_name if c.isalnum() or c in (' ', '.', '_', '-')]).strip()
        safe_category = "".join([c for c in category if c.isalnum() or c in (' ', '_', '-')]).strip()
        
        # 构造新路径
        target_dir = os.path.join(os.path.dirname(file_path), safe_category)
        target_path = os.path.join(target_dir, safe_name)
        
        print(f"[Analyze] {original_name} -> {safe_category}/{safe_name}")
        
        if not dry_run:
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            # 处理重名
            if os.path.exists(target_path):
                base, ext = os.path.splitext(target_path)
                import time
                target_path = f"{base}_{int(time.time())}{ext}"
                
            shutil.move(file_path, target_path)
            print(f"Moved to: {target_path}")
            
    except Exception as e:
        print(f"API Error or processing failed for {file_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Smart File Organizer powered by Local LLM")
    parser.add_argument("directory", help="Directory to organize")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without moving files")
    args = parser.parse_args()
    
    target_dir = args.directory
    if not os.path.exists(target_dir):
        print(f"Directory not found: {target_dir}")
        return
        
    print(f"Scanning directory: {target_dir}...")
    for root, dirs, files in os.walk(target_dir):
        # 跳过已生成的分类文件夹 (简单的防递归逻辑，可根据需要增强)
        if root != target_dir: 
            continue 
            
        for file in files:
            file_path = os.path.join(root, file)
            # 跳过脚本自身和一些系统文件
            if file == "smart_organizer.py" or file.startswith("."):
                continue
                
            analyze_and_rename(file_path, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
