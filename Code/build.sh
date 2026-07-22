#!/usr/bin/env bash
# Render.com build script for LogInsight AI
set -o errexit

# Upgrade pip
python -m pip install --upgrade pip

# Install CPU-only PyTorch first (much smaller than CUDA version)
pip install torch --index-url https://download.pytorch.org/whl/cpu --no-cache-dir

# Install remaining dependencies
pip install --no-cache-dir -r requirements.txt
