#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

exec "$SCRIPT_DIR/llama.cpp/build/bin/llama-server" \
    --model "$SCRIPT_DIR/models/gemma-4-E4B-it-GGUF/gemma-4-E4B-it-UD-Q4_K_XL.gguf" \
    --mmproj "$SCRIPT_DIR/models/gemma-4-E4B-it-GGUF/mmproj-BF16.gguf" \
    --temp 1.0 --top-p 0.95 --top-k 64 --jinja -c 32768 -ub 1024 \
    --host 0.0.0.0 --port 8080
