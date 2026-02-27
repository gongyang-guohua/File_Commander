from huggingface_hub import hf_hub_download
import os

model_id = "bartowski/Qwen2.5-0.5B-Instruct-GGUF"
filename = "Qwen2.5-0.5B-Instruct-Q4_K_M.gguf"

print(f"Downloading {filename} from {model_id}...")
try:
    path = hf_hub_download(repo_id=model_id, filename=filename, local_dir="models", local_dir_use_symlinks=False)
    print(f"Model downloaded to: {path}")
except Exception as e:
    print(f"Download failed: {e}")
