"""
LogInsight AI — FastAPI Application
Main entry point for the backend server.

On Render: MCP tools run in-process via mounted SSE app (single port).
Locally:   Connects to separate MCP server on port 8001.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import FRONTEND_DIR, UPLOAD_DIR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("loginsight")


def _mount_mcp(app: FastAPI):
    """Mount MCP server SSE transport directly into FastAPI (single-process mode)."""
    try:
        from mcp_server.server import mcp as mcp_server
        mcp_sse = mcp_server.sse_app()
        app.mount("/mcp", mcp_sse)
        logger.info("✅ MCP server mounted in-process at /mcp")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Could not mount MCP in-process: {e}")
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle events."""
    logger.info("🚀 LogInsight AI Backend starting...")
    logger.info(f"📁 Upload directory: {UPLOAD_DIR}")
    logger.info(f"🌐 Frontend served from: {FRONTEND_DIR}")

    # Check MCP server connectivity (external or in-process)
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

# Mount MCP SSE app in-process (for Render single-port deployment)
_mount_mcp(app)

# Include API routers
from backend.routes import logs, analysis
app.include_router(logs.router)
app.include_router(analysis.router)

# Serve frontend static files
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


@app.get("/api/health")
async def health():
    """Global health check."""
    return {"status": "healthy", "service": "LogInsight AI", "version": "1.0.0"}

