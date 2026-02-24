# src/nodes/detectives.py
from typing import List
import asyncio

from src.state import Evidence, AgentState

# Base Detective Interface
class DetectiveBase:
    """
    Base class for all Detective agents.
    Each detective collects evidence asynchronously.
    """
    def __init__(self, agent_state: AgentState):
        self.agent_state = agent_state

    async def collect_evidence(self) -> List[Evidence]:
        """
        Collect evidence relevant to the audit.
        Must be implemented by subclasses.
        """
        raise NotImplementedError


# -----------------------------
# Concrete Detective Agents
# -----------------------------

class RepoInvestigator(DetectiveBase):
    """
    Investigates code repository:
    - Git history
    - AST patterns
    - Sandbox code execution (if needed)
    """
    async def collect_evidence(self) -> List[Evidence]:
        evidence_list = []

        # TODO: Implement repo inspection using src/tools/git_tools.py and src/tools/ast_tools.py
        # Example placeholder:
        evidence_list.append(
            Evidence(
                type="repo_snapshot",
                content="RepoInvestigator: scanned repository structure",
                source="RepoInvestigator",
            )
        )

        # Optionally update agent state
        self.agent_state.evidences.extend(evidence_list)
        return evidence_list


class DocAnalyst(DetectiveBase):
    """
    Parses and analyzes PDF or textual documentation:
    - Chunking PDFs
    - Searching for compliance info
    """
    async def collect_evidence(self) -> List[Evidence]:
        evidence_list = []

        # TODO: Implement PDF/document parsing using src/tools/pdf_tools.py
        evidence_list.append(
            Evidence(
                type="doc_analysis",
                content="DocAnalyst: parsed and chunked documentation",
                source="DocAnalyst",
            )
        )

        self.agent_state.evidences.extend(evidence_list)
        return evidence_list


class VisionInspector(DetectiveBase):
    """
    Optional multimodal agent for images or screenshots in the repo:
    - Scans images for charts, screenshots, or diagrams
    """
    async def collect_evidence(self) -> List[Evidence]:
        evidence_list = []

        # TODO: Implement vision inspection using src/tools/vision_tools.py
        evidence_list.append(
            Evidence(
                type="vision_inspection",
                content="VisionInspector: processed visual assets",
                source="VisionInspector",
            )
        )

        self.agent_state.evidences.extend(evidence_list)
        return evidence_list


# -----------------------------
# Utility to Run All Detectives
# -----------------------------
async def run_detectives(agent_state: AgentState) -> List[Evidence]:
    """
    Fan-out all detective agents concurrently and collect their evidence.
    """
    detectives = [
        RepoInvestigator(agent_state),
        DocAnalyst(agent_state),
        VisionInspector(agent_state),
    ]
    # Gather results concurrently
    results = await asyncio.gather(*(d.collect_evidence() for d in detectives))
    # Flatten list of lists
    all_evidence = [item for sublist in results for item in sublist]
    return all_evidence
