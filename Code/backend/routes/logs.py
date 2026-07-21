"""
LogInsight AI — Log Management Routes
Upload, list, and manage log files.
"""

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from backend.config import UPLOAD_DIR, SAMPLE_LOGS_DIR, MAX_LOG_LINES
from backend.models.schemas import LogUploadResponse, SampleLogInfo

router = APIRouter(prefix="/api/logs", tags=["logs"])

# In-memory store for uploaded log metadata
_uploaded_logs: dict[str, dict] = {}


@router.post("/upload", response_model=LogUploadResponse)
async def upload_log(file: UploadFile = File(...)):
    """Upload a log file for analysis."""
    if not file.filename:
        raise HTTPException(400, "No filename provided")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(413, "File too large (max 10 MB)")

    text = content.decode("utf-8", errors="replace")
    lines = text.strip().split("\n")

    log_id = str(uuid.uuid4())[:8]
    file_path = UPLOAD_DIR / f"{log_id}_{file.filename}"

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)

    _uploaded_logs[log_id] = {
        "filename": file.filename,
        "path": str(file_path),
        "line_count": len(lines),
        "size_bytes": len(content),
    }

    return LogUploadResponse(
        log_id=log_id,
        filename=file.filename,
        line_count=len(lines),
        size_bytes=len(content),
    )


@router.get("/samples", response_model=list[SampleLogInfo])
async def list_samples():
    """List available sample log files."""
    samples = []
    if SAMPLE_LOGS_DIR.exists():
        for f in sorted(SAMPLE_LOGS_DIR.iterdir()):
            if f.suffix == ".log":
                content = f.read_text(encoding="utf-8", errors="replace")
                lines = content.strip().split("\n")
                display = f.stem.replace("_", " ").replace("sample", "").strip().title()
                samples.append(SampleLogInfo(
                    name=f.name,
                    display_name=display,
                    size_bytes=f.stat().st_size,
                    line_count=len(lines),
                ))
    return samples


@router.get("/samples/{name}")
async def load_sample(name: str):
    """Load a sample log file and return its content + auto-generated log_id."""
    file_path = SAMPLE_LOGS_DIR / name
    if not file_path.exists() or not file_path.suffix == ".log":
        raise HTTPException(404, f"Sample log '{name}' not found")

    content = file_path.read_text(encoding="utf-8", errors="replace")
    lines = content.strip().split("\n")

    log_id = f"sample_{name.replace('.log', '')}"
    _uploaded_logs[log_id] = {
        "filename": name,
        "path": str(file_path),
        "line_count": len(lines),
        "size_bytes": file_path.stat().st_size,
    }

    return {
        "log_id": log_id,
        "filename": name,
        "content": content,
        "line_count": len(lines),
    }


@router.get("/{log_id}")
async def get_log(log_id: str):
    """Get raw log content by ID."""
    if log_id not in _uploaded_logs:
        raise HTTPException(404, f"Log '{log_id}' not found")

    meta = _uploaded_logs[log_id]
    path = Path(meta["path"])
    if not path.exists():
        raise HTTPException(404, "Log file no longer exists on disk")

    content = path.read_text(encoding="utf-8", errors="replace")
    lines = content.strip().split("\n")

    # Truncate if too many lines
    if len(lines) > MAX_LOG_LINES:
        lines = lines[:MAX_LOG_LINES]
        content = "\n".join(lines) + f"\n\n... [TRUNCATED: showing {MAX_LOG_LINES} of {meta['line_count']} lines]"

    return {
        "log_id": log_id,
        "filename": meta["filename"],
        "content": content,
        "line_count": len(lines),
        "total_lines": meta["line_count"],
    }


@router.delete("/{log_id}")
async def delete_log(log_id: str):
    """Delete an uploaded log file."""
    if log_id not in _uploaded_logs:
        raise HTTPException(404, f"Log '{log_id}' not found")

    meta = _uploaded_logs.pop(log_id)
    path = Path(meta["path"])
    if path.exists() and str(UPLOAD_DIR) in str(path):
        path.unlink()

    return {"message": f"Log '{log_id}' deleted", "filename": meta["filename"]}


def get_log_content(log_id: str) -> str:
    """Helper: get log content by ID (used by analysis routes)."""
    if log_id not in _uploaded_logs:
        raise HTTPException(404, f"Log '{log_id}' not found")

    meta = _uploaded_logs[log_id]
    path = Path(meta["path"])
    if not path.exists():
        raise HTTPException(404, "Log file no longer exists on disk")

    return path.read_text(encoding="utf-8", errors="replace")
