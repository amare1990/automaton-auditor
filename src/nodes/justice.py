from typing import List, Optional, Dict
from src.state import AgentState, Evidence, JudicialOpinion, AuditReport, CriterionResult

class ChiefJusticeNode:
    """
    Synthesizes the final AuditReport.
    Enhanced with:
    - Weighted scoring (Tech Lead has more weight on implementation).
    - Evidence-based anchoring (Grounds the report in the Detective findings).
    - Advanced Dissent detection.
    """

    def __init__(self, agent_state: AgentState):
        self.state = agent_state

    def _compute_weighted_score(self, opinions: List[JudicialOpinion]) -> int:
        """
        Applies weights to different judicial personas.
        """
        if not opinions:
            return 1

        total_weight = 0.0
        weighted_sum = 0.0

        weights = {
            "TechLead": 1.5,   # Tech Lead has a 50% higher say in technical reality
            "Prosecutor": 1.0,
            "Defense": 1.0
        }

        for op in opinions:
            # Match the judge field from JudicialOpinion (Literal)
            weight = weights.get(op.judge, 1.0)
            weighted_sum += (op.score * weight)
            total_weight += weight

        return max(1, min(5, round(weighted_sum / total_weight)))

    def _generate_dissent_analysis(self, opinions: List[JudicialOpinion]) -> Optional[str]:
        """Analyzes divergence between Judge personas."""
        if len(opinions) < 2:
            return None

        scores = [op.score for op in opinions]
        spread = max(scores) - min(scores)

        if spread >= 2:
            # Logic for explaining why they disagree
            prosecutor_op = next((o for o in opinions if o.judge == "Prosecutor"), None)
            defense_op = next((o for o in opinions if o.judge == "Defense"), None)

            summary = f"High variance (spread: {spread}). "
            if prosecutor_op and defense_op and prosecutor_op.score < defense_op.score:
                summary += "Prosecutor flagged critical gaps that the Defense view as acceptable trade-offs."
            return summary
        return None

    def synthesize_report(self) -> AuditReport:
        """Combines evidence and opinions into the final structured AuditReport."""
        # Flatten evidence for the summary
        all_evidences = [ev for bucket in self.state.evidences.values() for ev in bucket]
        opinions = self.state.opinions

        criteria_results: List[CriterionResult] = []
        rubric_dimensions = getattr(self.state, "rubric_dimensions", [])

        for dim in rubric_dimensions:
            # Filter opinions relevant to this specific rubric dimension
            relevant_opinions = [op for op in opinions if op.criterion_id == dim.id]

            # Use the new weighted scoring
            final_score = self._compute_weighted_score(relevant_opinions)
            dissent = self._generate_dissent_analysis(relevant_opinions)

            # Map evidence to remediation
            relevant_evidence = [e for e in all_evidences if e.found is False]
            remediation = "No critical issues found."
            if relevant_evidence:
                remediation = f"Address failures in: " + ", ".join(list(set(e.location for e in relevant_evidence[:3])))

            criteria_results.append(
                CriterionResult(
                    dimension_id=dim.id,
                    dimension_name=dim.name,
                    final_score=final_score,
                    judge_opinions=relevant_opinions,
                    dissent_summary=dissent,
                    remediation=remediation,
                )
            )

        # Calculate overall project score
        overall_avg = sum(c.final_score for c in criteria_results) / len(criteria_results) if criteria_results else 1.0

        report = AuditReport(
            repo_url=self.state.repo_url or "Local Scan",
            executive_summary=f"Audit synthesized from {len(all_evidences)} evidence nodes. "
                              f"Final verdict derived from {len(opinions)} judicial deliberations.",
            overall_score=round(overall_avg, 2),
            criteria=criteria_results,
            remediation_plan="Prioritize remediation based on the Tech Lead's cited technical debt."
        )

        self.state.final_report = report
        return report

    def generate_markdown(self, report: AuditReport) -> str:
        """Generates a professional Markdown audit for the final submission."""
        md = f"# ⚖️ Digital Courtroom: Final Audit Report\n\n"
        md += f"**Target:** `{report.repo_url}`\n"
        md += f"**Overall Audit Score:** `{report.overall_score} / 5.0`\n\n"
        md += f"## 📝 Executive Summary\n{report.executive_summary}\n\n"
        md += "--- \n"

        for c in report.criteria:
            md += f"### {c.dimension_name} | Score: {c.final_score}/5\n"
            if c.dissent_summary:
                md += f"> ⚠️ **Dissent Detected:** {c.dissent_summary}\n\n"

            md += f"**Remediation Guidance:** {c.remediation}\n\n"

            md += "| Judge | Score | Argument |\n"
            md += "| :--- | :--- | :--- |\n"
            for op in c.judge_opinions:
                md += f"| {op.judge} | {op.score} | {op.argument} |\n"
            md += "\n"

        md += "---\n"
        md += "## 🛠️ Remediation Plan\n"
        md += report.remediation_plan + "\n"

        return md

    async def run(self) -> AuditReport:
        report = self.synthesize_report()
        self.state.final_report_md = self.generate_markdown(report)
        return report
