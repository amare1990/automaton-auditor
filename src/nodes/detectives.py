# src/nodes/detectives.py

from typing import List
import asyncio
from pathlib import Path
from src.state import Evidence, AgentState
from src.tools import repo_tools, doc_tools

# from PIL import Image

class DetectiveBase:
    def __init__(self, state: AgentState):
        self.state = state

    async def collect_evidence(self) -> List[Evidence]:
        raise NotImplementedError

class RepoInvestigator(DetectiveBase):
    async def collect_evidence(self) -> List[Evidence]:
        evidence_list: List[Evidence] = []
        repo_url = self.state.repo_url
        if not repo_url:
            evidence_list.append(Evidence(
                goal="git_forensic_analysis",
                found=False,
                content=None,
                location="",
                rationale="No repo_url provided to detective",
                confidence=0.0
            ))
            if self.state.evidences is None:
                self.state.evidences = {}

            self.state.evidences["repo_investigator"] = evidence_list
            return evidence_list

        # Clone repo sandbox
        try:
            repo_path = repo_tools.clone_repo_sandbox(repo_url)
        except Exception as exc:
            evidence_list.append(Evidence(
                goal="git_forensic_analysis",
                found=False,
                content=None,
                location=str(repo_url),
                rationale=f"Clone failed: {exc}",
                confidence=0.0
            ))
            return evidence_list

        try:
            commits = repo_tools.extract_git_history(repo_path)
        except Exception as exc:
            commits = []
            evidence_list.append(Evidence(
                goal="git_forensic_analysis",
                found=False,
                content=None,
                location=str(repo_path),
                rationale=f"Failed to extract git history: {exc}",
                confidence=0.0
            ))

        try:
            graph_info = repo_tools.analyze_graph_structure(repo_path)
        except Exception:
            graph_info = {"add_edge_calls": [], "stategraph_inits": []}

        evidence_list.append(Evidence(
            goal="git_forensic_analysis",
            found=len(commits) > 0,
            content=str(commits[:10]),
            location=str(repo_path),
            rationale="Extracted git log; >3 commits indicate activity",
            confidence=0.9
        ))

        evidence_list.append(Evidence(
            goal="graph_orchestration",
            found=bool(graph_info.get("add_edge_calls") or graph_info.get("stategraph_inits")),
            content=str(graph_info),
            location=str(repo_path),
            rationale="AST scan for StateGraph and add_edge calls",
            confidence=0.8
        ))

        if self.state.evidences is None:
            self.state.evidences = {}
        self.state.evidences["repo_investigator"] = evidence_list
        return evidence_list

class DocAnalyst(DetectiveBase):
    async def collect_evidence(self) -> List[Evidence]:
        evidence_list: List[Evidence] = []
        pdf_path = self.state.pdf_path

        if not pdf_path:
            evidence_list.append(Evidence(
                goal="doc_parsing",
                found=False,
                content=None,
                location="",
                rationale="No pdf_path provided to detective",
                confidence=0.0
            ))
            if self.state.evidences is None:
                self.state.evidences = {}
            self.state.evidences["repo_investigator"] = evidence_list
            return evidence_list

        path = Path(pdf_path)
        if not path.exists():
            evidence_list.append(Evidence(
                goal="doc_parsing",
                found=False,
                content=None,
                location=str(pdf_path),
                rationale="PDF not found",
                confidence=0.0
            ))
            if self.state.evidences is None:
                self.state.evidences = {}
            self.state.evidences["repo_investigator"] = evidence_list
            return evidence_list

        chunks = doc_tools.ingest_pdf(path)
        hits = []
        keywords = ["Dialectical Synthesis", "Fan-In", "Fan-Out", "Metacognition"]
        for c in chunks:
            for kw in keywords:
                if kw.lower() in c.lower():
                    hits.append((kw, c[:400]))

        evidence_list.append(Evidence(
            goal="theoretical_depth",
            found=bool(hits),
            content=str(hits[:3]),
            location=str(pdf_path),
            rationale="Searched report chunks for key architecture terms",
            confidence=0.8 if hits else 0.2
        ))

        text = "\n".join(chunks)
        paths = doc_tools.extract_file_paths_from_text(text)
        evidence_list.append(Evidence(
            goal="report_file_paths",
            found=bool(paths),
            content=str(paths[:20]),
            location=str(pdf_path),
            rationale="Extracted likely file paths mentioned in report",
            confidence=0.8
        ))

        if self.state.evidences is None:
            self.state.evidences = {}
        self.state.evidences["repo_investigator"] = evidence_list
        return evidence_list


class VisionInspector(DetectiveBase):
    """
    Optional vision-based detective for multimodal repo/report artifacts.

    Currently supports:
    - Basic image existence checks
    - Placeholder for object detection / diagram analysis

    Execution is safe for interim; missing images do not fail workflow.
    """

    async def collect_evidence(self) -> List[Evidence]:
        evidence_list: List[Evidence] = []

        # Look for images under a standard folder (e.g., docs/images)
        from pathlib import Path

        repo_url = self.state.repo_url or ""
        image_dir = Path(repo_url) / "docs" / "images"
        found_images: List[str] = []

        if image_dir.exists() and image_dir.is_dir():
            for img_path in image_dir.rglob("*"):
                if img_path.suffix.lower() in [".png", ".jpg", ".jpeg", ".svg"]:
                    found_images.append(str(img_path))

        if not found_images:
            evidence_list.append(Evidence(
                goal="vision_inspection",
                found=False,
                content=None,
                location=str(image_dir),
                rationale="No images found in standard location; vision inspection skipped",
                confidence=0.0
            ))
        else:
            # Optional: placeholder for real analysis (OCR, diagram detection)
            analysis_summary = [f"{p} (placeholder analysis)" for p in found_images[:10]]

            evidence_list.append(Evidence(
                goal="vision_inspection",
                found=True,
                content=str(analysis_summary),
                location=str(image_dir),
                rationale=f"Found {len(found_images)} image(s) and performed placeholder analysis",
                confidence=0.7
            ))

        if self.state.evidences is None:
            self.state.evidences = {}
        self.state.evidences["repo_investigator"] = evidence_list
        return evidence_list

async def run_detectives(state: AgentState) -> List[Evidence]:
    """Run all detectives concurrently and merge evidence into AgentState."""
    detectives = [
        RepoInvestigator(state),
        DocAnalyst(state),
        VisionInspector(state)  # now fully integrated
    ]

    # run all detectives in parallel
    results = await asyncio.gather(*(d.collect_evidence() for d in detectives))

    # flatten list of lists
    all_evidence = [item for sublist in results for item in sublist]

    # merge into shared state under 'evidences'
    if state.evidences is None:
        state.evidences = {}

    for d, sublist in zip(
        ["repo_investigator", "doc_analyst", "vision_inspector"], results
    ):
        state.evidences[d] = sublist

    return all_evidence
