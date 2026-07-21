"""
predict_failures Tool — Predictive Failure Analysis.

Analyzes error frequency trends to predict potential future failures:
1. Extracts error events with timestamps/line positions
2. Computes rolling error rates over sliding windows
3. Detects accelerating/decelerating trends via linear regression
4. Identifies periodic failure patterns (recurring errors)
5. Returns risk predictions with confidence scores
"""

import json
import re
import math
from typing import Any
from collections import defaultdict, Counter


def _extract_error_events(log_lines: list[str]) -> list[dict[str, Any]]:
    """Extract error-level events with positions."""
    severity_re = re.compile(
        r"\b(FATAL|CRITICAL|EMERGENCY|ERROR|WARN(?:ING)?)\b", re.I
    )
    component_re = re.compile(r"\[([A-Za-z][\w.-]+)\]")
    events = []

    for i, line in enumerate(log_lines):
        line = line.strip()
        if not line:
            continue
        m = severity_re.search(line)
        if m:
            comp_match = component_re.search(line)
            events.append({
                "line_number": i + 1,
                "position_pct": round(i / max(len(log_lines), 1) * 100, 2),
                "severity": m.group(1).upper(),
                "component": comp_match.group(1) if comp_match else "unknown",
                "content": line[:200],
            })

    return events


def _linear_regression(x: list[float], y: list[float]) -> tuple[float, float, float]:
    """Simple linear regression. Returns (slope, intercept, r_squared)."""
    n = len(x)
    if n < 2:
        return 0.0, 0.0, 0.0

    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi ** 2 for xi in x)

    denom = n * sum_x2 - sum_x ** 2
    if abs(denom) < 1e-10:
        return 0.0, sum_y / n, 0.0

    slope = (n * sum_xy - sum_x * sum_y) / denom
    intercept = (sum_y - slope * sum_x) / n

    # R-squared
    y_mean = sum_y / n
    ss_tot = sum((yi - y_mean) ** 2 for yi in y)
    ss_res = sum((yi - (slope * xi + intercept)) ** 2 for xi, yi in zip(x, y))
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

    return slope, intercept, r_squared


def _detect_periodicity(event_positions: list[int]) -> dict[str, Any] | None:
    """Detect periodic patterns in error occurrence positions."""
    if len(event_positions) < 4:
        return None

    # Compute gaps between consecutive errors
    gaps = [
        event_positions[i + 1] - event_positions[i]
        for i in range(len(event_positions) - 1)
    ]

    if not gaps:
        return None

    mean_gap = sum(gaps) / len(gaps)
    if mean_gap < 1:
        return None

    variance = sum((g - mean_gap) ** 2 for g in gaps) / len(gaps)
    std_dev = math.sqrt(variance)
    cv = std_dev / mean_gap if mean_gap > 0 else float("inf")  # Coefficient of variation

    # Low CV means highly periodic
    if cv < 0.3:
        return {
            "is_periodic": True,
            "mean_interval_lines": round(mean_gap, 1),
            "regularity_score": round(1 - cv, 3),
            "pattern": f"Errors occur approximately every {round(mean_gap)} lines",
        }

    return None


