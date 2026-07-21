"""
Salesforce LogAI Detector — PRIMARY detection engine.
Uses LogAI's programmatic API for log parsing and anomaly detection.
"""

import os
import tempfile
from typing import Any


class LogAIDetector:
    """Primary anomaly detector using Salesforce LogAI library."""

    def __init__(self):
        self._available = None

    def _check_available(self) -> bool:
        """Check if LogAI is installed and available."""
        if self._available is None:
            try:
                import logai
                self._available = True
            except ImportError:
                self._available = False
        return self._available

    def detect(self, log_lines: list[str]) -> dict[str, Any]:
        """
        Run LogAI anomaly detection pipeline on log lines.

        Args:
            log_lines: List of raw log strings.

        Returns:
            Dictionary with anomaly detection results.
        """
        if not self._check_available():
            return {
                "engine": "logai",
                "available": False,
                "message": "LogAI library not installed. Install with: pip install logai",
                "anomalies": [],
            }

        try:
            return self._run_detection(log_lines)
        except Exception as e:
            return {
                "engine": "logai",
                "available": True,
                "error": str(e),
                "anomalies": [],
                "fallback": True,
            }

    def _run_detection(self, log_lines: list[str]) -> dict[str, Any]:
        """Execute the full LogAI detection pipeline."""
        from logai.dataloader.data_loader import FileDataLoader, DataLoaderConfig
        from logai.information_extraction.log_parser import LogParser, LogParserConfig

        import pandas as pd

        # Sanitize log lines — strip whitespace, remove empty lines
        clean_lines = []
        for line in log_lines:
            s = str(line).rstrip() if not isinstance(line, float) else ""
            if s:
                clean_lines.append(s)

        if len(clean_lines) < 5:
            return {
                "engine": "logai",
                "available": True,
                "anomalies": [],
                "anomaly_count": 0,
                "message": "Too few valid log lines for LogAI analysis",
            }

        # Write log lines to a temp CSV file for LogAI's file-based loader
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as f:
            f.write("logline\n")
            for line in clean_lines:
                # Escape quotes for CSV
                escaped = line.replace('"', '""')
                f.write(f'"{escaped}"\n')
            temp_path = f.name

        try:
            # Step 1: Load data using CSV format with proper config
            loader_config = DataLoaderConfig(
                filepath=temp_path,
                log_type="csv",
                dimensions={"body": ["logline"]},
            )
            loader = FileDataLoader(loader_config)
            logrecord = loader.load_data()

            # Step 2: Extract body series and sanitize (drop NaN, convert floats to str)
            from logai.utils import constants
            body_series = logrecord.body[constants.LOGLINE_NAME]

            # Critical fix: drop NaN rows and ensure all values are strings
            body_series = body_series.dropna()
            body_series = body_series.astype(str)
            body_series = body_series[body_series.str.strip().str.len() > 0]

            if len(body_series) < 5:
                return {
                    "engine": "logai",
                    "available": True,
                    "anomalies": [],
                    "anomaly_count": 0,
                    "message": "Too few valid entries after LogAI parsing",
                }

            # Step 3: Parse with Drain algorithm
            parser_config = LogParserConfig.from_dict({
                "parsing_algorithm": "drain",
            })
            parser = LogParser(parser_config)
            parsed_result = parser.parse(body_series)

            # Step 4: Anomaly detection using simple feature-based IsolationForest
            anomalies = []
            anomaly_scores = []
            try:
                from sklearn.ensemble import IsolationForest
                import numpy as np

                # Use line lengths and token counts as features
                loglines_list = body_series.tolist()
                features = np.array([
                    [len(str(b)), len(str(b).split())]
                    for b in loglines_list
                ])

                if len(features) > 10:  # Need minimum samples
                    clf = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
                    clf.fit(features)
                    predictions = clf.predict(features)
                    scores = clf.decision_function(features)

                    for i, (pred, score) in enumerate(zip(predictions, scores)):
                        if pred == -1:  # IsolationForest: -1 = anomaly
                            anomalies.append({
                                "line_number": i + 1,
                                "content": str(loglines_list[i])[:200],
                                "anomaly_score": round(float(score), 4),
                            })
                            anomaly_scores.append(float(score))
            except Exception:
                pass  # Anomaly detection is optional

            # Build result — extract templates from parsed DataFrame
            templates = []
            if "parsed_logline" in parsed_result.columns:
                template_counts: dict[str, int] = {}
                for tmpl in parsed_result["parsed_logline"].tolist():
                    t = str(tmpl)
                    template_counts[t] = template_counts.get(t, 0) + 1
                templates = [
                    {"template": t, "count": c}
                    for t, c in sorted(template_counts.items(), key=lambda x: -x[1])
                ]

            return {
                "engine": "logai",
                "available": True,
                "anomalies": anomalies[:50],
                "anomaly_count": len(anomalies),
                "templates_found": len(templates),
                "templates": templates[:30],
                "total_lines_analyzed": len(log_lines),
                "avg_anomaly_score": (
                    round(sum(anomaly_scores) / len(anomaly_scores), 4)
                    if anomaly_scores else 0.0
                ),
            }
        finally:
            try:
                os.unlink(temp_path)
            except OSError:
                pass
