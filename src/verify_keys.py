import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

def test_kimi():
    print("-" * 30)
    print("Testing Kimi (Moonshot)...")
    key = os.getenv("MOONSHOT_API_KEY", "").strip()
    if not key:
        print("MOONSHOT_API_KEY not found.")
        return

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    try:
        resp = requests.get("https://api.moonshot.cn/v1/models", headers=headers)
        if resp.status_code == 200:
            print("Success! Models list retrieved.")
        else:
            print(f"FAILED: Status {resp.status_code}")
            print(f"Response: {resp.text}")
    except Exception as e:
        print(f"Error: {e}")

def test_openai():
    print("-" * 30)
    print("Testing OpenAI (Raw Requests)...")
    raw_key = os.getenv("OPENAI_API_KEY", "")
    key = raw_key.strip()
    
    if not key:
        print("OPENAI_API_KEY not found.")
        return

    print(f"DEBUG: Key Length: {len(key)}")
    print(f"DEBUG: Key Starts With: {key[:10]}...")
    print(f"DEBUG: Key Ends With: ...{key[-10:]}")
    print(f"DEBUG: specific chars check: Isalnum? {key.replace('-', '').replace('_', '').isalnum()}")
    
    # 检查是否有不可见字符
    if len(raw_key) != len(key):
        print(f"WARNING: Key had leading/trailing whitespace! (Original len: {len(raw_key)})")

    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    try:
        # 尝试最基础的模型列表接口
        resp = requests.get("https://api.openai.com/v1/models", headers=headers, timeout=10)
        
        if resp.status_code == 200:
            print("Success! OpenAI API is working.")
            print("First 3 models:", [m['id'] for m in resp.json()['data'][:3]])
        else:
            print(f"FAILED: Status {resp.status_code}")
            print(f"Response: {resp.text}")
            
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    test_kimi()
    test_openai()
