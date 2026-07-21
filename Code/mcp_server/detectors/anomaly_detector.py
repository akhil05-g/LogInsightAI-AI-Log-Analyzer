"""
PyOD Anomaly Detector
Uses Isolation Forest for statistical anomaly detection on extracted log features.
"""

import re
from typing import Any
from collections import Counter


class AnomalyDetector:
    """Detect anomalous patterns using PyOD Isolation Forest on extracted features."""

    def __init__(self, contamination: float = 0.05):
        self.contamination = contamination

    def _extract_features(self, log_lines: list[str]) -> list[dict[str, Any]]:
        """Extract numerical features from each log line."""
        features = []
        level_map = {"FATAL": 5, "CRITICAL": 5, "ERROR": 4, "WARN": 3, "WARNING": 3, "INFO": 2, "DEBUG": 1, "TRACE": 0}
        level_re = re.compile(r"\b(FATAL|CRITICAL|ERROR|WARN(?:ING)?|INFO|DEBUG|TRACE)\b", re.IGNORECASE)

        for line in log_lines:
            line = line.strip()
            if not line:
                continue

            level_match = level_re.search(line)
            level_val = level_map.get(level_match.group(1).upper(), 2) if level_match else 2

            features.append({
                "line_length": len(line),
                "word_count": len(line.split()),
                "level_numeric": level_val,
                "has_ip": 1 if re.search(r"\d+\.\d+\.\d+\.\d+", line) else 0,
                "has_exception": 1 if re.search(r"(?:exception|error|fail)", line, re.I) else 0,
                "digit_ratio": sum(c.isdigit() for c in line) / max(len(line), 1),
                "special_char_count": sum(1 for c in line if c in "[](){}:;!@#$%^&*"),
            })

        return features

    def detect(self, log_lines: list[str]) -> dict[str, Any]:
        """
        Run anomaly detection on log lines.

        Args:
            log_lines: List of raw log strings.

        Returns:
            Dictionary with anomaly results.
        """
        features = self._extract_features(log_lines)
        if len(features) < 20:
            return {
                "engine": "pyod",
                "anomalies": [],
                "message": "Too few log lines for statistical anomaly detection (need >= 20)",
            }

        try:
            import numpy as np
            from pyod.models.iforest import IForest

            feature_names = ["line_length", "word_count", "level_numeric", "has_ip", "has_exception", "digit_ratio", "special_char_count"]
            X = np.array([[f[k] for k in feature_names] for f in features])

            clf = IForest(contamination=self.contamination, random_state=42)
            clf.fit(X)

            labels = clf.labels_
            scores = clf.decision_scores_

            anomalies = []
            for i, (label, score) in enumerate(zip(labels, scores)):
                if label == 1:
                    anomalies.append({
                        "line_number": i + 1,
                        "anomaly_score": round(float(score), 4),
                        "content": log_lines[i].strip()[:200],
                        "features": features[i],
                    })

            anomalies.sort(key=lambda x: x["anomaly_score"], reverse=True)

            return {
                "engine": "pyod",
                "anomalies": anomalies[:50],
                "total_anomalies": len(anomalies),
                "total_lines_analyzed": len(features),
                "anomaly_rate": round(len(anomalies) / len(features) * 100, 2),
            }

        except ImportError:
            return {
                "engine": "pyod",
                "anomalies": [],
                "error": "PyOD not installed",
            }
        except Exception as e:
            return {
                "engine": "pyod",
                "anomalies": [],
                "error": str(e),
            }
