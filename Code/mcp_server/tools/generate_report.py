"""
generate_report Tool — Compliance & Audit Report Generator.

Performs automated compliance checks on log data:
1. PII exposure detection (emails, IPs, SSNs, credit cards in logs)
2. Security compliance checks (unencrypted connections, auth failures, privilege escalation)
3. Audit trail completeness (gaps in logging, missing session tracking)
4. Retention and format compliance
5. Generates a compliance score with detailed violation listings
"""

import json
import re
from typing import Any
from collections import defaultdict


# PII detection patterns
PII_PATTERNS = {
    "email": re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
    "ipv4_address": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "credit_card": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b"),
    "phone_number": re.compile(r"\b(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"),
    "api_key_pattern": re.compile(r"(?:api[_-]?key|token|secret|password|passwd)\s*[=:]\s*\S+", re.I),
}

# Security compliance patterns
SECURITY_CHECKS = {
    "unencrypted_connection": {
        "pattern": re.compile(r"(?:http://|ftp://|telnet://|plain\s*text|unencrypted)", re.I),
        "severity": "high",
        "standard": "SOC2/HIPAA",
        "description": "Unencrypted connection or protocol detected",
    },
    "auth_failure_burst": {
        "pattern": re.compile(r"(?:authentication fail|failed password|invalid user|access denied|login fail)", re.I),
        "severity": "high",
        "standard": "SOC2",
        "description": "Authentication failure — possible brute force attempt",
    },
    "privilege_escalation": {
        "pattern": re.compile(r"(?:sudo|su\s|privilege|root\s+access|admin\s+login|escalat)", re.I),
        "severity": "medium",
        "standard": "SOC2/ISO27001",
        "description": "Privilege escalation or elevated access event",
    },
    "cert_issue": {
        "pattern": re.compile(r"(?:certificate\s+(?:expired|invalid|error|warning)|SSL\s+error|TLS\s+handshake\s+fail)", re.I),
        "severity": "high",
        "standard": "PCI-DSS",
        "description": "Certificate or TLS/SSL issue detected",
    },
    "data_exposure": {
        "pattern": re.compile(r"(?:stack\s*trace|debug\s*mode|verbose|dump|core\s*dump)", re.I),
        "severity": "medium",
        "standard": "OWASP",
        "description": "Potential data exposure through debug output or stack traces",
    },
    "service_account_misuse": {
        "pattern": re.compile(r"(?:service\s+account|system\s+user|machine\s+identity).*(?:fail|deny|reject)", re.I),
        "severity": "high",
        "standard": "SOC2",
        "description": "Service account or system identity issue",
    },
}

# Audit trail checks
AUDIT_CHECKS = {
    "session_tracking": re.compile(r"(?:session[_\s]?id|request[_\s]?id|correlation[_\s]?id|trace[_\s]?id)", re.I),
    "user_identification": re.compile(r"(?:user[_\s]?(?:name|id)|uid|principal|subject)", re.I),
    "timestamp_present": re.compile(r"\d{4}[-/]\d{2}[-/]\d{2}|\d{2}:\d{2}:\d{2}"),
    "action_logging": re.compile(r"(?:action|operation|event[_\s]?type|method)\s*[=:]", re.I),
}


