from huggingface_hub import hf_hub_download
import os
import argparse

MODELS = {
    "qwen-0.5b": ("bartowski/Qwen2.5-0.5B-Instruct-GGUF", "Qwen2.5-0.5B-Instruct-Q4_K_M.gguf"),
    "qwen-7b": ("bartowski/Qwen2.5-7B-Instruct-GGUF", "Qwen2.5-7B-Instruct-Q4_K_M.gguf"),
    "llama3-8b": ("bartowski/Meta-Llama-3-8B-Instruct-GGUF", "Meta-Llama-3-8B-Instruct-Q4_K_M.gguf"),
    "mistral-7b": ("bartowski/Mistral-7B-Instruct-v0.3-GGUF", "Mistral-7B-Instruct-v0.3-Q4_K_M.gguf"),
    "gemma-2b": ("bartowski/gemma-2-2b-it-GGUF", "gemma-2-2b-it-Q4_K_M.gguf")
}

def download_model(key):
    if key not in MODELS:
        print(f"Unknown model key: {key}")
        return
    
    repo_id, filename = MODELS[key]
    print(f"Downloading {filename} from {repo_id}...")
    try:
        path = hf_hub_download(
            repo_id=repo_id, 
            filename=filename, 
            local_dir="models", 
            local_dir_use_symlinks=False
        )
        print(f"Model downloaded to: {path}")
    except Exception as e:
        print(f"Download failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download top-tier local models.")
    parser.add_argument("model", choices=MODELS.keys(), help="Model to download")
    args = parser.parse_args()
    
    download_model(args.model)
