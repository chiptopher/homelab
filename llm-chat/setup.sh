#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "==> Installing system dependencies..."
brew install cmake poppler

echo "==> Cloning and building llama.cpp..."
if [ ! -d "llama.cpp" ]; then
    git clone https://github.com/ggml-org/llama.cpp
fi
cmake llama.cpp -B llama.cpp/build -DBUILD_SHARED_LIBS=OFF
cmake --build llama.cpp/build --config Release -j --target llama-cli llama-mtmd-cli llama-server

echo "==> Setting up Python environment..."
if [ ! -d "llm-env" ]; then
    python3 -m venv llm-env
fi
source llm-env/bin/activate
pip install -q huggingface_hub hf_transfer openai

echo "==> Downloading Gemma 4 E4B model..."
python3 -c "
from huggingface_hub import snapshot_download
snapshot_download('unsloth/gemma-4-E4B-it-GGUF', local_dir='models/gemma-4-E4B-it-GGUF', allow_patterns='*UD-Q4_K_XL*')
snapshot_download('unsloth/gemma-4-E4B-it-GGUF', local_dir='models/gemma-4-E4B-it-GGUF', allow_patterns='*mmproj*')
"

echo ""
echo "==> Setup complete! Start the server with:"
echo "    $SCRIPT_DIR/start.sh"
