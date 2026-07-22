"""
LogInsight AI — Configuration v2.0
Loads settings from .env file and environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
UPLOAD_DIR = PROJECT_ROOT / os.getenv("UPLOAD_DIR", "uploads")
SAMPLE_LOGS_DIR = PROJECT_ROOT / "sample_logs"
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Ensure upload directory exists
UPLOAD_DIR.mkdir(exist_ok=True)

# Google Cloud API Key (Vertex AI)
GOOGLE_CLOUD_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Groq Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq").lower()

# MCP Server Configuration
MCP_SERVER_HOST = os.getenv("MCP_SERVER_HOST", "127.0.0.1")
MCP_SERVER_PORT = int(os.getenv("MCP_SERVER_PORT", "8001"))
MCP_SERVER_URL = f"http://{MCP_SERVER_HOST}:{MCP_SERVER_PORT}"

# Backend Configuration
# On Render, PORT is provided dynamically; bind to 0.0.0.0 for external access
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("PORT", os.getenv("BACKEND_PORT", "8000")))

# Render detection
IS_RENDER = os.getenv("RENDER", "").lower() in ("true", "1")

# Application Settings
MAX_LOG_LINES = int(os.getenv("MAX_LOG_LINES", "5000"))
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB

# DeepLog LSTM Configuration
DEEPLOG_ENABLED = os.getenv("DEEPLOG_ENABLED", "true").lower() == "true"
DEEPLOG_WINDOW_SIZE = int(os.getenv("DEEPLOG_WINDOW_SIZE", "10"))
DEEPLOG_TOP_K = int(os.getenv("DEEPLOG_TOP_K", "9"))
DEEPLOG_NUM_EPOCHS = int(os.getenv("DEEPLOG_NUM_EPOCHS", "30"))
