"""
LogInsight AI — FastAPI Application
Main entry point for the backend server (port 8000).
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import FRONTEND_DIR, UPLOAD_DIR
from backend.routes import logs, analysis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("loginsight")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events."""
    logger.info("🚀 LogInsight AI Backend starting...")
    logger.info(f"📁 Upload directory: {UPLOAD_DIR}")
    logger.info(f"🌐 Frontend served from: {FRONTEND_DIR}")

    # Check MCP server connectivity
    from backend.routes.analysis import _mcp_client
    mcp_ok = await _mcp_client.health_check()
    if mcp_ok:
        logger.info("✅ MCP server connected")
    else:
        logger.warning("⚠️ MCP server not reachable — using direct tool execution fallback")

    yield

    # Cleanup
    await _mcp_client.close()
    logger.info("👋 LogInsight AI Backend shutting down")


# Create FastAPI app
app = FastAPI(
    title="LogInsight AI",
    description="Intelligent Log Analyzer",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(logs.router)
app.include_router(analysis.router)

# Serve frontend static files
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


@app.get("/api/health")
async def health():
    """Global health check."""
    return {"status": "healthy", "service": "LogInsight AI", "version": "1.0.0"}
