# src/graph.p

import sys
import asyncio
import json
from pathlib import Path
from typing import List

from langgraph.graph import StateGraph, START, END

from src.state import AgentState, RubricDimension
from src.nodes.detectives import run_detectives
from src.nodes.judges import run_judges
from src.nodes.justice import ChiefJusticeNode

# -----------------------------
# Load rubric.json
# -----------------------------
RUBRIC_FILE = Path("rubric/week2_rubric.json")
with RUBRIC_FILE.open("r", encoding="utf-8") as f:
    rubric_data = json.load(f)

rubric_dims: List[RubricDimension] = [
    RubricDimension(id=d["id"], name=d["name"], target_artifact=d["target_artifact"])
    for d in rubric_data.get("dimensions", [])
]

# -----------------------------
# Define Graph Nodes
# -----------------------------

async def detectives_node(state: AgentState) -> dict:
    """Run detectives that have input to work with."""
    if state.repo_url or state.pdf_path:
        await run_detectives(state)  # Detectives internally check which inputs exist
    return {"evidences": state.evidences}


async def aggregate_evidence_node(state: AgentState) -> dict:
    """Fan-in node: merge all detective evidence into a flat list."""
    flat = [ev for bucket in state.evidences.values() for ev in bucket]
    return {"flat_evidences": flat}

async def judges_node(state: AgentState) -> dict:
    """Run all judge nodes in parallel on aggregated evidence."""
    await run_judges(state)
    return {"opinions": state.opinions}

async def chief_justice_node(state: AgentState) -> dict:
    """Run ChiefJustice to synthesize final report."""
    chief = ChiefJusticeNode(state)
    await chief.run()
    return {
        "final_report": state.final_report,
        "final_report_md": state.final_report_md
    }

# -----------------------------
# Build the StateGraph
# -----------------------------
# We pass the class itself here
graph = StateGraph(AgentState)

# Nodes
graph.add_node("Detectives", detectives_node)
graph.add_node("EvidenceAggregator", aggregate_evidence_node)
graph.add_node("Judges", judges_node)
graph.add_node("ChiefJustice", chief_justice_node)

# Flow logic
graph.add_edge(START, "Detectives") # Set the entry point
graph.add_edge("Detectives", "EvidenceAggregator")
graph.add_edge("EvidenceAggregator", "Judges")
graph.add_edge("Judges", "ChiefJustice")
graph.add_edge("ChiefJustice", END) # Set the exit point

# Compile the graph
app = graph.compile()

# -----------------------------
# Graph Execution
# -----------------------------
async def run_graph(repo_url: str | None = None, pdf_path: str | None = None) -> AgentState:
    initial_state = AgentState(
        repo_url=repo_url,
        pdf_path=pdf_path,
        rubric_dimensions=rubric_dims,
    )
    result = await app.ainvoke(initial_state)
    return result if isinstance(result, AgentState) else AgentState(**result)

def run_sync(repo_url: str | None = None, pdf_path: str | None = None) -> AgentState:
    return asyncio.run(run_graph(repo_url, pdf_path))

# -----------------------------
# CLI Entry
# -----------------------------
if __name__ == "__main__":
    import sys

    repo: str | None = None
    pdf: str | None = None

    # Parse arguments
    # Usage examples:
    # python src/graph.py repo_url pdf_path
    # python src/graph.py repo_url
    # python src/graph.py "" pdf_path
    if len(sys.argv) == 3:
        repo, pdf = sys.argv[1], sys.argv[2]
        if repo == "":  # allow empty string if only pdf is used
            repo = None
    elif len(sys.argv) == 2:
        arg = sys.argv[1]
        # Simple heuristic: if it ends with .pdf → treat as PDF
        if arg.lower().endswith(".pdf"):
            pdf = arg
        else:
            repo = arg
    else:
        print("Usage: python src/graph.py <repo_url_or_empty> <pdf_path_optional>")
        print("Example 1: python src/graph.py https://github.com/user/repo report.pdf")
        print("Example 2: python src/graph.py https://github.com/user/repo")
        print("Example 3: python src/graph.py \"\" report.pdf")
        sys.exit(2)

    print(f"--- Starting Audit ---")
    if repo:
        print(f"Repo URL: {repo}")
    if pdf:
        print(f"PDF Path: {pdf}")

    final_result_state = run_sync(repo, pdf)

    print("\n" + "="*30)
    print("AUDIT COMPLETE")
    print("="*30)

    print(f"Evidence buckets collected: {list(final_result_state.evidences.keys())}")
    print(f"Total Judge Opinions:       {len(final_result_state.opinions)}")

    if final_result_state.final_report_md:
        print("\n--- Markdown Report Preview (First 600 chars) ---")
        print(final_result_state.final_report_md[:600])
    else:
        print("\nNo Markdown report was generated.")
