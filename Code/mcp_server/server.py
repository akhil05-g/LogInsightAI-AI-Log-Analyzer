"""
LogInsight AI — MCP Server
Separate HTTP server (port 8001) exposing 5 MCP tools:
  1. parse_logs()       — Log parsing & template mining
  2. detect_errors()    — Error/anomaly detection (5 engines incl. DeepLog LSTM)
  3. correlate_events() — Event correlation & cascading failure analysis
  4. predict_failures() — Predictive failure analysis
  5. generate_report()  — Compliance & audit reporting
"""

import sys
import os

# Add project root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from mcp_server.tools.parse_logs import parse_logs as _parse_logs
from mcp_server.tools.detect_errors import detect_errors as _detect_errors
from mcp_server.tools.correlate_events import correlate_events as _correlate_events
from mcp_server.tools.predict_failures import predict_failures as _predict_failures
from mcp_server.tools.generate_report import generate_report as _generate_report

# Initialize MCP server
mcp = FastMCP("LogInsightMCP")


@mcp.tool()
def parse_logs(log_content: str, log_format: str = "auto") -> str:
    """
    Parse system log content to extract structured information, templates, and statistics.

    Uses multiple parsing engines: Drain3 template mining, Grok pattern matching,
    JSON parsing, and regex-based extraction. Automatically detects the log format.

    Args:
        log_content: The raw log file content as a string.
        log_format: Expected format - "auto", "syslog", "apache_access", "apache_error",
                    "hdfs", "zookeeper", "json", or "general_timestamp".

    Returns:
        JSON string with parsed templates, structured entries, format info, and statistics.
    """
    return _parse_logs(log_content, log_format)


@mcp.tool()
def detect_errors(log_content: str, sensitivity: str = "medium") -> str:
    """
    Detect errors, anomalies, and security issues in system logs.

    Uses 5 detection engines:
    - Salesforce LogAI: ML-based anomaly detection (primary engine)
    - FlashText: Fast keyword scanning for error/warning/security terms
    - PyOD Isolation Forest: Statistical outlier detection
    - Regex patterns: Known error signatures (stack traces, HTTP errors, connection issues)
    - DeepLog LSTM: Deep learning sequence anomaly detection (self-supervised)

    Args:
        log_content: The raw log file content as a string.
        sensitivity: Detection sensitivity - "low", "medium", or "high".

    Returns:
        JSON string with errors, anomalies, severity distribution, and health assessment.
    """
    return _detect_errors(log_content, sensitivity)


@mcp.tool()
def correlate_events(log_content: str, time_window_seconds: int = 60) -> str:
    """
    Correlate log events across components to identify cascading failures and root causes.

    Analyzes temporal proximity and component relationships to find:
    - Root cause events (first error in a cascade chain)
    - Cascading failures (errors propagating across components)
    - Event clusters (groups of related errors within a time window)
    - Component impact analysis (which components are most affected)

    Args:
        log_content: The raw log file content as a string.
        time_window_seconds: Maximum seconds between events to consider them correlated.

    Returns:
        JSON string with correlated event groups, timeline, root causes, and component impact.
    """
    return _correlate_events(log_content, time_window_seconds)


@mcp.tool()
def predict_failures(log_content: str, analysis_depth: str = "standard") -> str:
    """
    Analyze log error trends and predict potential future failures.

    Examines error frequency patterns to identify:
    - Accelerating error rates (worsening system health)
    - Periodic failure patterns (recurring issues)
    - Component-specific risk predictions with confidence scores
    - Overall system health trajectory and risk level

    Args:
        log_content: The raw log file content as a string.
        analysis_depth: "quick", "standard", or "deep" analysis depth.

    Returns:
        JSON string with trend analysis, per-component predictions, and risk assessment.
    """
    return _predict_failures(log_content, analysis_depth)


@mcp.tool()
def generate_report(log_content: str, report_type: str = "full") -> str:
    """
    Generate a compliance and security audit report from log data.

    Performs automated checks for:
    - PII exposure (emails, SSNs, credit cards, API keys in logs)
    - Security compliance (SOC2, HIPAA, PCI-DSS, ISO 27001 checks)
    - Audit trail completeness (session tracking, user identification)
    - Data handling and encryption practices

    Args:
        log_content: The raw log file content as a string.
        report_type: "full" (all checks), "security", or "pii" scan only.

    Returns:
        JSON string with compliance score, grade, violations, and recommendations.
    """
    return _generate_report(log_content, report_type)


if __name__ == "__main__":
    port = int(os.environ.get("MCP_SERVER_PORT", 8001))
    host = os.environ.get("MCP_SERVER_HOST", "127.0.0.1")
    print(f"[MCP] LogInsight MCP Server starting on http://{host}:{port}")
    print(f"[MCP] Registered 5 tools: parse_logs, detect_errors, correlate_events, predict_failures, generate_report")
    mcp.settings.host = host
    mcp.settings.port = port
    mcp.run(transport="sse")
