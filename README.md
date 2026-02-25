Automaton Auditor — Interim Detective Runner

Quickstart

1. Create and activate a Python virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install the package (uses `pyproject.toml`) — using `uv` package manager:

```bash
uv install
```

If you prefer `pip` as a fallback you can still run:

```bash
python -m pip install -e .
```

3. Copy `.env.example` to `.env` and add your `OPENAI_API_KEY` (or other provider keys):

```bash
cp .env.example .env
# edit .env
```

Run the detective graph (interim):

```bash
python src/graph.py <github_repo_url> <path/to/interim_report.pdf>
```

What this does (interim):

- Clones the target repo into a temporary sandbox
- Extracts git history and performs lightweight AST scans for StateGraph wiring
- Parses the provided PDF report and extracts key terms and referenced file paths
- Aggregates evidence into a typed `AgentState` (see `src/state.py`)

Next steps to complete the Week 2 interim submission:

- Implement Judge personas (`src/nodes/judges.py`) that return `JudicialOpinion` objects
- Implement the Chief Justice synthesis node and Markdown report generation
- (Optional) integrate `vision_tools` image analysis for diagrams

Files of interest:

- `src/state.py` — typed Pydantic models and `AgentState` TypedDict
- `src/tools/repo_tools.py` — sandboxed clone + git/AST helpers
- `src/tools/doc_tools.py` — PDF ingestion + simple path extraction
- `src/nodes/detectives.py` — RepoInvestigator, DocAnalyst, VisionInspector
- `src/graph.py` — runner for detective fan-out/fan-in

If you want, I can implement the judges and ChiefJustice synthesis next.
