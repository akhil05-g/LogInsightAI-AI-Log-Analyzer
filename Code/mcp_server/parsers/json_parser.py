"""
JSON Log Parser
Parses JSON-formatted log lines (NDJSON) and normalizes field names.
"""

import json
from typing import Any

# Common field name aliases → canonical names
FIELD_ALIASES = {
    "timestamp": ["timestamp", "time", "ts", "@timestamp", "datetime", "date", "log_time"],
    "level": ["level", "severity", "log_level", "loglevel", "lvl", "priority"],
    "message": ["message", "msg", "log", "text", "body", "log_message"],
    "source": ["source", "logger", "component", "module", "class", "service", "app"],
    "hostname": ["hostname", "host", "server", "node", "machine"],
}


def _normalize_key(key: str) -> str:
    """Map a field name to its canonical form."""
    key_lower = key.lower().strip()
    for canonical, aliases in FIELD_ALIASES.items():
        if key_lower in aliases:
            return canonical
    return key_lower


class JSONParser:
    """Parse JSON-formatted log lines (NDJSON)."""

    def is_json_log(self, sample_lines: list[str]) -> bool:
        """Check if the log file uses JSON format."""
        json_count = 0
        check_lines = [l.strip() for l in sample_lines[:10] if l.strip()]

        for line in check_lines:
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    json_count += 1
            except (json.JSONDecodeError, ValueError):
                pass

        return json_count >= len(check_lines) * 0.5 if check_lines else False

    def parse(self, log_lines: list[str]) -> dict[str, Any]:
        """
        Parse JSON log lines and normalize field names.

        Args:
            log_lines: List of raw log strings.

        Returns:
            Dictionary with parsed entries and metadata.
        """
        entries = []
        parse_errors = 0
        all_fields: set[str] = set()

        for i, line in enumerate(log_lines):
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
                if not isinstance(obj, dict):
                    parse_errors += 1
                    continue

                normalized = {"line_number": i + 1}
                for key, value in obj.items():
                    canonical = _normalize_key(key)
                    normalized[canonical] = value
                    all_fields.add(canonical)

                entries.append(normalized)
            except (json.JSONDecodeError, ValueError):
                parse_errors += 1

        return {
            "format_detected": "json" if entries else None,
            "entries": entries[:500],
            "parsed_count": len(entries),
            "parse_errors": parse_errors,
            "total_lines": len(log_lines),
            "fields_found": sorted(all_fields),
        }