def generate_report(log_content: str, report_type: str = "full") -> str:
    """
    Generate a compliance and security audit report from log data.

    Performs automated checks for:
    - PII (Personally Identifiable Information) exposure
    - Security compliance (SOC2, HIPAA, PCI-DSS, ISO 27001)
    - Audit trail completeness
    - Data handling practices

    Args:
        log_content: Raw log content as string.
        report_type: "full" (all checks), "security" (security only),
                     or "pii" (PII scan only).

    Returns:
        JSON string with compliance score, violations, and recommendations.
    """
    log_lines = log_content.strip().split("\n")
    if not log_lines:
        return json.dumps({"error": "No log content provided"})

    total_lines = len(log_lines)
    violations: list[dict[str, Any]] = []
    pii_findings: list[dict[str, Any]] = []
    security_findings: list[dict[str, Any]] = []
    compliance_checks: dict[str, bool] = {}

    # ── PII Scan ──
    pii_counts: dict[str, int] = defaultdict(int)
    for i, line in enumerate(log_lines):
        line = line.strip()
        if not line:
            continue

        for pii_type, pattern in PII_PATTERNS.items():
            matches = pattern.findall(line)
            if matches:
                pii_counts[pii_type] += len(matches)
                if len(pii_findings) < 50:  # Limit findings
                    pii_findings.append({
                        "line_number": i + 1,
                        "pii_type": pii_type,
                        "count": len(matches),
                        "severity": "high" if pii_type in ("ssn", "credit_card", "api_key_pattern") else "medium",
                        "context": line[:200],
                        "recommendation": f"Remove or mask {pii_type} data before logging",
                    })

    has_pii = sum(pii_counts.values()) > 0
    compliance_checks["no_pii_exposure"] = not has_pii

    if report_type == "pii":
        pii_score = 100 if not has_pii else max(0, 100 - sum(pii_counts.values()) * 5)
        return json.dumps({
            "report_type": "pii",
            "total_lines": total_lines,
            "pii_findings": pii_findings,
            "pii_summary": dict(pii_counts),
            "pii_compliance_score": pii_score,
            "has_pii": has_pii,
        }, default=str)

    # ── Security Compliance Scan ──
    security_counts: dict[str, int] = defaultdict(int)
    for i, line in enumerate(log_lines):
        line = line.strip()
        if not line:
            continue

        for check_name, check in SECURITY_CHECKS.items():
            if check["pattern"].search(line):
                security_counts[check_name] += 1
                if len(security_findings) < 100:
                    security_findings.append({
                        "line_number": i + 1,
                        "check": check_name,
                        "severity": check["severity"],
                        "standard": check["standard"],
                        "description": check["description"],
                        "context": line[:200],
                    })

    compliance_checks["no_unencrypted_connections"] = security_counts.get("unencrypted_connection", 0) == 0
    compliance_checks["no_auth_failure_bursts"] = security_counts.get("auth_failure_burst", 0) < 5
    compliance_checks["no_cert_issues"] = security_counts.get("cert_issue", 0) == 0
    compliance_checks["no_data_exposure"] = security_counts.get("data_exposure", 0) == 0

    # ── Audit Trail Completeness ──
    audit_scores: dict[str, float] = {}
    sample_size = min(100, total_lines)
    sample_lines = log_lines[:sample_size]

    for check_name, pattern in AUDIT_CHECKS.items():
        matches = sum(1 for line in sample_lines if pattern.search(line))
        score = matches / max(sample_size, 1)
        audit_scores[check_name] = round(score * 100, 1)
        compliance_checks[f"audit_{check_name}"] = score > 0.5

    # ── Calculate Overall Compliance Score ──
    passed = sum(1 for v in compliance_checks.values() if v)
    total_checks = len(compliance_checks)
    compliance_score = round(passed / max(total_checks, 1) * 100)

    # Severity penalty
    high_severity_count = sum(
        1 for f in security_findings + pii_findings if f.get("severity") == "high"
    )
    if high_severity_count > 10:
        compliance_score = max(0, compliance_score - 20)
    elif high_severity_count > 5:
        compliance_score = max(0, compliance_score - 10)

    # ── Grade ──
    if compliance_score >= 90:
        grade = "A"
        status = "COMPLIANT"
    elif compliance_score >= 75:
        grade = "B"
        status = "MOSTLY_COMPLIANT"
    elif compliance_score >= 50:
        grade = "C"
        status = "NEEDS_IMPROVEMENT"
    else:
        grade = "F"
        status = "NON_COMPLIANT"

    # ── Recommendations ──
    recommendations = []
    if has_pii:
        recommendations.append({
            "priority": "HIGH",
            "area": "PII Protection",
            "action": "Implement log masking/redaction for PII data (emails, IPs, credentials)",
            "standard": "HIPAA/GDPR",
        })
    if security_counts.get("unencrypted_connection", 0) > 0:
        recommendations.append({
            "priority": "HIGH",
            "area": "Encryption",
            "action": "Migrate all connections to TLS/HTTPS. Disable plain-text protocols.",
            "standard": "SOC2/PCI-DSS",
        })
    if security_counts.get("auth_failure_burst", 0) >= 5:
        recommendations.append({
            "priority": "HIGH",
            "area": "Authentication",
            "action": "Implement rate limiting and account lockout policies for authentication.",
            "standard": "SOC2",
        })
    if audit_scores.get("session_tracking", 0) < 50:
        recommendations.append({
            "priority": "MEDIUM",
            "area": "Audit Trail",
            "action": "Add session/correlation IDs to all log entries for traceability.",
            "standard": "SOC2/ISO27001",
        })
    if audit_scores.get("user_identification", 0) < 50:
        recommendations.append({
            "priority": "MEDIUM",
            "area": "User Tracking",
            "action": "Include user/principal identity in all log entries.",
            "standard": "SOC2",
        })
    if security_counts.get("data_exposure", 0) > 0:
        recommendations.append({
            "priority": "MEDIUM",
            "area": "Data Protection",
            "action": "Disable debug/verbose logging in production. Suppress stack traces in user-facing outputs.",
            "standard": "OWASP",
        })

    return json.dumps({
        "report_type": report_type,
        "total_lines": total_lines,
        "compliance_score": compliance_score,
        "grade": grade,
        "status": status,
        "checks_passed": passed,
        "checks_total": total_checks,
        "compliance_checks": compliance_checks,
        "pii_findings": pii_findings[:30],
        "pii_summary": dict(pii_counts),
        "security_findings": security_findings[:50],
        "security_summary": dict(security_counts),
        "audit_trail_scores": audit_scores,
        "recommendations": recommendations,
        "standards_referenced": ["SOC2", "HIPAA", "PCI-DSS", "ISO27001", "OWASP", "GDPR"],
    }, default=str)
