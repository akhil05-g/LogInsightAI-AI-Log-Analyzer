"""
parse_logs Tool Implementation
Orchestrates all parsers: Drain3, Grok, JSON, and Regex.
"""

import json
from typing import Any

from mcp_server.parsers.drain_parser import DrainParser
from mcp_server.parsers.grok_parser import GrokParser
from mcp_server.parsers.json_parser import JSONParser
from mcp_server.parsers.regex_parser import RegexParser


def parse_logs(log_content: str, log_format: str = "auto") -> str:
    """
    Parse system log content to extract structured information.

    This tool analyzes raw log text using multiple parsing engines:
    - Drain3 for template mining (clustering similar log messages)
    - Grok patterns for structured field extraction
    - JSON parser for JSON-formatted logs
    - Regex fallback for timestamp, level, and component extraction

    Args:
        log_content: The raw log file content as a string.
        log_format: Expected log format. Use "auto" for automatic detection,
                    or specify: "syslog", "apache_access", "apache_error",
                    "hdfs", "zookeeper", "json", "general_timestamp".

    Returns:
        JSON string with parsed results including templates, entries, and statistics.
    """
    log_lines = log_content.strip().split("\n")
    if not log_lines:
        return json.dumps({"error": "No log content provided", "entries": []})

    results: dict[str, Any] = {
        "total_lines": len(log_lines),
        "format_detected": None,
    }

    # Step 1: Check if JSON format
    json_parser = JSONParser()
    if log_format in ("auto", "json") and json_parser.is_json_log(log_lines):
        json_result = json_parser.parse(log_lines)
        results["json_parsing"] = json_result
        results["format_detected"] = "json"
    else:
        # Step 2: Try Grok pattern matching
        grok_parser = GrokParser()
        fmt = log_format if log_format != "auto" else None
        grok_result = grok_parser.parse(log_lines, format_name=fmt)
        results["grok_parsing"] = grok_result

        if grok_result.get("format_detected"):
            results["format_detected"] = grok_result["format_detected"]

    # Step 3: Always run Drain3 template mining
    try:
        drain_parser = DrainParser()
        drain_result = drain_parser.parse(log_lines)
        results["template_mining"] = drain_result
    except Exception as e:
        results["template_mining"] = {"error": str(e), "templates": []}

    # Step 4: Always run regex fallback for level distribution
    regex_parser = RegexParser()
    regex_result = regex_parser.parse(log_lines)
    results["regex_parsing"] = regex_result

    if not results["format_detected"] and regex_result.get("format_detected"):
        results["format_detected"] = regex_result["format_detected"]

    # Build summary statistics
    level_dist = regex_result.get("level_distribution", {})
    template_count = results.get("template_mining", {}).get("total_clusters", 0)

    results["summary"] = {
        "format": results["format_detected"] or "unknown",
        "total_lines": len(log_lines),
        "unique_templates": template_count,
        "level_distribution": level_dist,
        "has_errors": level_dist.get("ERROR", 0) + level_dist.get("FATAL", 0) > 0,
        "has_warnings": level_dist.get("WARN", 0) + level_dist.get("WARNING", 0) > 0,
    }

    return json.dumps(results, default=str)
