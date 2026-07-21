"""
LogInsight AI — Analysis Routes v2.0
Endpoints for log analysis (parse, detect, full AI analysis, compare).
"""

import logging
from fastapi import APIRouter, HTTPException

from backend.models.schemas import AnalysisRequest, AnalysisResponse, CompareRequest
from backend.services.mcp_client import MCPClient
from backend.services.llm_orchestrator import LLMOrchestrator
from backend.routes.logs import get_log_content
from backend.config import MCP_SERVER_URL

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analysis", tags=["analysis"])

# Shared service instances
_mcp_client = MCPClient(server_url=MCP_SERVER_URL)
_orchestrator = LLMOrchestrator(mcp_client=_mcp_client)


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_log(request: AnalysisRequest):
    """
    Run full analysis pipeline on a log file.

    analysis_type options:
    - "full": Parse + Detect (5 engines) + Correlate + Predict + Compliance + AI Summary
    - "parse": Parse only (no LLM, no detection)
    - "detect": Detect only (5 engines, no LLM, no parsing)
    """
    try:
        log_content = get_log_content(request.log_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(404, f"Could not read log: {str(e)}")

    try:
        result = await _orchestrator.analyze(
            log_content=log_content,
            analysis_type=request.analysis_type,
            sensitivity=request.sensitivity,
            log_format=request.log_format,
        )

        return AnalysisResponse(
            log_id=request.log_id,
            analysis_type=request.analysis_type,
            parse_result=result.get("parse_result"),
            detection_result=result.get("detection_result"),
            correlation_result=result.get("correlation_result"),
            prediction_result=result.get("prediction_result"),
            compliance_result=result.get("compliance_result"),
            ai_summary=result.get("ai_summary"),
            issue_explanations=result.get("issue_explanations"),
            engines_used=result.get("engines_used", []),
            timing=result.get("timing", {}),
            status="completed",
        )

    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return AnalysisResponse(
            log_id=request.log_id,
            analysis_type=request.analysis_type,
            status="error",
            error=str(e),
        )


@router.post("/compare")
async def compare_logs(request: CompareRequest):
    """
    Compare analysis results between two log files.
    Useful for before/after deployment comparisons.
    """
    try:
        content_a = get_log_content(request.log_id_a)
        content_b = get_log_content(request.log_id_b)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(404, f"Could not read logs: {str(e)}")

    # Run analysis on both
    result_a = await _orchestrator.analyze(
        log_content=content_a,
        analysis_type=request.analysis_type,
        sensitivity=request.sensitivity,
    )
    result_b = await _orchestrator.analyze(
        log_content=content_b,
        analysis_type=request.analysis_type,
        sensitivity=request.sensitivity,
    )

    # Build comparison
    def _get_issue_count(r):
        det = r.get("detection_result", {}) or {}
        summary = det.get("summary", {})
        return summary.get("total_issues_found", 0)

    def _get_health(r):
        det = r.get("detection_result", {}) or {}
        summary = det.get("summary", {})
        return summary.get("health_assessment", "UNKNOWN")

    return {
        "log_a": {
            "log_id": request.log_id_a,
            "issues_found": _get_issue_count(result_a),
            "health": _get_health(result_a),
            "engines_used": result_a.get("engines_used", []),
        },
        "log_b": {
            "log_id": request.log_id_b,
            "issues_found": _get_issue_count(result_b),
            "health": _get_health(result_b),
            "engines_used": result_b.get("engines_used", []),
        },
        "comparison": {
            "issue_delta": _get_issue_count(result_b) - _get_issue_count(result_a),
            "health_changed": _get_health(result_a) != _get_health(result_b),
        },
    }


@router.get("/health")
async def analysis_health():
    """Check analysis service health (MCP server connectivity)."""
    mcp_healthy = await _mcp_client.health_check()
    return {
        "status": "healthy" if mcp_healthy else "degraded",
        "mcp_server": "connected" if mcp_healthy else "disconnected",
        "mcp_url": MCP_SERVER_URL,
        "version": "2.0.0",
        "tools_available": [
            "parse_logs", "detect_errors", "correlate_events",
            "predict_failures", "generate_report"
        ],
        "detection_engines": [
            "logai", "flashtext", "pyod", "regex_patterns", "deeplog_lstm"
        ],
    }
