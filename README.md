
---

# Hierarchical Multi-Agent Repository and PDF Document Auditor

**Author:** Amare Kassa
**Date:** February 28, 2026

---

## Overview

The **Automaton Auditor** is a deterministic, hierarchical multi-agent system designed to perform automated audits of software repositories and associated documentation. It generates structured evidence-backed technical reports, following a **digital courtroom architecture**:

**Detectives → Judges → Chief Justice**

- Detectives gather factual evidence (git history, PDF content, code structure, images)
- Judges reason over the collected evidence
- Chief Justice synthesizes verdicts and remediation suggestions

The system is **designed for production-grade execution**, supporting parallelism, offline-safe operation, and reproducibility.

---

## Repository Structure

```text
.
├── src/                 # Core source code
│   ├── graph.py         # LangGraph orchestration
│   ├── nodes/           # Detectives, Judges, ChiefJustice
│   ├── tools/           # AST, git, PDF, and vision tools
├── reports/             # Generated audit reports
├── rubric/              # Machine-readable evaluation rubrics
├── .env.examples        # Example environment configuration
├── Dockerfile           # Optional containerized execution
├── Makefile             # Build/test utilities
└── README.md            # This file
```

---

## Prerequisites

1. **Python 3.10+**
2. **uv package manager** installed
3. **Git** installed and accessible from the command line

---

## Setup Instructions

1. Clone the repository:

```bash
git clone <repo-url>
cd <repo-directory>
```

2. Install dependencies via `uv`:

```bash
uv install
```

3. Setup environment variables:

```bash
cp .env.examples .env
# Then edit .env to provide API keys or configuration values if needed
```

---

## Running the Multi-Agent Swarm

The system can execute audits against any repository URL and optional PDF report.

### 1. Run Detectives Only (evidence collection)

```bash
uv run python -m src.nodes.run_detectives --repo "<target-repo-path-or-url>" --pdf "<report-path>"
```

**Output:** Evidence buckets for RepoInvestigator, DocAnalyst, and VisionInspector.

---

### 2. Run Full Audit (Detectives → Judges → ChiefJustice)

```bash
uv run python -m src.graph "<target-repo-path-or-url>" "<report-path>"
```

**Behavior:**

- Detectives execute concurrently, collecting structured evidence
- Judges reason over evidence (execution may be serialized locally due to API limits)
- Chief Justice deterministically synthesizes a report

**Output:**

- JSON reports in `reports/`
- Markdown report preview, including scores, verdicts, and remediation

---

## Handling API Limits

- Judges can execute in parallel in production
- Local testing may serialize judicial calls due to external API quotas (`RESOURCE_EXHAUSTED`)
- Detectives are deterministic and do not depend on LLM calls

---

## Environment Variables

Your `.env` file can include:

```text
GEMINI_API_KEY=<your-api-key>
UV_LOG_LEVEL=INFO
REPO_SANDBOX_PATH=/tmp/repo_sandbox
PDF_DEFAULT_PATH=reports/Final_Report.pdf
```

Adjust according to your environment and API quotas.

---

## Notes

- The system is **offline-safe**: detects missing PDFs or repo issues gracefully
- Evidence collection is reproducible and type-validated via **Pydantic schemas**
- Swarm execution is CI-friendly, cost-aware, and horizontally scalable

---
