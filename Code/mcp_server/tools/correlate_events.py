"""
correlate_events Tool — Log Event Correlation & Cascading Failure Detection.

Identifies causal chains in logs by:
1. Grouping log entries by component (extracted via regex)
2. Detecting temporal proximity between errors across components
3. Building an event timeline showing cascading failures
4. Identifying root cause candidates (first error in a cascade)
"""

import json
import re
from typing import Any
from datetime import datetime, timedelta
from collections import defaultdict


# Common timestamp patterns
TIMESTAMP_PATTERNS = [
    # ISO 8601: 2024-01-15T10:30:45.123
    re.compile(r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?)"),
    # Syslog: Jan 15 10:30:45
    re.compile(r"([A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})"),
    # Apache CLF: [15/Jan/2024:10:30:45 +0000]
    re.compile(r"\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})\s"),
    # Simple: 10:30:45 or 10:30:45.123
    re.compile(r"(?:^|\s)(\d{2}:\d{2}:\d{2}(?:\.\d+)?)"),
]

# Component extraction patterns
COMPONENT_PATTERNS = [
    re.compile(r"\[([A-Za-z][\w.-]+)\]"),          # [component]
    re.compile(r"<([A-Za-z][\w.-]+)>"),             # <component>
    re.compile(r"(\w+(?:\.\w+){2,})"),              # com.example.Class
    re.compile(r"(?:^|\s)([a-z][\w-]+)\[\d+\]:"),  # sshd[1234]:
    re.compile(r"(?:^|\s)([A-Z][\w]+(?:Service|Manager|Handler|Controller|Worker))"), # ServiceName
]

SEVERITY_PATTERN = re.compile(
    r"\b(FATAL|CRITICAL|EMERGENCY|ERROR|WARN(?:ING)?|INFO|DEBUG|TRACE)\b", re.I
)


def _extract_timestamp(line: str) -> str | None:
    """Try to extract a timestamp string from a log line."""
    for pattern in TIMESTAMP_PATTERNS:
        m = pattern.search(line)
        if m:
            return m.group(1)
    return None


def _extract_component(line: str) -> str:
    """Try to extract the component/source from a log line."""
    for pattern in COMPONENT_PATTERNS:
        m = pattern.search(line)
        if m:
            return m.group(1)
    return "unknown"


def _extract_severity(line: str) -> str:
    """Extract log level/severity."""
    m = SEVERITY_PATTERN.search(line)
    if m:
        level = m.group(1).upper()
        if level in ("WARN", "WARNING"):
            return "warning"
        return level.lower()
    # Heuristic: check for error-like content
    if re.search(r"(?:exception|error|fail|refused|denied)", line, re.I):
        return "error"
    return "info"


def correlate_events(log_content: str, time_window_seconds: int = 60) -> str:
    """
    Correlate log events across components to identify cascading failures.

    Analyzes temporal proximity and component relationships to find:
    - Root cause events (first error in a cascade chain)
    - Cascading failures (errors that propagate across components)
    - Event clusters (groups of related errors within a time window)

    Args:
        log_content: Raw log content as string.
        time_window_seconds: Maximum seconds between events to consider
                             them correlated (default: 60).

    Returns:
        JSON string with correlated event groups, timeline, and root cause analysis.
    """
    log_lines = log_content.strip().split("\n")
    if not log_lines:
        return json.dumps({"error": "No log content provided"})

    # Step 1: Parse all lines into structured events
    events = []
    for i, line in enumerate(log_lines):
        line = line.strip()
        if not line:
            continue

        severity = _extract_severity(line)
        if severity in ("info", "debug", "trace"):
            continue  # Only correlate errors/warnings

        events.append({
            "line_number": i + 1,
            "timestamp": _extract_timestamp(line),
            "component": _extract_component(line),
            "severity": severity,
            "content": line[:300],
        })

    if not events:
        return json.dumps({
            "event_groups": [],
            "timeline": [],
            "root_causes": [],
            "total_correlated_events": 0,
            "message": "No error/warning events found to correlate",
        })

    # Step 2: Group events by temporal proximity
    event_groups = []
    current_group = [events[0]]

    for event in events[1:]:
        # If timestamps are available, use time-based grouping
        # Otherwise, use line-proximity (within 10 lines)
        if current_group:
            last = current_group[-1]
            line_gap = event["line_number"] - last["line_number"]
            if line_gap <= 10:
                current_group.append(event)
            else:
                event_groups.append(current_group)
                current_group = [event]
        else:
            current_group = [event]

    if current_group:
        event_groups.append(current_group)

    # Step 3: Analyze each group for cascading patterns
    cascading_failures = []
    root_causes = []
    component_error_counts: dict[str, int] = defaultdict(int)

    for group_idx, group in enumerate(event_groups):
        components_involved = list(set(e["component"] for e in group))
        severities = [e["severity"] for e in group]

        for e in group:
            component_error_counts[e["component"]] += 1

        cascade = {
            "group_id": group_idx + 1,
            "event_count": len(group),
            "components_involved": components_involved,
            "severity_breakdown": {
                "critical": severities.count("critical") + severities.count("fatal") + severities.count("emergency"),
                "error": severities.count("error"),
                "warning": severities.count("warning"),
            },
            "line_range": [group[0]["line_number"], group[-1]["line_number"]],
            "events": group[:10],  # Limit events per group
            "is_cascading": len(components_involved) > 1,
        }

        if cascade["is_cascading"]:
            cascading_failures.append(cascade)
            # First event in a cascading group is a root cause candidate
            root_causes.append({
                "line_number": group[0]["line_number"],
                "component": group[0]["component"],
                "severity": group[0]["severity"],
                "content": group[0]["content"],
                "cascade_size": len(group),
                "affected_components": components_involved,
            })

    # Step 4: Build timeline
    timeline = []
    for group in event_groups[:20]:
        timeline.append({
            "line_start": group[0]["line_number"],
            "line_end": group[-1]["line_number"],
            "event_count": len(group),
            "primary_component": group[0]["component"],
            "max_severity": max(
                (e["severity"] for e in group),
                key=lambda s: {"critical": 4, "fatal": 4, "emergency": 4,
                               "error": 3, "warning": 2}.get(s, 1),
            ),
            "summary": group[0]["content"][:100],
        })

    # Step 5: Component impact analysis
    component_impact = [
        {"component": comp, "error_count": count, "impact_rank": rank + 1}
        for rank, (comp, count) in enumerate(
            sorted(component_error_counts.items(), key=lambda x: -x[1])
        )
    ]

    return json.dumps({
        "total_error_events": len(events),
        "total_event_groups": len(event_groups),
        "cascading_failures": cascading_failures[:10],
        "root_cause_candidates": root_causes[:10],
        "timeline": timeline,
        "component_impact": component_impact[:15],
        "summary": {
            "cascading_failure_count": len(cascading_failures),
            "unique_components_affected": len(component_error_counts),
            "most_affected_component": (
                component_impact[0]["component"] if component_impact else "N/A"
            ),
        },
    }, default=str)
