"""
LogInsight AI — LLM Orchestrator v2.0
Gemini Vertex AI client with agentic tool-calling loop.
Supports 5 MCP tools for comprehensive log analysis.
"""

import json
import time
import logging
from typing import Any, Optional

from backend.config import GOOGLE_CLOUD_API_KEY, GEMINI_MODEL, GROQ_API_KEY, GROQ_MODEL, LLM_PROVIDER
from backend.services.mcp_client import MCPClient

logger = logging.getLogger(__name__)

# Enhanced system prompt for Gemini v2.0
SYSTEM_PROMPT = """You are LogInsight AI v2.0, an expert enterprise log analysis platform powered by deep learning and multi-engine detection. You help IT operations, security, and SRE teams understand system logs through comprehensive AI-driven analysis.

You have access to 5 specialized analysis tools. Follow this multi-step workflow for full analysis:

**Step 1 — Parse:** Call parse_logs() to understand log structure, format, templates, and extract statistics.
**Step 2 — Detect:** Call detect_errors() to run 5 detection engines (LogAI ML, FlashText, PyOD, Regex, DeepLog LSTM).
**Step 3 — Correlate:** Call correlate_events() to identify cascading failures and root cause chains.
**Step 4 — Predict:** Call predict_failures() to analyze error trends and predict future failures.
**Step 5 — Compliance:** Call generate_report() to run security and compliance audit checks.

After all tools return results, synthesize everything into a comprehensive, well-structured analysis report. You MUST include ALL of the following sections in order. Do not skip any section. If a section has no findings, explicitly say "No issues detected in this area."

---

## Executive Summary
Provide a 4-6 bullet point overview for quick scanning. Each bullet must reference specific data:
- Overall system health verdict with supporting evidence
- Total issues found across all engines with severity breakdown
- Most critical finding with affected component and line numbers
- Error trend direction (from predictive analysis) with quantitative slope data
- Compliance posture summary (score, grade, top violation type)
- Single most urgent recommended action

---

## Log Overview
- Format detected, total lines analyzed, time range covered
- Number of unique templates discovered by Drain3
- Log level distribution (ERROR, WARN, INFO, DEBUG counts)
- Data quality assessment (are timestamps present? are components identifiable?)

---

## Key Findings (Top Issues)
Rank the top 5-10 most important issues by severity and impact. For EACH issue, provide:
1. **Issue title** — a short, descriptive name (e.g., "Database Connection Pool Exhaustion")
2. **Severity** — CRITICAL / ERROR / WARNING
3. **What happened** — plain English description of the issue
4. **Where** — specific line numbers, affected component(s)
5. **Impact** — what this means for the system/users
6. **Evidence** — quote the relevant log line(s)

---

## Error Analysis
- Breakdown by error category (connection failures, authentication errors, disk/IO issues, memory problems, timeout errors, application exceptions)
- For each category: count, percentage of total errors, affected components
- Error frequency pattern — are errors clustered or distributed?
- DeepLog LSTM sequence anomalies — which log lines broke expected patterns and why

---

## Anomaly Detection Results
- **PyOD Isolation Forest**: Number of statistical outliers, anomaly scores, which lines were flagged and why they are unusual
- **DeepLog LSTM**: Sequence anomalies detected, the normal pattern vs. what was observed
- **LogAI ML Pipeline**: ML-based anomaly findings with confidence scores
- Cross-engine agreement — which anomalies were flagged by multiple engines (higher confidence)

---

## Event Correlation & Root Cause Analysis
- Cascading failure chains identified (Component A error at line X led to Component B failure at line Y)
- Root cause candidates ranked by evidence strength
- Component dependency map inferred from the correlation
- Timeline of the failure cascade with line number references

---

## Predictive Analysis & Risk Assessment

### Error Trend
| Metric | Value |
|--------|-------|
| Trend Direction | INCREASING / STABLE / DECREASING |
| Slope | (numeric value from regression) |
| Confidence (R-squared) | (numeric value) |

### Component Risk Matrix
| Component | Error Count | Error Rate | Trend | Risk Level |
|-----------|------------|------------|-------|------------|
| (component name) | (count) | (percentage) | (direction) | HIGH/MEDIUM/LOW |

- Components at imminent risk of failure with justification
- Periodic failure patterns detected (e.g., errors every N lines)

---

## Security & Compliance Audit
- **Compliance Score**: X/100 (Grade: A/B/C/F)
- **PII Exposure**: Types found (emails, IPs, SSNs, API keys), count, affected lines
- **Security Violations**: Authentication failures, unencrypted connections, privilege escalation attempts
- **Audit Trail**: Completeness scores for session tracking, user identification, timestamps, action logging
- **Standards Referenced**: SOC2, HIPAA, PCI-DSS, ISO 27001, OWASP, GDPR

---

## Priority Action Items
Provide a numbered list ordered by urgency. For each action:
1. **[CRITICAL]** Action description — specific fix with component and line references
2. **[HIGH]** Action description
3. **[MEDIUM]** Action description

Include both:
- Immediate actions (fix within hours)
- Long-term improvements (fix within days/weeks)

---

## Overall Health Assessment

| Dimension | Rating | Evidence |
|-----------|--------|----------|
| System Stability | CRITICAL/UNHEALTHY/DEGRADED/FAIR/HEALTHY | (supporting data) |
| Security Posture | CRITICAL/HIGH/MEDIUM/LOW risk | (supporting data) |
| Error Trajectory | WORSENING/STABLE/IMPROVING | (trend slope and R-squared) |
| Compliance Status | COMPLIANT/NEEDS IMPROVEMENT/NON-COMPLIANT | (score and grade) |

**Final Verdict**: (One paragraph synthesizing all dimensions into an overall assessment with the single most important takeaway)

---

CRITICAL FORMATTING RULES:
- Be specific with line numbers and log content throughout. Cite evidence for every claim.
- Use Markdown tables where specified above — they MUST render correctly.
- Use `code formatting` for log lines, component names, and file paths.
- Use **bold** for emphasis on key findings.
- Use clear, professional language suitable for enterprise IT operations teams.
- Do NOT use emojis.
- Every section heading must use ## (double hash) markdown format.
- Separate sections with --- (horizontal rule) for visual clarity."""