def predict_failures(log_content: str, analysis_depth: str = "standard") -> str:
    """
    Analyze log error trends and predict potential future failures.

    Examines error frequency patterns over time/position to identify:
    - Accelerating error rates (worsening trends)
    - Periodic failure patterns (recurring issues)
    - Component-specific risk predictions
    - Overall system health trajectory

    Args:
        log_content: Raw log content as string.
        analysis_depth: "quick" (basic stats), "standard" (trends + patterns),
                        or "deep" (full predictive analysis).

    Returns:
        JSON string with trend analysis, predictions, and risk assessment.
    """
    log_lines = log_content.strip().split("\n")
    if not log_lines:
        return json.dumps({"error": "No log content provided"})

    total_lines = len(log_lines)
    events = _extract_error_events(log_lines)

    if len(events) < 3:
        return json.dumps({
            "total_lines": total_lines,
            "total_error_events": len(events),
            "predictions": [],
            "message": "Too few error events for trend analysis (need >= 3)",
            "overall_risk": "LOW",
        })

    # ── Trend Analysis: Split log into segments and count errors per segment ──
    num_segments = min(10, max(3, total_lines // 50))
    segment_size = total_lines // num_segments
    segment_counts = [0] * num_segments

    for event in events:
        seg_idx = min((event["line_number"] - 1) // segment_size, num_segments - 1)
        segment_counts[seg_idx] += 1

    # Linear regression on segment error counts
    x_vals = list(range(num_segments))
    slope, intercept, r_sq = _linear_regression(
        [float(x) for x in x_vals],
        [float(c) for c in segment_counts],
    )

    # Determine trend direction
    if slope > 0.5 and r_sq > 0.3:
        trend = "INCREASING"
        trend_description = f"Error rate is increasing by ~{abs(slope):.1f} errors per segment"
    elif slope < -0.5 and r_sq > 0.3:
        trend = "DECREASING"
        trend_description = f"Error rate is decreasing by ~{abs(slope):.1f} errors per segment"
    else:
        trend = "STABLE"
        trend_description = "Error rate is relatively stable across the log"

    # ── Per-Component Analysis ──
    component_events: dict[str, list[int]] = defaultdict(list)
    for event in events:
        component_events[event["component"]].append(event["line_number"])

    component_predictions = []
    for comp, positions in component_events.items():
        count = len(positions)
        rate = count / total_lines * 100

        # Component-specific trend
        comp_segments = [0] * num_segments
        for pos in positions:
            seg_idx = min((pos - 1) // segment_size, num_segments - 1)
            comp_segments[seg_idx] += 1

        comp_slope, _, comp_r2 = _linear_regression(
            [float(x) for x in x_vals],
            [float(c) for c in comp_segments],
        )

        # Periodicity check
        periodicity = _detect_periodicity(positions)

        # Risk assessment
        if comp_slope > 1.0 and comp_r2 > 0.4:
            risk = "HIGH"
            prediction = f"Component '{comp}' error rate is accelerating — likely failure"
        elif comp_slope > 0.3:
            risk = "MEDIUM"
            prediction = f"Component '{comp}' shows gradually increasing errors"
        elif periodicity and periodicity.get("is_periodic"):
            risk = "MEDIUM"
            prediction = f"Component '{comp}' has recurring errors ({periodicity['pattern']})"
        else:
            risk = "LOW"
            prediction = f"Component '{comp}' error rate is stable"

        component_predictions.append({
            "component": comp,
            "error_count": count,
            "error_rate_pct": round(rate, 2),
            "trend_slope": round(comp_slope, 3),
            "trend_r_squared": round(comp_r2, 3),
            "risk_level": risk,
            "prediction": prediction,
            "is_periodic": bool(periodicity),
            "periodicity": periodicity,
        })

    component_predictions.sort(
        key=lambda x: {"HIGH": 3, "MEDIUM": 2, "LOW": 1}[x["risk_level"]],
        reverse=True,
    )

    # ── Overall Risk Assessment ──
    high_risk_count = sum(1 for p in component_predictions if p["risk_level"] == "HIGH")
    error_rate = len(events) / total_lines * 100

    if high_risk_count >= 2 or error_rate > 20:
        overall_risk = "CRITICAL"
        risk_summary = "Multiple components showing accelerating failures. Immediate attention required."
    elif high_risk_count >= 1 or error_rate > 10:
        overall_risk = "HIGH"
        risk_summary = "At least one component trending toward failure. Investigation recommended."
    elif trend == "INCREASING":
        overall_risk = "MEDIUM"
        risk_summary = "Overall error rate is increasing. Monitor closely."
    else:
        overall_risk = "LOW"
        risk_summary = "System appears stable. No imminent failure predicted."

    # ── Severity Distribution Over Time ──
    severity_trends: dict[str, list[int]] = defaultdict(lambda: [0] * num_segments)
    for event in events:
        sev = event["severity"]
        if sev in ("WARN", "WARNING"):
            sev = "WARNING"
        seg_idx = min((event["line_number"] - 1) // segment_size, num_segments - 1)
        severity_trends[sev][seg_idx] += 1

    return json.dumps({
        "total_lines": total_lines,
        "total_error_events": len(events),
        "overall_error_rate_pct": round(error_rate, 2),
        "trend": {
            "direction": trend,
            "description": trend_description,
            "slope": round(slope, 3),
            "r_squared": round(r_sq, 3),
            "segment_error_counts": segment_counts,
        },
        "overall_risk": overall_risk,
        "risk_summary": risk_summary,
        "component_predictions": component_predictions[:15],
        "severity_trends": dict(severity_trends),
        "high_risk_components": [
            p["component"] for p in component_predictions if p["risk_level"] == "HIGH"
        ],
    }, default=str)
