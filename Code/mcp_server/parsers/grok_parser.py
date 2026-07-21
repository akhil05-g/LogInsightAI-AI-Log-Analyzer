"""
Grok Pattern Parser
Uses pygrok to match log lines against predefined Grok patterns (similar to Logstash).
"""

from typing import Any


# Predefined Grok patterns for common log formats
GROK_PATTERNS = {
    "syslog": r"%{SYSLOGTIMESTAMP:timestamp} %{SYSLOGHOST:hostname} %{DATA:program}(?:\[%{POSINT:pid}\])?: %{GREEDYDATA:message}",
    "apache_access": r'%{IPORHOST:clientip} %{USER:ident} %{USER:auth} \[%{HTTPDATE:timestamp}\] "(?:%{WORD:verb} %{NOTSPACE:request}(?: HTTP/%{NUMBER:httpversion})?|%{DATA:rawrequest})" %{NUMBER:response} (?:%{NUMBER:bytes}|-)',
    "apache_error": r"\[%{DATA:timestamp}\] \[%{WORD:level}\] (?:\[client %{IPORHOST:clientip}\] )?%{GREEDYDATA:message}",
    "hdfs": r"%{NUMBER:date} %{NUMBER:time} %{NUMBER:pid} %{LOGLEVEL:level} %{DATA:component}: %{GREEDYDATA:message}",
    "zookeeper": r"%{TIMESTAMP_ISO8601:timestamp} \[myid:%{NUMBER:myid}\] - %{LOGLEVEL:level}\s+\[%{DATA:thread}\] - %{GREEDYDATA:message}",
    "general_timestamp": r"%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level}\s+%{GREEDYDATA:message}",
}


class GrokParser:
    """Parse logs using Grok patterns for structured field extraction."""

    def __init__(self):
        self._groks: dict = {}
        self._initialized = False

    def _init_patterns(self):
        """Lazy-initialize Grok pattern objects."""
        if self._initialized:
            return

        try:
            from pygrok import Grok
            for name, pattern in GROK_PATTERNS.items():
                try:
                    self._groks[name] = Grok(pattern)
                except Exception:
                    pass  # Skip invalid patterns gracefully
        except ImportError:
            pass  # pygrok not installed

        self._initialized = True

    def detect_format(self, sample_lines: list[str]) -> str | None:
        """
        Auto-detect log format by trying each Grok pattern against sample lines.

        Args:
            sample_lines: First N lines of the log file.

        Returns:
            Name of the matching pattern, or None.
        """
        self._init_patterns()

        if not self._groks:
            return None

        scores: dict[str, int] = {}
        test_lines = sample_lines[:20]

        for name, grok in self._groks.items():
            match_count = 0
            for line in test_lines:
                line = line.strip()
                if not line:
                    continue
                result = grok.match(line)
                if result:
                    match_count += 1
            if match_count > 0:
                scores[name] = match_count

        if not scores:
            return None

        return max(scores, key=scores.get)

    def parse(self, log_lines: list[str], format_name: str | None = None) -> dict[str, Any]:
        """
        Parse log lines using the detected or specified Grok pattern.

        Args:
            log_lines: List of raw log strings.
            format_name: Specific Grok pattern name, or None for auto-detect.

        Returns:
            Dictionary with parsed entries and format info.
        """
        self._init_patterns()

        if format_name is None:
            format_name = self.detect_format(log_lines)

        if format_name is None or format_name not in self._groks:
            return {
                "format_detected": None,
                "entries": [],
                "parsed_count": 0,
                "total_lines": len(log_lines),
            }

        grok = self._groks[format_name]
        entries = []

        for i, line in enumerate(log_lines):
            line = line.strip()
            if not line:
                continue

            result = grok.match(line)
            if result:
                entry = {"line_number": i + 1, **result}
                entries.append(entry)

        return {
            "format_detected": format_name,
            "entries": entries[:500],  # Limit for response size
            "parsed_count": len(entries),
            "total_lines": len(log_lines),
            "parse_rate": round(len(entries) / max(len(log_lines), 1) * 100, 1),
        }
