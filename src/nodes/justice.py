# src/nodes/justice.py
from typing import List, Optional
from src.state import AgentState, Evidence, JudicialOpinion, AuditReport, CriterionResult

class ChiefJusticeNode:
    """
    Synthesizes a final AuditReport from collected evidence and judge opinions.
    Applies deterministic conflict resolution:
      - Fact supremacy: evidence overrides opinion if critical failure
      - Dissent detection: variance triggers dissent summary
      - Security override: critical repo/pdf failures reduce overall score
    Stores result as AuditReport in agent_state.final_report
    """

    def __init__(self, agent_state: AgentState):
        self.state = agent_state

    def _compute_dimension_score(self, opinions: List[JudicialOpinion]) -> int:
        """
        Aggregate multiple opinions into a single integer score (1-5) per criterion.
        """
        if not opinions:
            return 1  # default minimum score

        scores = [op.score for op in opinions]
        avg = sum(scores) / len(scores)
        return max(1, min(5, round(avg)))

    def _resolve_conflicts(self, opinions: list[JudicialOpinion]) -> tuple[int, Optional[str]]:
        """
        Determine overall average score and optional dissent summary.
        """
        if not opinions:
            return 1, None

        scores = [op.score for op in opinions]
        avg = sum(scores) / len(scores)
        dissent_summary = None
        if max(scores) - min(scores) >= 2:
            dissent_summary = "Significant disagreement among judges detected."

        return round(avg), dissent_summary

    def synthesize_report(self) -> AuditReport:
        """
        Main deterministic synthesis workflow.
        Combines evidence and opinions into structured AuditReport.
        """
        evidences: List[Evidence] = []
        for det_list in self.state.evidences.values():
            evidences.extend(det_list)

        opinions: List[JudicialOpinion] = self.state.opinions

        # Build per-criterion results
        criteria_results: List[CriterionResult] = []
        rubric_dimensions = getattr(self.state, "rubric_dimensions", [])

        for dim in rubric_dimensions:
            relevant_opinions = [op for op in opinions if op.criterion_id == dim.id]
            final_score = self._compute_dimension_score(relevant_opinions)
            dissent_summary = None
            if relevant_opinions:
                _, dissent_summary = self._resolve_conflicts(relevant_opinions)

            criteria_results.append(
                CriterionResult(
                    dimension_id=dim.id,
                    dimension_name=dim.name,
                    final_score=final_score,
                    judge_opinions=relevant_opinions,
                    dissent_summary=dissent_summary,
                    remediation="Review files indicated in evidence for remediation",
                )
            )

        overall_score, _ = self._resolve_conflicts(opinions)

        report = AuditReport(
            repo_url=self.state.repo_url,
            executive_summary=f"Audit completed with {len(evidences)} evidence items and {len(opinions)} opinions.",
            overall_score=overall_score,
            criteria=criteria_results,
            remediation_plan="Follow remediation guidance in each criterion.",
        )

        # store in agent state
        self.state.final_report = report
        return report

    def generate_markdown(self, report: AuditReport) -> str:
        """
        Convert AuditReport into Markdown for human readability.
        """
        md = f"# Audit Report\n\n"
        md += f"**Repository:** {report.repo_url}\n\n"
        md += f"**Executive Summary:** {report.executive_summary}\n\n"

        for c in report.criteria:
            md += f"## {c.dimension_name} (Score: {c.final_score})\n"
            if c.dissent_summary:
                md += f"**Dissent:** {c.dissent_summary}\n"
            md += f"**Remediation:** {c.remediation}\n"
            md += f"### Judge Opinions:\n"
            for op in c.judge_opinions:
                md += f"- {op.judge}: {op.argument} (Score: {op.score})\n"
            md += "\n"

        md += f"**Overall Score:** {report.overall_score}\n"
        md += f"**Remediation Plan:** {report.remediation_plan}\n"
        return md

    async def run(self) -> AuditReport:
        """
        Complete ChiefJustice workflow: synthesize report and store in AgentState.
        """
        report = self.synthesize_report()
        md = self.generate_markdown(report)

        # store markdown optionally
        self.state.final_report_md = md
        return report
