#!/bin/bash
set -e

echo "🚀 Starting cleanup and reinstall process..."

# 1. Remove Hugging Face cache (models)
echo "🧹 Clearing Hugging Face cache..."
rm -rf ~/.cache/huggingface

# 2. Remove pip cache
echo "🧹 Clearing pip cache..."
pip cache purge || true

# 3. Remove heavy GPU PyTorch build if installed
echo "🧹 Uninstalling existing PyTorch (GPU build if present)..."
pip uninstall -y torch torchvision torchaudio || true

# 4. Install CPU‑only PyTorch
echo "⬇️ Installing CPU‑only PyTorch..."
# Install latest CPU-only PyTorch
pip install --no-cache-dir torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cpu

# 5. Move Hugging Face cache to /workspace (more space)
SAFE_CACHE_DIR="/workspace/hf_cache"
echo "📦 Setting Hugging Face cache to $SAFE_CACHE_DIR"
mkdir -p "$SAFE_CACHE_DIR"
export HF_HOME="$SAFE_CACHE_DIR"
export TRANSFORMERS_CACHE="$SAFE_CACHE_DIR"

# 6. Reinstall sentence-transformers without cache
echo "⬇️ Installing sentence-transformers..."
pip install --no-cache-dir sentence-transformers

echo "✅ Cleanup and reinstall complete!"
echo "💡 Remember: Keep HF_HOME and TRANSFORMERS_CACHE set in your scripts to avoid filling up /home."
