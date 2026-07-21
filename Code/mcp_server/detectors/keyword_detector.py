"""
FlashText Keyword Detector
Fast keyword extraction for error, warning, security, and performance keywords.
"""

from typing import Any


# Keyword categories with severity mapping
KEYWORD_CATEGORIES = {
    "critical": {
        "severity": "critical",
        "keywords": [
            "FATAL", "PANIC", "EMERGENCY", "EMERG", "CRITICAL",
            "SEVERE", "unrecoverable", "system crash", "kernel panic",
            "out of memory", "OOM", "data corruption", "data loss",
        ],
    },
    "error": {
        "severity": "error",
        "keywords": [
            "ERROR", "Exception", "FAILURE", "FAILED", "exception",
            "traceback", "stack trace", "NullPointerException",
            "IOException", "RuntimeException", "PermissionError",
            "ConnectionRefused", "Connection refused", "Connection reset",
            "Broken pipe", "EOFException", "timeout", "timed out",
            "segfault", "core dump", "abort",
        ],
    },
    "warning": {
        "severity": "warning",
        "keywords": [
            "WARNING", "WARN", "DEPRECATED", "deprecated",
            "Redundant", "retry", "retrying", "slow",
            "high latency", "disk full", "low memory",
            "certificate expir", "insecure", "not recommended",
        ],
    },
    "security": {
        "severity": "error",
        "keywords": [
            "unauthorized", "denied", "forbidden", "authentication failure",
            "Failed password", "invalid user", "illegal user",
            "BREAK-IN ATTEMPT", "injection", "XSS",
            "brute force", "Too many authentication failures",
            "SYN flooding",
        ],
    },
    "performance": {
        "severity": "warning",
        "keywords": [
            "timeout", "latency", "slow", "throttl",
            "queue full", "backpressure", "congestion",
            "memory leak", "swap", "high cpu", "deadlock",
        ],
    },
}


class KeywordDetector:
    """Detect error keywords in log lines using FlashText."""

    def __init__(self):
        self._processor = None
        self._keyword_severity: dict[str, str] = {}

    def _init_processor(self):
        """Lazy-initialize the FlashText KeywordProcessor."""
        if self._processor is not None:
            return

        from flashtext import KeywordProcessor

        self._processor = KeywordProcessor(case_sensitive=False)

        for category, config in KEYWORD_CATEGORIES.items():
            severity = config["severity"]
            for kw in config["keywords"]:
                clean_name = f"{category}::{kw}"
                self._processor.add_keyword(kw, clean_name)
                self._keyword_severity[clean_name] = severity

    def detect(self, log_lines: list[str]) -> dict[str, Any]:
        """
        Scan log lines for error/warning/security keywords.

        Args:
            log_lines: List of raw log strings.

        Returns:
            Dictionary with detected keywords and severity distribution.
        """
        self._init_processor()

        detections = []
        severity_counts = {"critical": 0, "error": 0, "warning": 0, "info": 0}

        for i, line in enumerate(log_lines):
            line = line.strip()
            if not line:
                continue

            found = self._processor.extract_keywords(line, span_info=True)
            if found:
                for keyword_name, start, end in found:
                    severity = self._keyword_severity.get(keyword_name, "info")
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1

                    detections.append({
                        "line_number": i + 1,
                        "keyword": keyword_name.split("::")[-1],
                        "category": keyword_name.split("::")[0],
                        "severity": severity,
                        "context": line[:300],
                        "span": [start, end],
                    })

        return {
            "engine": "flashtext",
            "detections": detections[:200],
            "total_detections": len(detections),
            "severity_distribution": severity_counts,
            "lines_with_issues": len(set(d["line_number"] for d in detections)),
        }
