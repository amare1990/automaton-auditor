import sys
import asyncio
import json
from pathlib import Path
from typing import List, Literal

from langgraph.graph import StateGraph, START, END

from src.state import AgentState, RubricDimension
from src.nodes.detectives import run_detectives
from src.nodes.judges import Prosecutor, Defense, TechLead # Import individual classes
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
    if state.repo_url or state.pdf_path:
        await run_detectives(state)
    return {"evidences": state.evidences}

# --- 1. CONDITIONAL EDGE LOGIC ---
def route_after_detectives(state: AgentState) -> Literal["EvidenceAggregator", END]:
    """Gap Fix: Graph-level error edge. If no evidence found, stop early."""
    total_ev = sum(len(v) for v in state.evidences.values())
    if total_ev == 0:
        print("⚠️ No evidence collected. Ending audit early.")
        return END
    return "EvidenceAggregator"

async def aggregate_evidence_node(state: AgentState) -> dict:
    flat = [ev for bucket in state.evidences.values() for ev in bucket]
    return {"flat_evidences": flat}

# --- 2. PARALLEL JUDGE NODES (The Fan-Out) ---
async def prosecutor_node(state: AgentState) -> dict:
    judge = Prosecutor(state)
    opinion = await judge.review_evidence(state.flat_evidences)
    return {"opinions": [opinion]}

async def defense_node(state: AgentState) -> dict:
    judge = Defense(state)
    opinion = await judge.review_evidence(state.flat_evidences)
    return {"opinions": [opinion]}

async def tech_lead_node(state: AgentState) -> dict:
    judge = TechLead(state)
    opinion = await judge.review_evidence(state.flat_evidences)
    return {"opinions": [opinion]}

async def chief_justice_node(state: AgentState) -> dict:
    chief = ChiefJusticeNode(state)
    await chief.run()
    return {
        "final_report": state.final_report,
        "final_report_md": state.final_report_md
    }

# -----------------------------
# Build the StateGraph
# -----------------------------
builder = StateGraph(AgentState)

builder.add_node("Detectives", detectives_node)
builder.add_node("EvidenceAggregator", aggregate_evidence_node)
builder.add_node("Prosecutor", prosecutor_node)
builder.add_node("Defense", defense_node)
builder.add_node("TechLead", tech_lead_node)
builder.add_node("ChiefJustice", chief_justice_node)

# --- 3. UPDATED FLOW LOGIC ---
builder.add_edge(START, "Detectives")

# Gap Fix: Conditional Edge
builder.add_conditional_edges(
    "Detectives",
    route_after_detectives
)

# Fan-Out
builder.add_edge("EvidenceAggregator", "Prosecutor")
builder.add_edge("EvidenceAggregator", "Defense")
builder.add_edge("EvidenceAggregator", "TechLead")

# Fan-In (Parallel nodes converge at ChiefJustice)
builder.add_edge("Prosecutor", "ChiefJustice")
builder.add_edge("Defense", "ChiefJustice")
builder.add_edge("TechLead", "ChiefJustice")

builder.add_edge("ChiefJustice", END)

app = builder.compile()

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
