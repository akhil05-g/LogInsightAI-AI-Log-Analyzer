"""
DeepLog — LSTM-Based Log Anomaly Detection Engine.

Reference: Du et al., "DeepLog: Anomaly Detection and Diagnosis from System Logs
through Deep Learning", ACM CCS 2017.

How it works:
  1. Takes Drain3 template IDs as input (log key sequence).
  2. Trains a 2-layer LSTM to predict the next template in the sequence.
  3. If the actual next template is NOT in the model's top-k predictions,
     that log line is flagged as anomalous.
  4. Training is self-supervised — the model learns from the log itself.

This is the gold-standard deep learning approach for log anomaly detection.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class DeepLogDetector:
    """LSTM-based sequence anomaly detector using the DeepLog approach."""

    def __init__(
        self,
        window_size: int = 10,
        top_k: int = 9,
        hidden_size: int = 64,
        num_layers: int = 2,
        num_epochs: int = 30,
        learning_rate: float = 0.001,
        batch_size: int = 64,
    ):
        self.window_size = window_size
        self.top_k = top_k
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.num_epochs = num_epochs
        self.learning_rate = learning_rate
        self.batch_size = batch_size
        self._available = None

    def _check_available(self) -> bool:
        """Check if PyTorch is installed and importable."""
        if self._available is None:
            try:
                import torch
                import torch.nn as nn
                self._available = True
            except Exception:
                # Catch ALL exceptions — torch import can crash with
                # KeyboardInterrupt, OSError, compilation errors, etc.
                self._available = False
                logger.warning("PyTorch import failed — DeepLog LSTM disabled")
        return self._available

    def detect(
        self, log_lines: list[str], template_ids: list[int] | None = None
    ) -> dict[str, Any]:
        """
        Run DeepLog anomaly detection.

        Args:
            log_lines: Raw log lines (used for context in results).
            template_ids: Sequence of Drain3 template IDs for each log line.
                          If None, falls back to line-length hashing.

        Returns:
            Dictionary with DeepLog anomaly detection results.
        """
        if not self._check_available():
            return {
                "engine": "deeplog",
                "available": False,
                "message": "PyTorch not installed. Install with: pip install torch",
                "anomalies": [],
                "anomaly_count": 0,
            }

        if len(log_lines) < self.window_size + 10:
            return {
                "engine": "deeplog",
                "available": True,
                "anomalies": [],
                "anomaly_count": 0,
                "message": f"Too few log lines for DeepLog (need >= {self.window_size + 10})",
            }

        try:
            return self._run_detection(log_lines, template_ids)
        except BaseException as e:
            # Catch BaseException to handle KeyboardInterrupt from torch import
            logger.error(f"DeepLog detection failed: {e}")
            return {
                "engine": "deeplog",
                "available": True,
                "error": str(e),
                "anomalies": [],
                "anomaly_count": 0,
            }

    def _generate_template_ids(self, log_lines: list[str]) -> list[int]:
        """
        Fallback: generate pseudo-template IDs using simple hashing
        when Drain3 template IDs are not provided.
        """
        from collections import OrderedDict

        template_map: dict[str, int] = OrderedDict()
        ids = []

        for line in log_lines:
            # Normalize: strip timestamps and numbers for grouping
            import re
            normalized = re.sub(r"\d+", "<NUM>", line.strip())
            normalized = re.sub(r"\s+", " ", normalized)[:100]

            if normalized not in template_map:
                template_map[normalized] = len(template_map)
            ids.append(template_map[normalized])

        return ids

    def _run_detection(
        self, log_lines: list[str], template_ids: list[int] | None
    ) -> dict[str, Any]:
        """Execute the full DeepLog LSTM pipeline."""
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, TensorDataset

        # Step 1: Get template ID sequence
        if template_ids is None or len(template_ids) != len(log_lines):
            template_ids = self._generate_template_ids(log_lines)

        num_classes = max(template_ids) + 1
        if num_classes < 2:
            return {
                "engine": "deeplog",
                "available": True,
                "anomalies": [],
                "anomaly_count": 0,
                "message": "Only 1 unique template found — no sequence diversity to analyze",
                "num_templates": num_classes,
            }

        # Step 2: Create sliding window sequences
        sequences = []
        labels = []
        for i in range(len(template_ids) - self.window_size):
            seq = template_ids[i : i + self.window_size]
            label = template_ids[i + self.window_size]
            sequences.append(seq)
            labels.append(label)

        if len(sequences) < 10:
            return {
                "engine": "deeplog",
                "available": True,
                "anomalies": [],
                "anomaly_count": 0,
                "message": "Not enough sequences for training",
            }

        X = torch.tensor(sequences, dtype=torch.long)
        y = torch.tensor(labels, dtype=torch.long)

        # Step 3: Define LSTM model
        class DeepLogModel(nn.Module):
            def __init__(self, num_classes, hidden_size, num_layers):
                super().__init__()
                self.embedding = nn.Embedding(num_classes, hidden_size)
                self.lstm = nn.LSTM(
                    hidden_size, hidden_size, num_layers, batch_first=True, dropout=0.1
                )
                self.fc = nn.Linear(hidden_size, num_classes)

            def forward(self, x):
                emb = self.embedding(x)
                out, _ = self.lstm(emb)
                out = self.fc(out[:, -1, :])
                return out

        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = DeepLogModel(num_classes, self.hidden_size, self.num_layers).to(device)

        # Step 4: Train the model (self-supervised)
        dataset = TensorDataset(X, y)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True)
        optimizer = torch.optim.Adam(model.parameters(), lr=self.learning_rate)
        criterion = nn.CrossEntropyLoss()

        model.train()
        for epoch in range(self.num_epochs):
            total_loss = 0
            for batch_x, batch_y in loader:
                batch_x, batch_y = batch_x.to(device), batch_y.to(device)
                optimizer.zero_grad()
                output = model(batch_x)
                loss = criterion(output, batch_y)
                loss.backward()
                optimizer.step()
                total_loss += loss.item()

        # Step 5: Detect anomalies (inference)
        model.eval()
        anomalies = []
        with torch.no_grad():
            for i in range(len(sequences)):
                seq_tensor = torch.tensor([sequences[i]], dtype=torch.long).to(device)
                output = model(seq_tensor)
                probs = torch.softmax(output, dim=1)
                top_k_values, top_k_indices = torch.topk(probs, min(self.top_k, num_classes))

                actual = labels[i]
                predicted_set = top_k_indices[0].tolist()

                if actual not in predicted_set:
                    line_idx = i + self.window_size
                    confidence = 1.0 - probs[0][actual].item()
                    anomalies.append({
                        "line_number": line_idx + 1,
                        "content": log_lines[line_idx].strip()[:200],
                        "actual_template_id": actual,
                        "predicted_template_ids": predicted_set[:5],
                        "confidence": round(confidence, 4),
                        "anomaly_type": "sequence_deviation",
                    })

        # Sort by confidence (highest first)
        anomalies.sort(key=lambda x: x["confidence"], reverse=True)

        return {
            "engine": "deeplog",
            "available": True,
            "model": "LSTM (2-layer)",
            "device": str(device),
            "anomalies": anomalies[:50],
            "anomaly_count": len(anomalies),
            "total_lines_analyzed": len(log_lines),
            "num_templates": num_classes,
            "window_size": self.window_size,
            "top_k": self.top_k,
            "training_sequences": len(sequences),
            "anomaly_rate": round(len(anomalies) / max(len(sequences), 1) * 100, 2),
        }
