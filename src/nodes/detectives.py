# src/nodes/detectives.py
from typing import List
import asyncio
from pathlib import Path
from src.state import Evidence, AgentState
from src.tools import repo_tools, doc_tools

class DetectiveBase:
    def __init__(self, state: AgentState):
        self.state = state

    async def collect_evidence(self) -> List[Evidence]:
        raise NotImplementedError

class RepoInvestigator(DetectiveBase):
    async def collect_evidence(self) -> List[Evidence]:
        evidence_list: List[Evidence] = []
        repo_url = self.state.get("repo_url")
        if not repo_url:
            evidence_list.append(Evidence(
                goal="git_forensic_analysis",
                found=False,
                content=None,
                location="",
                rationale="No repo_url provided to detective",
                confidence=0.0
            ))
            self.state.setdefault("evidences", {})
            self.state["evidences"]["repo_investigator"] = evidence_list
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

        self.state.setdefault("evidences", {})
        self.state["evidences"]["repo_investigator"] = evidence_list
        return evidence_list

class DocAnalyst(DetectiveBase):
    async def collect_evidence(self) -> List[Evidence]:
        evidence_list: List[Evidence] = []
        pdf_path = self.state.get("pdf_path")
        if not pdf_path:
            evidence_list.append(Evidence(
                goal="doc_parsing",
                found=False,
                content=None,
                location="",
                rationale="No pdf_path provided to detective",
                confidence=0.0
            ))
            self.state.setdefault("evidences", {})
            self.state["evidences"]["doc_analyst"] = evidence_list
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
            self.state.setdefault("evidences", {})
            self.state["evidences"]["doc_analyst"] = evidence_list
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

        self.state.setdefault("evidences", {})
        self.state["evidences"]["doc_analyst"] = evidence_list
        return evidence_list

class VisionInspector(DetectiveBase):
    async def collect_evidence(self) -> List[Evidence]:
        evidence = Evidence(
            goal="vision_inspector",
            found=False,
            content=None,
            location="",
            rationale="Vision inspection not executed in interim",
            confidence=0.0
        )
        self.state.setdefault("evidences", {})
        self.state["evidences"]["vision_inspector"] = [evidence]
        return [evidence]

async def run_detectives(state: AgentState) -> List[Evidence]:
    detectives = [RepoInvestigator(state), DocAnalyst(state), VisionInspector(state)]
    results = await asyncio.gather(*(d.collect_evidence() for d in detectives))
    return [e for sub in results for e in sub]
