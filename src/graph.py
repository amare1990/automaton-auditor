import asyncio
from typing import Dict, Any
from pathlib import Path

from src.state import AgentState
from src.nodes.detectives import run_detectives


async def run_detective_graph(repo_url: str, pdf_path: str) -> AgentState:
    """Run the detective fan-out (RepoInvestigator, DocAnalyst, VisionInspector)
    and then aggregate evidence into the AgentState. Returns final state.
    """
    initial_state: AgentState = {
        "repo_url": repo_url,
        "pdf_path": pdf_path,
        "rubric_dimensions": [],
        "evidences": {},
        "opinions": [],
        "final_report": None,
    }

    # run detectives in parallel
    gathered = await run_detectives(initial_state)

    # evidence already merged by detectives into initial_state['evidences']
    # mark fan-in complete
    initial_state.setdefault("evidences", {})
    initial_state["fan_in_ready"] = True  # type: ignore

    return initial_state


def run_sync(repo_url: str, pdf_path: str) -> Dict[str, Any]:
    """Synchronous helper to run the async graph from non-async callers."""
    return asyncio.run(run_detective_graph(repo_url, pdf_path))


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python src/graph.py <repo_url> <pdf_path>")
        raise SystemExit(2)

    repo = sys.argv[1]
    pdf = sys.argv[2]
    final = run_sync(repo, pdf)
    print("Detective graph completed. Evidence keys:", list(final.get("evidences", {}).keys()))

