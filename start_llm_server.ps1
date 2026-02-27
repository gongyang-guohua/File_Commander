$ModelPath = "models\Qwen2.5-7B-Instruct-Q4_K_M.gguf"

if (-not (Test-Path $ModelPath)) {
    Write-Error "Model file not found at $ModelPath. Please check the path."
    exit 1
}

Write-Host "Starting Local LLM Server with model: $ModelPath"
Write-Host "API will be available at http://localhost:8000/v1"
Write-Host "Press Ctrl+C to stop the server."

python -m llama_cpp.server --model $ModelPath --n_gpu_layers -1 --host 0.0.0.0 --port 8001
