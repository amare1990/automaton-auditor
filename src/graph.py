# src/graph.py
import asyncio
import json
from pathlib import Path
from typing import List

from src.state import AgentState, RubricDimension
from src.nodes.detectives import run_detectives
from src.nodes.judges import run_judges
from src.nodes.justice import ChiefJusticeNode


# =====================================================
# Rubric Loader (NEW — constitutional layer)
# =====================================================

def load_rubric(path: Path) -> List[RubricDimension]:
    """Load rubric.json and convert to typed RubricDimension list."""
    data = json.loads(path.read_text())

    dims = []
    for d in data.get("dimensions", []):
        dims.append(
            RubricDimension(
                id=d["id"],
                name=d["name"],
                target_artifact=d["target_artifact"],
            )
        )
    return dims


# =====================================================
# Full Hierarchical StateGraph
# =====================================================

async def run_full_stategraph(
    repo_url: str,
    pdf_path: str,
    rubric_path: str = "rubric/week2_rubric.json",
) -> AgentState:
    """
    END-TO-END PIPELINE

    START
      → Load Rubric
      → Detectives (parallel fan-out)
      → Judges (parallel fan-out per dimension)
      → ChiefJustice synthesis
      → Markdown report
    """

    # -----------------------------
    # Layer 0 — Constitution
    # -----------------------------
    rubric_dims = load_rubric(Path(rubric_path))

    state = AgentState(
        repo_url=repo_url,
        pdf_path=pdf_path,
        rubric_dimensions=rubric_dims,
    )

    # -----------------------------
    # Layer 1 — Detectives
    # -----------------------------
    await run_detectives(state)

    # -----------------------------
    # Layer 2 — Judges
    # Judges evaluate EACH dimension
    # -----------------------------
    await run_judges(state)

    # -----------------------------
    # Layer 3 — Chief Justice (fan-in)
    # -----------------------------
    chief = ChiefJusticeNode(state)
    report = await chief.run()

    return state


# =====================================================
# Sync wrapper
# =====================================================

def run_sync(repo_url: str, pdf_path: str):
    return asyncio.run(run_full_stategraph(repo_url, pdf_path))


# =====================================================
# CLI
# =====================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python src/graph.py <repo_url> <pdf_path>")
        raise SystemExit(2)

    state = run_sync(sys.argv[1], sys.argv[2])

    print("\nAudit complete.")
    print("Evidence buckets:", list(state.evidences.keys()))
    print("Opinions:", len(state.opinions))

    if state.final_report_md:
        print("\nMarkdown Preview:\n")
        print(state.final_report_md[:600])
