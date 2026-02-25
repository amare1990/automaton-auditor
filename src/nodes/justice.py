# src/nodes/justice.py
from typing import Dict, Any
import asyncio

from src.state import AgentState, Evidence, Opinion

class ChiefJustice:
    """
    Synthesizes a final verdict / audit report from collected evidence and opinions.
    Produces structured JSON for downstream reporting and Markdown summary.
    """
    def __init__(self, agent_state: AgentState):
        self.agent_state = agent_state

    async def synthesize_report(self) -> Dict[str, Any]:
        """
        Main synthesis workflow: combine evidence and opinions into final report.
        """
        # Ensure we have evidence and opinions
        if not self.agent_state.evidences:
            raise ValueError("No evidence collected to synthesize.")
        if not self.agent_state.opinions:
            raise ValueError("No opinions collected to synthesize.")

        # Example scoring / synthesis logic
        total_score = sum(opinion.score for opinion in self.agent_state.opinions)
        avg_score = total_score / len(self.agent_state.opinions)

        report_json = {
            "summary": f"Audit completed with {len(self.agent_state.evidences)} pieces of evidence "
                       f"and {len(self.agent_state.opinions)} opinions.",
            "evidences": [e.dict() for e in self.agent_state.evidences],
            "opinions": [o.dict() for o in self.agent_state.opinions],
            "average_opinion_score": avg_score
        }

        return report_json

    async def generate_markdown(self, report_json: Dict[str, Any]) -> str:
        """
        Converts the report JSON into a Markdown-friendly audit summary.
        """
        md = f"# Audit Report\n\n"
        md += f"**Summary:** {report_json['summary']}\n\n"
        md += f"## Evidence Collected ({len(report_json['evidences'])})\n"
        for e in report_json['evidences']:
            md += f"- [{e['type']}] {e['description']} (ID: {e['id']})\n"

        md += f"\n## Opinions ({len(report_json['opinions'])})\n"
        for o in report_json['opinions']:
            md += f"- [{o['author']}] Score: {o['score']} | Comment: {o['comment']}\n"

        md += f"\n**Average Opinion Score:** {report_json['average_opinion_score']:.2f}\n"

        return md

    async def run(self) -> Dict[str, Any]:
        """
        Complete ChiefJustice workflow: synthesize report and prepare Markdown.
        """
        report_json = await self.synthesize_report()
        report_md = await self.generate_markdown(report_json)

        # Optionally store in agent state for downstream nodes
        self.agent_state.final_report_json = report_json
        self.agent_state.final_report_md = report_md

        return report_json
