"""
detect_errors Tool Implementation
Orchestrates all 5 detection engines:
  1. Salesforce LogAI (ML-based parsing + anomaly detection)
  2. FlashText (fast keyword scanning)
  3. PyOD Isolation Forest (statistical outlier detection)
  4. Regex patterns (known error signatures)
  5. DeepLog LSTM (deep learning sequence anomaly detection)
"""

import json
from typing import Any

from mcp_server.detectors.logai_detector import LogAIDetector
from mcp_server.detectors.keyword_detector import KeywordDetector
from mcp_server.detectors.anomaly_detector import AnomalyDetector
from mcp_server.detectors.pattern_detector import PatternDetector
from mcp_server.detectors.deeplog_detector import DeepLogDetector


def detect_errors(log_content: str, sensitivity: str = "medium") -> str:
    """
    Detect errors, anomalies, and security issues in system logs.

    This tool uses 5 detection engines:
    - Salesforce LogAI (PRIMARY): ML-based anomaly detection with log parsing
    - FlashText: Fast keyword scanning for error/warning/security terms
    - PyOD: Statistical outlier detection using Isolation Forest
    - Regex patterns: Known error signature matching (stack traces, HTTP errors, etc.)
    - DeepLog LSTM: Deep learning sequence anomaly detection (trains on the log itself)

    Args:
        log_content: The raw log file content as a string.
        sensitivity: Detection sensitivity level - "low", "medium", or "high".
                     Higher sensitivity may produce more false positives.

    Returns:
        JSON string with detected errors, anomalies, and severity distribution.
    """
    log_lines = log_content.strip().split("\n")
    if not log_lines:
        return json.dumps({"error": "No log content provided", "errors": []})

    contamination = {"low": 0.01, "medium": 0.05, "high": 0.10}.get(sensitivity, 0.05)

    results: dict[str, Any] = {
        "total_lines": len(log_lines),
        "sensitivity": sensitivity,
    }

    # Engine 1: Salesforce LogAI (PRIMARY)
    logai = LogAIDetector()
    results["logai_analysis"] = logai.detect(log_lines)

    # Engine 2: FlashText keyword detection
    keyword_det = KeywordDetector()
    results["keyword_detection"] = keyword_det.detect(log_lines)

    # Engine 3: PyOD anomaly detection
    anomaly_det = AnomalyDetector(contamination=contamination)
    results["anomaly_detection"] = anomaly_det.detect(log_lines)

    # Engine 4: Regex pattern matching
    pattern_det = PatternDetector()
    results["pattern_detection"] = pattern_det.detect(log_lines)

    # Engine 5: DeepLog LSTM (deep learning sequence anomaly detection)
    deeplog_top_k = {"low": 12, "medium": 9, "high": 5}.get(sensitivity, 9)
    deeplog = DeepLogDetector(window_size=10, top_k=deeplog_top_k, num_epochs=30)
    results["deeplog_detection"] = deeplog.detect(log_lines)

    # Merge severity distributions
    merged_severity = {"critical": 0, "error": 0, "warning": 0, "info": 0}
    for engine_key in ["keyword_detection", "pattern_detection"]:
        engine_data = results.get(engine_key, {})
        dist = engine_data.get("severity_distribution", {})
        for sev, count in dist.items():
            merged_severity[sev] = merged_severity.get(sev, 0) + count

    # Collect all unique error lines from ALL engines
    error_lines: set[int] = set()

    # From keyword + pattern detections (ALL severities, not just critical/error)
    for engine_key in ["keyword_detection", "pattern_detection"]:
        engine_data = results.get(engine_key, {})
        items = engine_data.get("detections", engine_data.get("matches", []))
        for item in items:
            if item.get("severity") in ("critical", "error", "warning"):
                error_lines.add(item.get("line_number", 0))

    # Add LogAI anomalies
    logai_data = results.get("logai_analysis", {})
    for anom in logai_data.get("anomalies", []):
        error_lines.add(anom.get("line_number", 0))

    # Add PyOD statistical anomalies
    pyod_data = results.get("anomaly_detection", {})
    for anom in pyod_data.get("anomalies", []):
        error_lines.add(anom.get("line_number", 0))

    # Add DeepLog sequence anomalies
    deeplog_data = results.get("deeplog_detection", {})
    for anom in deeplog_data.get("anomalies", []):
        error_lines.add(anom.get("line_number", 0))

    # Remove line 0 (invalid) if present
    error_lines.discard(0)

    results["summary"] = {
        "total_issues_found": len(error_lines),
        "severity_distribution": merged_severity,
        "engines_used": ["logai", "flashtext", "pyod", "regex_patterns", "deeplog_lstm"],
        "logai_anomalies": logai_data.get("anomaly_count", 0),
        "keyword_detections": results.get("keyword_detection", {}).get("total_detections", 0),
        "pattern_matches": results.get("pattern_detection", {}).get("total_matches", 0),
        "statistical_anomalies": pyod_data.get("total_anomalies", 0),
        "deeplog_anomalies": deeplog_data.get("anomaly_count", 0),
        "health_assessment": _assess_health(merged_severity, len(log_lines)),
    }

    return json.dumps(results, default=str)


def _assess_health(severity_dist: dict, total_lines: int) -> str:
    """Generate a brief health assessment based on severity distribution."""
    critical = severity_dist.get("critical", 0)
    error = severity_dist.get("error", 0)
    warning = severity_dist.get("warning", 0)

    if critical > 0:
        return "CRITICAL — Immediate attention required. Critical issues detected."
    elif error > total_lines * 0.1:
        return "UNHEALTHY — High error rate detected. Investigation recommended."
    elif error > 0:
        return "DEGRADED — Errors present. Monitor closely."
    elif warning > total_lines * 0.2:
        return "WARNING — Elevated warning rate. Review recommended."
    elif warning > 0:
        return "FAIR — Minor warnings detected."
    else:
        return "HEALTHY — No significant issues detected."
