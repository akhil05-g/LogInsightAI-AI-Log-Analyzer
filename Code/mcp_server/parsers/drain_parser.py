"""
Drain3 Template Mining Parser
Uses the Drain algorithm to extract log templates by clustering similar log messages.
"""

import re
from typing import Any


class DrainParser:
    """Parse logs using Drain3 template mining algorithm."""

    def __init__(self, sim_th: float = 0.4, depth: int = 4):
        self.sim_th = sim_th
        self.depth = depth
        self._miner = None

    def _get_miner(self):
        """Lazy-initialize the TemplateMiner."""
        if self._miner is None:
            from drain3 import TemplateMiner
            from drain3.template_miner_config import TemplateMinerConfig

            config = TemplateMinerConfig()
            config.drain_sim_th = self.sim_th
            config.drain_depth = self.depth
            config.masking = [
                {"regex_pattern": r"(\d+\.\d+\.\d+\.\d+)", "mask_with": "<IP>"},
                {"regex_pattern": r"(blk_-?\d+)", "mask_with": "<BLOCK>"},
                {"regex_pattern": r"(/[\w./\-_]+)", "mask_with": "<PATH>"},
                {"regex_pattern": r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})", "mask_with": "<TIMESTAMP>"},
                {"regex_pattern": r"(0x[0-9a-fA-F]+)", "mask_with": "<HEX>"},
                {"regex_pattern": r"(\b\d{5,}\b)", "mask_with": "<NUM>"},
            ]
            self._miner = TemplateMiner(config=config)
        return self._miner

    def parse(self, log_lines: list[str]) -> dict[str, Any]:
        """
        Parse log lines using Drain3 template mining.

        Args:
            log_lines: List of raw log line strings.

        Returns:
            Dictionary with templates and cluster assignments.
        """
        miner = self._get_miner()
        clusters = []
        line_clusters = []

        for i, line in enumerate(log_lines):
            line = line.strip()
            if not line:
                continue

            result = miner.add_log_message(line)
            line_clusters.append({
                "line_number": i + 1,
                "cluster_id": result.get("cluster_id", result.get("cluster_id", -1))
                    if isinstance(result, dict) else getattr(result, "cluster_id", -1),
                "template": result.get("template_mined", "")
                    if isinstance(result, dict) else getattr(result, "template_mined", ""),
            })

        # Extract unique templates with counts
        template_map: dict[int, dict] = {}
        for lc in line_clusters:
            cid = lc["cluster_id"]
            if cid not in template_map:
                template_map[cid] = {
                    "cluster_id": cid,
                    "template": lc["template"],
                    "count": 0,
                    "sample_lines": [],
                }
            template_map[cid]["count"] += 1
            if len(template_map[cid]["sample_lines"]) < 3:
                template_map[cid]["sample_lines"].append(lc["line_number"])

        templates = sorted(template_map.values(), key=lambda x: x["count"], reverse=True)

        return {
            "templates": templates,
            "total_clusters": len(templates),
            "total_lines_parsed": len(line_clusters),
            "line_clusters": line_clusters[:100],  # Limit to first 100 for response size
        }
