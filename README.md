<p align="center">
  <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%231A56DB'/%3E%3Cpath d='M8 22V10l4 4 4-6 4 6 4-4v12z' fill='%23fff' opacity='.9'/%3E%3C/svg%3E" width="64" alt="LogInsight AI Logo">
</p>

<h1 align="center">LogInsight AI</h1>

<p align="center">
  <strong>Enterprise Intelligent Log Analysis Platform — Powered by Gemini AI & MCP</strong>
</p>

<p align="center">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white">
  <img alt="Gemini" src="https://img.shields.io/badge/Gemini_2.5_Flash-Vertex_AI-4285F4?logo=google-cloud&logoColor=white">
  <img alt="MCP" src="https://img.shields.io/badge/MCP-Protocol-8B5CF6?logo=data:image/svg+xml;base64,&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-green">
</p>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [API Reference](#api-reference)
- [MCP Tools](#mcp-tools)
- [Detection Engines](#detection-engines)
- [Log Parsers](#log-parsers)
- [Frontend Dashboard](#frontend-dashboard)
- [Supported Log Formats](#supported-log-formats)
- [Configuration Reference](#configuration-reference)
- [Sample Logs](#sample-logs)

---

## Overview

**LogInsight AI** is a full-stack intelligent log analysis platform that combines multiple ML/AI detection engines with Google's Gemini 2.5 Flash LLM to provide comprehensive, enterprise-grade log file analysis. The system uses the **Model Context Protocol (MCP)** architecture to expose 5 specialized analysis tools that the LLM orchestrates in an agentic workflow.

### What It Does

1. **Upload** any system log file (`.log`, `.txt`)
2. **Parse** the log structure automatically using 4 parsing engines
3. **Detect** anomalies and errors using 5 detection engines (ML + rule-based)
4. **Correlate** events to identify cascading failures and root causes
5. **Predict** future failures based on error trend analysis
6. **Audit** logs for compliance (SOC2, HIPAA, PCI-DSS, ISO 27001, OWASP, GDPR)
7. **Summarize** all findings with an AI-generated natural language report

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Vanilla JS)                    │
│          Clinical Precision Design — Outfit + DM Mono            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────────┐   │
│  │  Upload   │ │  Log     │ │ Analysis │ │   AI Summary      │   │
│  │  Zone     │ │  Viewer  │ │ Dashboard│ │   (Markdown)      │   │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────────┘   │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTP (port 8000)
┌──────────────────────────▼───────────────────────────────────────┐
│                    BACKEND (FastAPI + Uvicorn)                    │
│  ┌────────────────┐  ┌─────────────────┐  ┌───────────────────┐ │
│  │  Routes         │  │  LLM            │  │  MCP Client       │ │
│  │  /api/logs      │  │  Orchestrator   │  │  (HTTP → MCP)     │ │
│  │  /api/analysis  │  │  (Gemini 2.5)   │  │                   │ │
│  └────────────────┘  └────────┬────────┘  └─────────┬─────────┘ │
└───────────────────────────────┼──────────────────────┼───────────┘
                                │ Tool calls           │ SSE
┌───────────────────────────────▼──────────────────────▼───────────┐
│                    MCP SERVER (FastMCP + SSE)                     │
│                         Port 8001                                │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────┐ ┌───────────┐ │
│  │ parse    │ │ detect   │ │ correlate│ │predict│ │ generate  │ │
│  │ _logs    │ │ _errors  │ │ _events  │ │_fails │ │ _report   │ │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──┬───┘ └─────┬─────┘ │
│       │             │            │           │           │       │
│  ┌────▼─────┐ ┌─────▼────────────▼───────────▼───┐ ┌────▼─────┐ │
│  │ Parsers  │ │      Detection Engines           │ │ Compliance│ │
│  │ • Drain3 │ │ • DeepLog LSTM (PyTorch)         │ │ • PII     │ │
│  │ • Grok   │ │ • PyOD Isolation Forest          │ │ • SOC2    │ │
│  │ • JSON   │ │ • Salesforce LogAI               │ │ • HIPAA   │ │
│  │ • Regex  │ │ • FlashText Keywords             │ │ • PCI-DSS │ │
│  └──────────┘ │ • Regex Pattern Matching         │ └──────────┘ │
│               └──────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

1. User uploads a `.log` file → **Backend** stores it in `uploads/`
2. User clicks "Run Analysis" → **Backend** sends log content to **LLM Orchestrator**
3. **Gemini 2.5 Flash** decides which MCP tools to call and in what order
4. **LLM Orchestrator** forwards tool calls to **MCP Server** via HTTP/SSE
5. **MCP Server** executes the tool (parse/detect/correlate/predict/report)
6. Results flow back: MCP → LLM → Backend → Frontend
7. Frontend renders structured results + AI-generated markdown summary

---

## Features

### 🔍 Multi-Engine Log Parsing
| Engine | Technology | Purpose |
|--------|-----------|---------|
| **Drain3** | Template Mining | Automatically extract log templates and patterns |
| **Grok** | Pattern Matching | Parse structured formats (Apache, syslog, etc.) |
| **JSON Parser** | JSON Extraction | Parse JSON-formatted log entries |
| **Regex Parser** | Regular Expressions | Extract timestamps, IPs, levels, and components |

### 🛡️ 5-Engine Anomaly Detection
| Engine | Type | Description |
|--------|------|-------------|
| **DeepLog LSTM** | Deep Learning | Self-supervised LSTM model that learns normal log sequences and flags deviations |
| **PyOD Isolation Forest** | Statistical ML | Outlier detection using line-length features and isolation forests |
| **Salesforce LogAI** | ML Pipeline | Template-based anomaly detection with K-Means clustering |
| **FlashText** | Rule-Based | Ultra-fast keyword scanning for 100+ error/warning/security terms |
| **Regex Patterns** | Rule-Based | Detects known error signatures: stack traces, OOM, HTTP errors, auth failures |

### 🔗 Event Correlation
- **Temporal clustering** — Groups events within configurable time windows
- **Root cause detection** — Identifies first error in cascade chains
- **Cascading failure analysis** — Tracks error propagation across components
- **Component impact scoring** — Ranks most affected system components

### 📈 Predictive Failure Analysis
- **Error trend analysis** — Detects accelerating, stable, or improving error rates
- **Per-component risk scoring** — Predicts which components will fail next
- **Confidence-scored predictions** — Each prediction has a risk level (LOW/MEDIUM/HIGH/CRITICAL)
- **Rate-of-change detection** — Catches subtle degradation patterns

### 📋 Compliance & Audit
| Standard | Checks Performed |
|----------|-----------------|
| **SOC2** | Audit trail completeness, access controls |
| **HIPAA** | PHI exposure, healthcare data in logs |
| **PCI-DSS** | Credit card numbers, CVVs, financial data |
| **ISO 27001** | Security event logging, incident detection |
| **OWASP** | SQL injection patterns, XSS attempts, auth failures |
| **GDPR** | PII exposure (emails, SSNs, phone numbers, API keys) |

### 🤖 AI-Powered Summary
- **Gemini 2.5 Flash** synthesizes all tool outputs into a structured report
- Agentic workflow — LLM decides tool execution order
- Markdown-formatted with sections: Overview, Key Findings, Anomaly Detection, Correlation, Predictions, Recommendations

---

## Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| Web Framework | **FastAPI** 0.115+ with async support |
| ASGI Server | **Uvicorn** with hot-reload |
| LLM | **Google Gemini 2.5 Flash** (Vertex AI) |
| MCP Protocol | **FastMCP** 2.0 + **MCP** SDK 1.0 |
| HTTP Client | **httpx** (async) |

### ML/AI Engines
| Library | Usage |
|---------|-------|
| **PyTorch** | DeepLog LSTM neural network |
| **PyOD** | Isolation Forest anomaly detection |
| **Salesforce LogAI** | ML log analysis pipeline |
| **scikit-learn** | Feature vectorization, clustering |
| **Drain3** | Log template mining (IBM Research) |
| **FlashText** | Aho-Corasick keyword extraction |
| **pygrok** | Grok pattern parsing |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | **Vanilla JS** (no build tools) |
| Styling | **CSS Custom Properties** + Clinical Precision design system |
| Fonts | **Outfit** (UI) + **DM Mono** (code) via Google Fonts |
| Animations | **Vanta.js** (landing page), **AOS** (scroll), **Typed.js** |
| Charts | **Canvas API** (donut chart) |

---

## Project Structure

```
GenAI 2 Project/
├── backend/                          # FastAPI backend server (port 8000)
│   ├── __init__.py
│   ├── config.py                     # Environment & path configuration
│   ├── main.py                       # FastAPI app entry point, CORS, lifespan
│   ├── models/
│   │   └── schemas.py                # Pydantic request/response models
│   ├── routes/
│   │   ├── logs.py                   # /api/logs/* — upload, list, read, delete
│   │   └── analysis.py              # /api/analysis/* — analyze, parse, detect
│   └── services/
│       ├── mcp_client.py            # HTTP client for MCP server communication
│       └── llm_orchestrator.py      # Gemini 2.5 agentic tool-calling loop
│
├── mcp_server/                       # MCP tool server (port 8001)
│   ├── __init__.py
│   ├── server.py                     # FastMCP server with 5 registered tools
│   ├── parsers/                      # Log parsing engines
│   │   ├── drain_parser.py          # Drain3 template mining
│   │   ├── grok_parser.py           # Grok pattern matching
│   │   ├── json_parser.py           # JSON log parsing
│   │   └── regex_parser.py          # Regex-based field extraction
│   ├── detectors/                    # Anomaly detection engines
│   │   ├── deeplog_detector.py      # DeepLog LSTM (PyTorch)
│   │   ├── anomaly_detector.py      # PyOD Isolation Forest
│   │   ├── logai_detector.py        # Salesforce LogAI ML pipeline
│   │   ├── keyword_detector.py      # FlashText keyword scanning
│   │   └── pattern_detector.py      # Regex pattern matching
│   └── tools/                        # MCP tool implementations
│       ├── parse_logs.py            # Orchestrates 4 parsers
│       ├── detect_errors.py         # Orchestrates 5 detection engines
│       ├── correlate_events.py      # Event correlation & root cause analysis
│       ├── predict_failures.py      # Predictive failure analytics
│       └── generate_report.py       # Compliance & audit report generation
│
├── frontend/                         # Static frontend (served by FastAPI)
│   ├── index.html                    # Single-page app — landing + dashboard
│   ├── css/
│   │   ├── styles.css               # Base design system (landing page + shared)
│   │   └── dashboard.css            # Clinical Precision dashboard overrides
│   └── js/
│       └── app.js                   # UI controller, file manager, renderers
│
├── sample_logs/                      # 16 pre-packaged log files for testing
│   ├── apache_sample.log
│   ├── hdfs_sample.log
│   ├── linux_sample.log
│   ├── openssh_sample.log
│   ├── windows_sample.log
│   ├── zookeeper_sample.log
│   └── loghub_*.log                  # LogHub benchmark datasets (2K lines each)
│
├── uploads/                          # User-uploaded log files (auto-created)
├── requirements.txt                  # Python dependencies
├── .env                              # Environment variables (API keys, ports)
├── .env.example                      # Template for environment configuration
└── README.md                         # This file
```

---

## Installation & Setup

### Prerequisites

- **Python 3.10+**
- **Google Cloud** account with Vertex AI API enabled
- **pip** package manager

### Step 1 — Clone & Install Dependencies

```bash
# Navigate to the project directory
cd "GenAI 2 Project"

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate   # macOS/Linux

# Install all dependencies
pip install -r requirements.txt
```

### Step 2 — Configure Environment Variables

Copy the example file and add your API keys:

```bash
copy .env.example .env
```

Edit `.env` with your settings:

```env
# Required — Google Cloud Vertex AI
GOOGLE_CLOUD_PROJECT=your-gcp-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=True

# LLM Model (default: gemini-2.5-flash)
GEMINI_MODEL=gemini-2.5-flash

# Server ports
MCP_SERVER_HOST=127.0.0.1
MCP_SERVER_PORT=8001
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000

# Application
UPLOAD_DIR=uploads
MAX_LOG_LINES=5000
```

### Step 3 — Optional: PyTorch for DeepLog LSTM

For the DeepLog LSTM deep learning engine, install PyTorch:

```bash
# CPU only (recommended for most users)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# CUDA GPU support (NVIDIA GPUs)
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

> **Note:** DeepLog will gracefully fall back if PyTorch is not installed. All other 4 detection engines work without it.

---

## Running the Application

You need to start **two servers** in separate terminals:

### Terminal 1 — MCP Server (port 8001)

```bash
cd "GenAI 2 Project"
cd mcp_server
python server.py
```

Expected output:
```
[MCP] LogInsight MCP Server starting on http://127.0.0.1:8001
[MCP] Registered 5 tools: parse_logs, detect_errors, correlate_events, predict_failures, generate_report
```

### Terminal 2 — Backend Server (port 8000)

```bash
cd "GenAI 2 Project"
python -m uvicorn backend.main:app --reload
```

Expected output:
```
INFO:     LogInsight AI Backend starting...
INFO:     Upload directory: uploads
INFO:     Frontend served from: frontend
INFO:     MCP server connected ✅
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Access the Application

Open your browser to: **http://localhost:8000**

---

## API Reference

### Log Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/logs/upload` | Upload a `.log` or `.txt` file |
| `GET` | `/api/logs/{log_id}` | Retrieve uploaded log content |
| `GET` | `/api/logs/list` | List all uploaded log files |
| `DELETE` | `/api/logs/{log_id}` | Delete an uploaded log file |
| `GET` | `/api/logs/samples` | List available sample log files |
| `POST` | `/api/logs/load-sample` | Load a sample log for analysis |

### Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/analysis/analyze` | Full AI analysis (all 5 tools + Gemini summary) |
| `POST` | `/api/analysis/parse` | Parse-only analysis (no LLM) |
| `POST` | `/api/analysis/detect` | Detection-only analysis (5 engines, no LLM) |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Backend health status |

### Request Examples

**Upload a log file:**
```bash
curl -X POST http://localhost:8000/api/logs/upload \
  -F "file=@sample_logs/apache_sample.log"
```

**Run full analysis:**
```bash
curl -X POST http://localhost:8000/api/analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{"log_id": "abc123", "analysis_type": "full"}'
```

---

## MCP Tools

The MCP server exposes 5 tools that Gemini orchestrates:

### 1. `parse_logs(log_content, log_format="auto")`
Parses raw log content into structured data.

**Engines used:** Drain3 → Grok → JSON → Regex

**Returns:**
- Log format detection (apache_access, syslog, hdfs, etc.)
- Template mining results (unique patterns)
- Level distribution (INFO, ERROR, WARN, etc.)
- Statistical summary (total lines, components, time range)

### 2. `detect_errors(log_content, sensitivity="medium")`
Runs 5 detection engines in parallel.

**Engines used:** DeepLog LSTM, PyOD, LogAI, FlashText, Regex

**Returns:**
- Keyword detections with line numbers and severity
- Pattern matches (stack traces, OOM, HTTP errors)
- ML anomaly scores per line
- LSTM sequence anomalies
- Health assessment (HEALTHY → CRITICAL)

### 3. `correlate_events(log_content, time_window_seconds=60)`
Correlates events across components.

**Returns:**
- Event groups clustered by time window
- Root cause candidates (first error in each cascade)
- Cascading failure chains
- Component impact ranking

### 4. `predict_failures(log_content, analysis_depth="standard")`
Analyzes error trends for predictive insights.

**Returns:**
- Overall risk level (LOW/MEDIUM/HIGH/CRITICAL)
- Per-component predictions with confidence scores
- Error rate trends (accelerating, stable, declining)
- Risk summary narrative

### 5. `generate_report(log_content, report_type="full")`
Audits logs against compliance standards.

**Returns:**
- Compliance score (0-100) and letter grade (A-F)
- PII detections (emails, SSNs, credit cards, API keys)
- Security findings per framework
- Audit trail completeness scores
- Actionable recommendations

---

## Detection Engines

### DeepLog LSTM
A self-supervised deep learning model based on the [DeepLog paper](https://www.cs.utah.edu/~mind/papers/deeplog.pdf) (Du et al., 2017).

- **Architecture:** LSTM neural network
- **Training:** Self-supervised on log template sequences
- **Detection:** Flags log lines whose template ID isn't in the top-K predictions
- **Config:** Window size (default 10), Top-K (default 9), Epochs (default 30)
- **Requirement:** PyTorch (optional — graceful fallback if missing)

### PyOD Isolation Forest
Statistical anomaly detection using feature engineering.

- **Features:** Line length, word count, digit ratio
- **Algorithm:** Isolation Forest (contamination = 5%)
- **Library:** [PyOD](https://pyod.readthedocs.io/)

### Salesforce LogAI
ML-powered log analysis pipeline.

- **Template Mining:** Drain3 for log pattern extraction
- **Clustering:** K-Means on TF-IDF vectorized templates
- **Anomaly Score:** Distance-based anomaly scoring
- **Library:** [LogAI](https://github.com/salesforce/logai)

### FlashText Keywords
Ultra-fast multi-keyword scanning.

- **100+ keywords** across categories: error, security, performance, network
- **Severity mapping:** Each keyword → critical/error/warning/info
- **Performance:** O(n) with Aho-Corasick algorithm

### Regex Pattern Detection
Known error signature matching.

- **Categories:** Stack traces, OOM/memory, HTTP errors (4xx/5xx), auth failures, connection issues, disk errors, timeout patterns
- **Output:** Matched text, line number, severity, category

---

## Log Parsers

### Drain3 (Template Mining)
- IBM Research's Drain algorithm for automatic log template extraction
- Groups similar log lines into templates with wildcards
- Example: `Connection from <*> port <*>` matches all SSH connection logs

### Grok (Pattern Matching)
- Logstash-compatible pattern matching
- Pre-defined patterns for Apache, syslog, and common formats
- Extracts structured fields: timestamp, level, component, message

### JSON Parser
- Parses JSON-formatted log entries
- Extracts nested fields
- Handles both single-line and multi-line JSON

### Regex Parser
- Regular expression-based field extraction
- Supports: syslog, Apache access/error, HDFS, Zookeeper, Windows Events
- Extracts: timestamp, IP addresses, log levels, components, PIDs

---

## Frontend Dashboard

The frontend is a **single-page application** with two views:

### Landing Page
- Animated Vanta.js wave background
- Hero section with typed.js text animation
- Feature cards with AOS scroll animations
- Stats row (99.9% accuracy, 10x faster, 4 engines, 6+ formats)

### Dashboard (Clinical Precision Design)
Inspired by **Linear.app**, **Vercel**, **Stripe**, and **Datadog**.

| Section | Description |
|---------|-------------|
| **Sidebar** | Navigation, engine selector, analysis controls |
| **Upload Zone** | Drag-and-drop or click-to-browse file upload |
| **Stats Grid** | 4-6 metric cards with DM Mono numbers and colored left accents |
| **Severity Chart** | Canvas donut chart with severity distribution |
| **Log Viewer** | Filterable, searchable raw log display with syntax highlighting |
| **Issues Table** | Alternating-row data table with severity badges |
| **Engine Metrics** | Performance table for all 5 detection engines |
| **Correlation** | Root cause candidates, cascading failures, component impact |
| **Prediction** | Risk assessment, trend analysis, at-risk components |
| **Compliance** | Grade badge, audit trail progress bars, PII findings |
| **AI Summary** | Markdown-rendered Gemini analysis with full formatting |


---

## Supported Log Formats

| Format | Auto-Detected | Example Source |
|--------|:---:|---------------|
| Apache Access Log | ✅ | Web servers (httpd, nginx) |
| Apache Error Log | ✅ | Web server errors |
| Syslog | ✅ | Linux system logs |
| HDFS | ✅ | Hadoop Distributed File System |
| Zookeeper | ✅ | Apache Zookeeper coordination |
| OpenSSH | ✅ | SSH authentication logs |
| Linux System | ✅ | `/var/log/messages`, `/var/log/syslog` |
| Windows Events | ✅ | Windows Event Log exports |
| OpenStack | ✅ | Cloud infrastructure logs |
| Spark | ✅ | Apache Spark job logs |
| Thunderbird | ✅ | HPC cluster logs |
| BGL (Blue Gene/L) | ✅ | Supercomputer logs |
| JSON Logs | ✅ | Structured JSON log entries |
| General Timestamp | ✅ | Any log with ISO/RFC timestamps |

---

## Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_CLOUD_PROJECT` | — | GCP project ID for Vertex AI |
| `GOOGLE_CLOUD_LOCATION` | `us-central1` | GCP region |
| `GOOGLE_GENAI_USE_VERTEXAI` | `True` | Use Vertex AI (vs API key) |
| `GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name |
| `MCP_SERVER_HOST` | `127.0.0.1` | MCP server bind address |
| `MCP_SERVER_PORT` | `8001` | MCP server port |
| `BACKEND_HOST` | `127.0.0.1` | Backend bind address |
| `BACKEND_PORT` | `8000` | Backend port |
| `UPLOAD_DIR` | `uploads` | Upload storage directory |
| `MAX_LOG_LINES` | `5000` | Maximum lines to process |
| `DEEPLOG_ENABLED` | `true` | Enable/disable DeepLog LSTM |
| `DEEPLOG_WINDOW_SIZE` | `10` | LSTM input sequence length |
| `DEEPLOG_TOP_K` | `9` | Top-K predictions for anomaly threshold |
| `DEEPLOG_NUM_EPOCHS` | `30` | LSTM training epochs |

---

## Sample Logs

The `sample_logs/` directory contains **16 log files** for testing:

### Quick Test Files (small)
| File | Lines | Source |
|------|-------|--------|
| `apache_sample.log` | ~30 | Apache access logs |
| `hdfs_sample.log` | ~80 | Hadoop HDFS logs |
| `linux_sample.log` | ~50 | Linux syslog |
| `openssh_sample.log` | ~40 | SSH authentication |
| `windows_sample.log` | ~30 | Windows events |
| `zookeeper_sample.log` | ~40 | Zookeeper coordination |

### LogHub Benchmark Files (2K lines each)
| File | Size | Source |
|------|------|--------|
| `loghub_apache_2k.log` | 167 KB | Apache web server |
| `loghub_bgl_2k.log` | 310 KB | Blue Gene/L supercomputer |
| `loghub_hdfs_2k.log` | 281 KB | Hadoop DFS |
| `loghub_linux_2k.log` | 212 KB | Linux system |
| `loghub_openssh_2k.log` | 220 KB | OpenSSH daemon |
| `loghub_openstack_2k.log` | 581 KB | OpenStack cloud |
| `loghub_spark_2k.log` | 192 KB | Apache Spark |
| `loghub_thunderbird_2k.log` | 318 KB | Thunderbird HPC |
| `loghub_windows_2k.log` | 279 KB | Windows events |
| `loghub_zookeeper_2k.log` | 273 KB | Zookeeper |

---

## Use Cases

### 1. DevOps Incident Investigation
Upload production logs during an outage → get root cause analysis, cascading failure chains, and affected components in seconds.

### 2. Security Audit
Scan logs for PII exposure, failed authentication attempts, SQL injection patterns, and compliance violations against SOC2/HIPAA/PCI-DSS.

### 3. Proactive Monitoring
Analyze logs periodically to detect accelerating error trends before they cause outages. The predictive engine identifies at-risk components.

### 4. Log Format Understanding
Upload unfamiliar logs → the parser auto-detects the format, extracts templates, and provides a structured breakdown of the log structure.

### 5. Compliance Reporting
Generate audit-ready compliance reports with grades, PII findings, and actionable recommendations for security teams.

---

<p align="center">
  <strong>Built with ❤️ using Gemini AI, FastAPI, and Model Context Protocol</strong>
</p>