class LLMOrchestrator:
    """Orchestrates Gemini or Groq with MCP tool calling."""

    def __init__(self, mcp_client: MCPClient):
        self.mcp_client = mcp_client
        self._client = None

    def _get_provider(self) -> str:
        return "groq" if LLM_PROVIDER == "groq" else "gemini"

    def _get_client(self):
        """Lazy-initialize the configured LLM client."""
        if self._client is None:
            provider = self._get_provider()
            if provider == "groq":
                from groq import Groq

                self._client = Groq(api_key=GROQ_API_KEY)
            else:
                from google import genai

                self._client = genai.Client(
                    vertexai=True,
                    api_key=GOOGLE_CLOUD_API_KEY,
                )
        return self._client

    def _get_tool_declarations(self):
        """Define tool schemas for Gemini function calling (5 tools)."""
        from google.genai import types

        parse_logs_tool = types.FunctionDeclaration(
            name="parse_logs",
            description="Parse system log content to extract structured information, templates, and statistics. Uses Drain3 template mining, Grok patterns, JSON parsing, and regex extraction.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "log_content": types.Schema(
                        type="STRING",
                        description="The raw log file content as a string.",
                    ),
                    "log_format": types.Schema(
                        type="STRING",
                        description='Expected log format: "auto", "syslog", "apache_access", "apache_error", "hdfs", "zookeeper", "json".',
                    ),
                },
                required=["log_content"],
            ),
        )

        detect_errors_tool = types.FunctionDeclaration(
            name="detect_errors",
            description="Detect errors, anomalies, and security issues using 5 engines: LogAI ML, FlashText keywords, PyOD Isolation Forest, Regex patterns, and DeepLog LSTM deep learning.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "log_content": types.Schema(
                        type="STRING",
                        description="The raw log file content as a string.",
                    ),
                    "sensitivity": types.Schema(
                        type="STRING",
                        description='Detection sensitivity: "low", "medium", or "high".',
                    ),
                },
                required=["log_content"],
            ),
        )

        correlate_events_tool = types.FunctionDeclaration(
            name="correlate_events",
            description="Correlate log events across components to identify cascading failures, root cause chains, and event clusters. Analyzes temporal proximity and component relationships.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "log_content": types.Schema(
                        type="STRING",
                        description="The raw log file content as a string.",
                    ),
                    "time_window_seconds": types.Schema(
                        type="INTEGER",
                        description="Maximum seconds between events to consider them correlated (default: 60).",
                    ),
                },
                required=["log_content"],
            ),
        )

        predict_failures_tool = types.FunctionDeclaration(
            name="predict_failures",
            description="Analyze error frequency trends to predict potential future failures. Detects accelerating error rates, periodic patterns, and generates per-component risk predictions.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "log_content": types.Schema(
                        type="STRING",
                        description="The raw log file content as a string.",
                    ),
                    "analysis_depth": types.Schema(
                        type="STRING",
                        description='Analysis depth: "quick", "standard", or "deep".',
                    ),
                },
                required=["log_content"],
            ),
        )

        generate_report_tool = types.FunctionDeclaration(
            name="generate_report",
            description="Generate a compliance and security audit report. Checks for PII exposure, security compliance (SOC2, HIPAA, PCI-DSS), audit trail completeness, and data handling practices.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "log_content": types.Schema(
                        type="STRING",
                        description="The raw log file content as a string.",
                    ),
                    "report_type": types.Schema(
                        type="STRING",
                        description='Report type: "full", "security", or "pii".',
                    ),
                },
                required=["log_content"],
            ),
        )

        return types.Tool(
            function_declarations=[
                parse_logs_tool,
                detect_errors_tool,
                correlate_events_tool,
                predict_failures_tool,
                generate_report_tool,
            ]
        )

    async def analyze(
        self,
        log_content: str,
        analysis_type: str = "full",
        sensitivity: str = "medium",
        log_format: str = "auto",
    ) -> dict[str, Any]:
        """
        Run the full analysis pipeline with Gemini + MCP tools.

        Args:
            log_content: Raw log content.
            analysis_type: "full", "parse", or "detect".
            sensitivity: Detection sensitivity.
            log_format: Expected log format.

        Returns:
            Dictionary with tool results and ai_summary.
        """
        result = {
            "parse_result": None,
            "detection_result": None,
            "correlation_result": None,
            "prediction_result": None,
            "compliance_result": None,
            "ai_summary": None,
            "engines_used": [],
            "timing": {},
        }

        # For parse-only or detect-only, call tools directly
        if analysis_type == "parse":
            t0 = time.time()
            result["parse_result"] = await self.mcp_client.call_tool(
                "parse_logs", {"log_content": log_content, "log_format": log_format}
            )
            result["timing"]["parse_logs"] = round(time.time() - t0, 2)
            result["engines_used"] = ["drain3", "grok", "json_parser", "regex"]
            return result

        if analysis_type == "detect":
            t0 = time.time()
            result["detection_result"] = await self.mcp_client.call_tool(
                "detect_errors", {"log_content": log_content, "sensitivity": sensitivity}
            )
            result["timing"]["detect_errors"] = round(time.time() - t0, 2)
            result["engines_used"] = ["logai", "flashtext", "pyod", "regex_patterns", "deeplog_lstm"]
            return result

        # Full analysis: use provider-specific path
        if self._get_provider() == "groq":
            ai_result = await self._run_groq_summary(log_content)
        else:
            ai_result = await self._run_agentic_loop(log_content)
        result.update(ai_result)

        # Generate natural language explanations for each detected issue
        if result.get("detection_result"):
            try:
                t0 = time.time()
                explanations = await self._explain_issues(result["detection_result"])
                result["issue_explanations"] = explanations
                result["timing"]["explain_issues"] = round(time.time() - t0, 2)
                logger.info(f"Generated {len(explanations)} issue explanations")
            except Exception as e:
                logger.warning(f"Issue explanation generation failed: {e}")
                result["issue_explanations"] = []

        return result

    async def _run_agentic_loop(self, log_content: str) -> dict[str, Any]:
        """Run the Gemini agentic tool-calling loop."""
        if self._get_provider() == "groq":
            return await self._run_groq_summary(log_content)

        from google.genai import types

        client = self._get_client()
        tools = self._get_tool_declarations()

        # Truncate log content if too large for context
        max_chars = 100000
        truncated = log_content[:max_chars]
        if len(log_content) > max_chars:
            truncated += f"\n\n... [TRUNCATED: showing {max_chars} of {len(log_content)} characters]"

        user_message = f"""Analyze the following system logs comprehensively using ALL available tools.

Follow this workflow:
1. parse_logs() — understand structure and templates
2. detect_errors() — run all 5 detection engines including DeepLog LSTM
3. correlate_events() — find cascading failures and root causes
4. predict_failures() — analyze trends and predict future issues
5. generate_report() — run compliance and security audit

After gathering all results, provide a detailed synthesis report.

```
{truncated}
```"""

        contents = [types.Content(role="user", parts=[types.Part(text=user_message)])]

        result = {
            "parse_result": None,
            "detection_result": None,
            "correlation_result": None,
            "prediction_result": None,
            "compliance_result": None,
            "ai_summary": None,
            "engines_used": [],
            "timing": {},
        }

        # Tool result key mapping
        tool_result_map = {
            "parse_logs": "parse_result",
            "detect_errors": "detection_result",
            "correlate_events": "correlation_result",
            "predict_failures": "prediction_result",
            "generate_report": "compliance_result",
        }

        # Agentic loop: keep calling until we get a text response
        max_iterations = 10  # Increased for 5 tools
        for iteration in range(max_iterations):
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    tools=[tools],
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.3,
                ),
            )

            # Check if response has function calls
            if response.candidates and response.candidates[0].content.parts:
                has_function_call = False
                function_responses = []

                for part in response.candidates[0].content.parts:
                    if part.function_call:
                        has_function_call = True
                        fc = part.function_call
                        logger.info(f"🔧 Gemini calling tool [{iteration+1}/{max_iterations}]: {fc.name}")

                        # Execute tool via MCP
                        tool_args = dict(fc.args) if fc.args else {}
                        # ALWAYS override log_content with the FULL original
                        # Gemini truncates/summarizes log_content in its function
                        # calls, so we must inject the complete content.
                        tool_args["log_content"] = log_content

                        t0 = time.time()
                        tool_result = await self.mcp_client.call_tool(fc.name, tool_args)
                        elapsed = round(time.time() - t0, 2)
                        result["timing"][fc.name] = elapsed
                        logger.info(f"   ✅ {fc.name} completed in {elapsed}s")

                        # Store results
                        result_key = tool_result_map.get(fc.name)
                        if result_key:
                            result[result_key] = tool_result

                        # Track engines used
                        if fc.name == "detect_errors":
                            result["engines_used"].extend(["logai", "flashtext", "pyod", "regex_patterns", "deeplog_lstm"])
                        elif fc.name == "parse_logs":
                            result["engines_used"].extend(["drain3", "grok", "json_parser", "regex"])
                        else:
                            result["engines_used"].append(fc.name)

                        # Add to conversation for Gemini
                        function_responses.append(
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=fc.name,
                                    response={"result": json.dumps(tool_result, default=str)[:50000]},
                                )
                            )
                        )

                if has_function_call:
                    # Add assistant message and tool responses
                    contents.append(response.candidates[0].content)
                    contents.append(types.Content(role="user", parts=function_responses))
                    continue

                # If we have text parts, extract the summary
                for part in response.candidates[0].content.parts:
                    if part.text:
                        result["ai_summary"] = (result.get("ai_summary") or "") + part.text
                break
            else:
                # No useful response
                if response.text:
                    result["ai_summary"] = response.text
                break

        if not result["ai_summary"]:
            result["ai_summary"] = "Analysis completed. See tool results for details."

        # Deduplicate engines
        result["engines_used"] = list(dict.fromkeys(result["engines_used"]))

        return result

    async def _run_groq_summary(self, log_content: str) -> dict[str, Any]:
        """Run the analysis pipeline via Groq using MCP tools and a single synthesis prompt."""
        result = {
            "parse_result": None,
            "detection_result": None,
            "correlation_result": None,
            "prediction_result": None,
            "compliance_result": None,
            "ai_summary": None,
            "engines_used": [],
            "timing": {},
        }

        tool_calls = [
            ("parse_logs", {"log_content": log_content, "log_format": "auto"}, "parse_result", ["drain3", "grok", "json_parser", "regex"]),
            ("detect_errors", {"log_content": log_content, "sensitivity": "medium"}, "detection_result", ["logai", "flashtext", "pyod", "regex_patterns", "deeplog_lstm"]),
            ("correlate_events", {"log_content": log_content, "time_window_seconds": 60}, "correlation_result", ["correlate_events"]),
            ("predict_failures", {"log_content": log_content, "analysis_depth": "standard"}, "prediction_result", ["predict_failures"]),
            ("generate_report", {"log_content": log_content, "report_type": "full"}, "compliance_result", ["generate_report"]),
        ]

        for tool_name, tool_args, result_key, engines in tool_calls:
            t0 = time.time()
            tool_result = await self.mcp_client.call_tool(tool_name, tool_args)
            result["timing"][tool_name] = round(time.time() - t0, 2)
            result[result_key] = tool_result
            result["engines_used"].extend(engines)

        prompt = f"""You are LogInsight AI. Synthesize the following MCP analysis results into a concise, executive-ready report.

Parse result:
{json.dumps(result['parse_result'], indent=2, default=str)}

Detection result:
{json.dumps(result['detection_result'], indent=2, default=str)}

Correlation result:
{json.dumps(result['correlation_result'], indent=2, default=str)}

Prediction result:
{json.dumps(result['prediction_result'], indent=2, default=str)}

Compliance result:
{json.dumps(result['compliance_result'], indent=2, default=str)}

Write a clear summary with key findings, severity, likely root cause, and recommended next steps.
"""

        from groq import Groq

        client = Groq(api_key=GROQ_API_KEY)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            temperature=0.3,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
        result["ai_summary"] = response.choices[0].message.content or "Analysis completed."
        result["engines_used"] = list(dict.fromkeys(result["engines_used"]))
        return result

    async def _explain_issues(
        self, detection_result: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Use Gemini to generate natural language explanations for detected issues.

        Takes the top issues from detection_result (keyword + pattern + anomaly
        detections) and asks Gemini to explain each one in plain English.

        Returns:
            List of dicts with keys:
              line_number, severity, raw_text, explanation, impact, fix
        """
        from google.genai import types

        # Collect top issues from all engines
        issues: list[dict[str, Any]] = []
        sev_rank = {"critical": 0, "error": 1, "warning": 2, "info": 3}

        # From keyword detection
        kw = detection_result.get("keyword_detection", {})
        for d in kw.get("detections", []):
            issues.append({
                "line_number": d.get("line_number", 0),
                "severity": d.get("severity", "info"),
                "raw_text": d.get("context", d.get("matched_text", ""))[:300],
                "engine": "FlashText Keywords",
            })

        # From pattern detection
        pt = detection_result.get("pattern_detection", {})
        for d in pt.get("matches", []):
            issues.append({
                "line_number": d.get("line_number", 0),
                "severity": d.get("severity", "info"),
                "raw_text": d.get("context", d.get("matched_text", ""))[:300],
                "engine": "Regex Patterns",
            })

        # From LogAI anomalies
        logai = detection_result.get("logai_analysis", {})
        for d in logai.get("anomalies", []):
            issues.append({
                "line_number": d.get("line_number", 0),
                "severity": "warning",
                "raw_text": d.get("content", d.get("log_line", ""))[:300],
                "engine": "LogAI ML",
            })

        # From PyOD anomalies
        pyod = detection_result.get("anomaly_detection", {})
        for d in pyod.get("anomalies", []):
            issues.append({
                "line_number": d.get("line_number", 0),
                "severity": "warning",
                "raw_text": d.get("content", d.get("log_line", ""))[:300],
                "engine": "PyOD IsolationForest",
            })

        # From DeepLog LSTM anomalies
        dl = detection_result.get("deeplog_detection", {})
        for d in dl.get("anomalies", []):
            issues.append({
                "line_number": d.get("line_number", 0),
                "severity": "warning",
                "raw_text": d.get("content", d.get("log_line", ""))[:300],
                "engine": "DeepLog LSTM",
            })

        if not issues:
            return []

        # Deduplicate by line number — keep highest severity per line
        unique_map: dict[int, dict] = {}
        for iss in issues:
            ln = iss["line_number"]
            if ln == 0:
                continue
            if ln not in unique_map or (
                sev_rank.get(iss["severity"], 3)
                < sev_rank.get(unique_map[ln]["severity"], 3)
            ):
                unique_map[ln] = iss

        # Sort by severity, take top 30
        sorted_issues = sorted(
            unique_map.values(),
            key=lambda x: sev_rank.get(x["severity"], 3),
        )[:30]

        # Build the prompt for Gemini
        issues_text = "\n".join(
            f"{i+1}. [Line {iss['line_number']}] [{iss['severity'].upper()}] "
            f"(Engine: {iss['engine']}) Log: {iss['raw_text'][:200]}"
            for i, iss in enumerate(sorted_issues)
        )

        explain_prompt = f"""You are an expert log analysis AI. Below is a list of issues detected in system logs by automated detection engines.

For EACH issue, provide a JSON array response. Each element must have these exact keys:
- "line_number": (integer) the line number from the input
- "severity": (string) the severity level from the input
- "explanation": (string) A clear, plain-English explanation of what happened in 1-2 sentences. Avoid jargon. Explain it as if briefing a senior engineer.
- "impact": (string) Why this matters — what could go wrong if ignored. 1 sentence.
- "fix": (string) A specific, actionable recommendation to resolve or mitigate this. 1-2 sentences.

Do NOT include any markdown formatting, code fences, or extra text. Return ONLY a valid JSON array.

Detected Issues:
{issues_text}"""

        try:
            if self._get_provider() == "groq":
                from groq import Groq

                client = Groq(api_key=GROQ_API_KEY)
                response = client.chat.completions.create(
                    model=GROQ_MODEL,
                    temperature=0.2,
                    messages=[{"role": "user", "content": explain_prompt}],
                )
                response_text = (response.choices[0].message.content or "[]").strip()
            else:
                client = self._get_client()
                response = client.models.generate_content(
                    model=GEMINI_MODEL,
                    contents=[types.Content(
                        role="user",
                        parts=[types.Part(text=explain_prompt)],
                    )],
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        response_mime_type="application/json",
                    ),
                )

                response_text = response.text.strip()

            explanations = json.loads(response_text)

            if not isinstance(explanations, list):
                logger.warning("Gemini returned non-list for issue explanations")
                return []

            # Merge raw_text back into explanations
            line_to_raw = {iss["line_number"]: iss["raw_text"] for iss in sorted_issues}
            for exp in explanations:
                ln = exp.get("line_number", 0)
                if ln in line_to_raw:
                    exp["raw_text"] = line_to_raw[ln]
                if "raw_text" not in exp:
                    exp["raw_text"] = ""

            return explanations

        except Exception as e:
            logger.error(f"Gemini issue explanation failed: {e}")
            # Fallback: return issues with generic explanations
            return [
                {
                    "line_number": iss["line_number"],
                    "severity": iss["severity"],
                    "raw_text": iss["raw_text"],
                    "explanation": f"A {iss['severity']}-level event was detected at line {iss['line_number']} by the {iss['engine']} engine.",
                    "impact": "This issue may indicate a system problem that requires investigation.",
                    "fix": "Review the log line and surrounding context to determine the appropriate corrective action.",
                }
                for iss in sorted_issues
            ]
