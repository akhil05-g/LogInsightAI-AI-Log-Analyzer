#!/usr/bin/env bash
# Render.com build script for LogInsight AI
set -o errexit

echo "=== LogInsight AI Build ==="

# Upgrade pip
python -m pip install --upgrade pip

# Install core dependencies first (these should always work)
echo "=== Installing core dependencies ==="
pip install --no-cache-dir -r requirements.txt

# Install CPU-only PyTorch (optional - DeepLog LSTM engine)
echo "=== Installing PyTorch (CPU-only) ==="
pip install torch --index-url https://download.pytorch.org/whl/cpu --no-cache-dir || {
    echo "WARNING: PyTorch installation failed. DeepLog LSTM engine will be disabled."
}

# Install logai (optional - LogAI ML engine, can be fragile)
echo "=== Installing LogAI (optional) ==="
pip install logai --no-cache-dir || {
    echo "WARNING: LogAI installation failed. LogAI engine will be disabled."
    echo "The other 4 detection engines will still work."
}

echo "=== Build complete ==="
