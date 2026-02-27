import os
import argparse
import time
from pathlib import Path
from llama_cpp import Llama

# Configuration
MODEL_PATH = r"F:\File_Commander\models\Qwen2.5-0.5B-Instruct-Q4_K_M.gguf"

# Initialize Local LLM
# Check if model exists
if not os.path.exists(MODEL_PATH):
    print(f"Model not found at {MODEL_PATH}. Please run download_model.py first.")
    exit(1)

print(f"Loading local model: {MODEL_PATH}...")
try:
    llm = Llama(
        model_path=MODEL_PATH,
        n_ctx=8192,
        n_threads=4, # Adjust based on CPU
        verbose=True # Enable verbose logging for debugging
    )
except Exception as e:
    print(f"Failed to load model: {e}")
    exit(1)

import pypdf
import docx

# ... (Configuration and LLM init remains same)

def get_file_content(filepath, max_chars=2000):
    """Reads file content using native python libs."""
    path_str = str(filepath).lower()
    
    try:
        # PDF
        if path_str.endswith('.pdf'):
            try:
                reader = pypdf.PdfReader(filepath)
                text = ""
                for page in reader.pages[:3]: # Read first 3 pages max
                    text += page.extract_text() + "\n"
                return text[:max_chars]
            except Exception as e:
                return f"[PDF Error: {e}]"

        # DOCX
        if path_str.endswith('.docx'):
            try:
                doc = docx.Document(filepath)
                text = "\n".join([para.text for para in doc.paragraphs])
                return text[:max_chars]
            except Exception as e:
                return f"[DOCX Error: {e}]"
        
        # DOC (Legacy) - Hard to read perfectly without win32com, skip or try heuristic
        if path_str.endswith('.doc'):
            try:
                # Basic string extraction for binary files (strings command equivalent)
                with open(filepath, 'rb') as f:
                     data = f.read()
                     # Filter for printable ascii or strict utf-8
                     text = "".join(chr(b) for b in data if 32 <= b <= 126 or b > 128) 
                     # This is very rough, but better than nothing for .doc headers
                     return text[:max_chars]
            except Exception:
                return "[DOC Binary/Unreadable]"

        # Default Text
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read(max_chars)
        except Exception:
            return "[Binary/Unreadable]"
            
    except Exception as e:
        return f"[Error: {e}]"

def suggest_name(content):
    """Asks Local LLM for a filename suggestion."""
    if not content or content.startswith("["):
        return None

    prompt_messages = [
        {"role": "system", "content": "You are a file naming assistant. Suggest a concise and descriptive CHINESE filename for the content provided by the user. Use underscores for separators. Return ONLY the filename base (WITHOUT extension). For example: 项目汇报_2023. No markdown, no explanations."},
        {"role": "user", "content": f"Content snippet:\n{content}\n\nSuggest a concise Chinese filename (no extension):"}
    ]

    try:
        response = llm.create_chat_completion(
            messages=prompt_messages,
            max_tokens=64,
            temperature=0.3
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return None

def process_file(filepath, apply=False):
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}")
        return

    print(f"Analyzing: {path.name}...")
    content = get_file_content(path)
    if not content or content.startswith("["):
        print(f"  Skipping: {content}")
        return

    new_name_base = suggest_name(content)
    if not new_name_base:
        print("  Skipping: No suggestion generated.")
        return

    import re
    # Clean up response (remove quotes, extra spaces)
    new_name_base = new_name_base.replace('"', '').replace("'", "").replace("`", "").strip()
    
    # Validation: Reject meaningless names
    bad_keywords = ["uni00", "Times New Roman", "Arial", "Calibri", "SimSun", "宋体", "黑体"]
    if any(k in new_name_base for k in bad_keywords) or len(new_name_base) < 2:
        print(f"  Skipping: Rejected meaningless suggestion '{new_name_base}'")
        return

    # Remove invalid characters for Windows filenames
    new_name_base = re.sub(r'[<>:"/\\|?*]', '_', new_name_base)
    
    # Strip common extensions if LLM successfully hallucinated them despite instructions
    lower_base = new_name_base.lower()
    for ext in ['.docx', '.doc', '.pdf', '.txt']:
        if lower_base.endswith(ext):
            new_name_base = new_name_base[:-len(ext)]
            break # Just remove the first matching one at the end
    
    new_name = new_name_base + path.suffix

    if new_name == path.name:
        print("  No change needed.")
        return

    print(f"  Suggestion: {new_name}")
    
    if apply:
        new_path = path.with_name(new_name)
        if new_path.exists():
            print(f"  Cannot rename: {new_name} already exists.")
        else:
            try:
                path.rename(new_path)
                print(f"  Renamed to: {new_name}")
            except Exception as e:
                print(f"  Rename failed: {e}")
    else:
        print("  (Run with --apply to rename)")

def process_directory(dirpath, apply=False):
    path = Path(dirpath)
    for item in path.iterdir():
        if item.is_file() and item.name != 'rename.py':
            process_file(item, apply)
            # No sleep needed for local LLM!

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rename files using Local AI (Qwen).")
    parser.add_argument("--dir", required=True, help="Directory to process")
    parser.add_argument("--apply", action="store_true", help="Apply changes")
    args = parser.parse_args()

    process_directory(args.dir, args.apply)
