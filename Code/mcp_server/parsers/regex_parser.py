"""
Regex-based Log Parser
Fallback parser that uses regex patterns to extract timestamps, levels, and messages.
"""

import re
from typing import Any

# Common timestamp patterns
TIMESTAMP_PATTERNS = [
    (r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?)", "iso8601"),
    (r"(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})", "syslog"),
    (r"(\d{6}\s+\d{6})", "hdfs"),
    (r"\[(\w{3}\s+\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+\d{4})\]", "apache_error"),
    (r"\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}\s+[+-]\d{4})\]", "apache_access"),
    (r"(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s+(?:AM|PM))", "windows"),
]

# Log level patterns
LEVEL_PATTERN = re.compile(
    r"\b(FATAL|CRITICAL|ERROR|WARN(?:ING)?|INFO|DEBUG|TRACE|NOTICE|SEVERE|PANIC|EMERG)\b",
    re.IGNORECASE,
)

# Component/source extraction
COMPONENT_PATTERNS = [
    re.compile(r"\[([A-Za-z][\w.:-]+)\]"),      # [Component]
    re.compile(r"(\w+(?:\.\w+)+):\s"),            # com.example.Class:
    re.compile(r"\b(\w+)\[\d+\]:"),               # sshd[12345]:
    re.compile(r"(\w+(?:\.py|\.java|\.go))\b"),   # filename.py
]


class RegexParser:
    """Fallback regex-based parser for generic log formats."""

    def __init__(self):
        self._compiled_ts = [(re.compile(p), name) for p, name in TIMESTAMP_PATTERNS]

    def _extract_timestamp(self, line: str) -> tuple[str | None, str | None]:
        """Extract timestamp and its format from a log line."""
        for pattern, fmt_name in self._compiled_ts:
            match = pattern.search(line)
            if match:
                return match.group(1), fmt_name
        return None, None

    def _extract_level(self, line: str) -> str | None:
        """Extract log level from a log line."""
        match = LEVEL_PATTERN.search(line)
        if match:
            level = match.group(1).upper()
            if level == "WARNING":
                level = "WARN"
            return level
        return None

    def _extract_component(self, line: str) -> str | None:
        """Extract component/source name from a log line."""
        for pattern in COMPONENT_PATTERNS:
            match = pattern.search(line)
            if match:
                return match.group(1)
        return None

    def parse(self, log_lines: list[str]) -> dict[str, Any]:
        """
        Parse log lines using regex patterns.

        Args:
            log_lines: List of raw log strings.

        Returns:
            Dictionary with parsed entries.
        """
        entries = []
        timestamp_formats: dict[str, int] = {}
        level_distribution: dict[str, int] = {}

        for i, line in enumerate(log_lines):
            line = line.strip()
            if not line:
                continue

            timestamp, ts_format = self._extract_timestamp(line)
            level = self._extract_level(line)
            component = self._extract_component(line)

            if ts_format:
                timestamp_formats[ts_format] = timestamp_formats.get(ts_format, 0) + 1

            if level:
                level_distribution[level] = level_distribution.get(level, 0) + 1

            entries.append({
                "line_number": i + 1,
                "timestamp": timestamp,
                "level": level,
                "component": component,
                "raw": line[:500],
            })

        # Detect the dominant timestamp format
        dominant_format = max(timestamp_formats, key=timestamp_formats.get) if timestamp_formats else None

        return {
            "format_detected": dominant_format or "unknown",
            "entries": entries[:500],
            "parsed_count": len(entries),
            "total_lines": len(log_lines),
            "timestamp_format": dominant_format,
            "level_distribution": level_distribution,
        }
