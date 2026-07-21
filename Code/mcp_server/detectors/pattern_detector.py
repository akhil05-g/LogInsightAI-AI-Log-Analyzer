"""
Regex Pattern Detector
Matches known error signatures like stack traces, HTTP errors, connection issues.
"""

import re
from typing import Any


# Compiled regex patterns for known error signatures
ERROR_PATTERNS = [
    {
        "name": "java_exception",
        "pattern": re.compile(r"(?:Exception|Error):\s+.+|(?:at\s+[\w.$]+\([\w.]+:\d+\))", re.IGNORECASE),
        "severity": "error",
        "category": "exception",
    },
    {
        "name": "python_traceback",
        "pattern": re.compile(r"Traceback \(most recent call last\)|File \"[^\"]+\", line \d+", re.IGNORECASE),
        "severity": "error",
        "category": "exception",
    },
    {
        "name": "http_5xx",
        "pattern": re.compile(r'"\s*(5\d{2})\s+\d+|HTTP[/ ]\d\.\d"\s+(5\d{2})'),
        "severity": "error",
        "category": "http_error",
    },
    {
        "name": "http_4xx",
        "pattern": re.compile(r'"\s*(4\d{2})\s+\d+|HTTP[/ ]\d\.\d"\s+(4\d{2})'),
        "severity": "warning",
        "category": "http_error",
    },
    {
        "name": "connection_error",
        "pattern": re.compile(r"Connection\s+(?:refused|reset|timed?\s*out|closed|broken)", re.IGNORECASE),
        "severity": "error",
        "category": "connection",
    },
    {
        "name": "disk_issue",
        "pattern": re.compile(r"No space left on device|disk\s+full|filesystem\s+full|I/O error", re.IGNORECASE),
        "severity": "critical",
        "category": "disk",
    },
    {
        "name": "memory_issue",
        "pattern": re.compile(r"Out of memory|OOM|Cannot allocate memory|MemoryError|heap\s+space", re.IGNORECASE),
        "severity": "critical",
        "category": "memory",
    },
    {
        "name": "auth_failure",
        "pattern": re.compile(r"(?:authentication|auth)\s+fail|Failed password|invalid user|Access denied|Permission denied|unauthorized", re.IGNORECASE),
        "severity": "warning",
        "category": "security",
    },
    {
        "name": "crash_signal",
        "pattern": re.compile(r"segfault|core dump|SIGSEGV|SIGABRT|SIGKILL|killed process", re.IGNORECASE),
        "severity": "critical",
        "category": "crash",
    },
    {
        "name": "service_restart",
        "pattern": re.compile(r"service\s+(?:terminated|stopped|restarting|crashed)|terminated unexpectedly", re.IGNORECASE),
        "severity": "warning",
        "category": "service",
    },
    {
        "name": "ssl_tls_error",
        "pattern": re.compile(r"SSL|TLS|certificate\s+(?:expired|invalid|error)|handshake\s+fail", re.IGNORECASE),
        "severity": "error",
        "category": "security",
    },
]


class PatternDetector:
    """Detect known error patterns using compiled regex."""

    def detect(self, log_lines: list[str]) -> dict[str, Any]:
        """
        Scan log lines for known error patterns.

        Args:
            log_lines: List of raw log strings.

        Returns:
            Dictionary with pattern matches grouped by category.
        """
        matches = []
        category_counts: dict[str, int] = {}
        severity_counts = {"critical": 0, "error": 0, "warning": 0, "info": 0}

        for i, line in enumerate(log_lines):
            line = line.strip()
            if not line:
                continue

            for ep in ERROR_PATTERNS:
                match = ep["pattern"].search(line)
                if match:
                    cat = ep["category"]
                    sev = ep["severity"]
                    category_counts[cat] = category_counts.get(cat, 0) + 1
                    severity_counts[sev] = severity_counts.get(sev, 0) + 1

                    matches.append({
                        "line_number": i + 1,
                        "pattern_name": ep["name"],
                        "category": cat,
                        "severity": sev,
                        "matched_text": match.group(0)[:100],
                        "context": line[:300],
                    })

        return {
            "engine": "regex_patterns",
            "matches": matches[:200],
            "total_matches": len(matches),
            "category_distribution": category_counts,
            "severity_distribution": severity_counts,
        }
