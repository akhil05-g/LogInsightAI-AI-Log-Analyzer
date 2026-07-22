#!/usr/bin/env bash
# LogInsight AI — Start script for Render.com
# Launches both MCP server (background) and FastAPI backend (foreground)
set -e

echo "[START] Launching MCP Server on port ${MCP_SERVER_PORT:-8001}..."
python -m mcp_server.server &
MCP_PID=$!
sleep 2

echo "[START] Launching FastAPI Backend on port ${PORT:-8000}..."
uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1

# If uvicorn exits, kill MCP server too
kill $MCP_PID 2>/dev/null
