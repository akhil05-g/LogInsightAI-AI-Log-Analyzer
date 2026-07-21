"""
LogInsight AI — Pydantic Schemas v2.0
Request/response models for the API.
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class LogUploadResponse(BaseModel):
    """Response after uploading a log file."""
    log_id: str
    filename: str
    line_count: int
    size_bytes: int
    message: str = "File uploaded successfully"


class SampleLogInfo(BaseModel):
    """Info about a sample log file."""
    name: str
    display_name: str
    size_bytes: int
    line_count: int


class AnalysisRequest(BaseModel):
    """Request to analyze a log file."""
    log_id: str
    analysis_type: str = Field(default="full", pattern="^(full|parse|detect)$")
    sensitivity: str = Field(default="medium", pattern="^(low|medium|high)$")
    log_format: str = Field(default="auto")


class AnalysisResponse(BaseModel):
    """Full analysis response v2.0."""
    analysis_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    log_id: str
    analysis_type: str
    parse_result: Optional[dict] = None
    detection_result: Optional[dict] = None
    correlation_result: Optional[dict] = None
    prediction_result: Optional[dict] = None
    compliance_result: Optional[dict] = None
    ai_summary: Optional[str] = None
    issue_explanations: Optional[list[dict]] = None
    engines_used: list[str] = Field(default_factory=list)
    timing: dict[str, float] = Field(default_factory=dict)
    status: str = "completed"
    error: Optional[str] = None


class CompareRequest(BaseModel):
    """Request to compare two log analyses."""
    log_id_a: str
    log_id_b: str
    analysis_type: str = Field(default="full", pattern="^(full|parse|detect)$")
    sensitivity: str = Field(default="medium", pattern="^(low|medium|high)$")
