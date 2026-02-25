# src/main.py
import argparse
import asyncio
from pathlib import Path

# Importing nodes
from nodes.detectives import RepoInvestigator, DocAnalyst, VisionInspector
from nodes.judges import Prosecutor, Defense, TechLead
from nodes.aggregator import EvidenceAggregator
from nodes.justice import ChiefJustice
from nodes.report import ReportWriter

# Default output directory
OUTPUT_DIR = Path(__file__).parent.parent / "audit" / "report_onself_generated"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


async def run_audit(repo_path: str):
    """Orchestrate the full auditing flow for a repository."""
    print(f"Starting audit for repo: {repo_path}")

    # ----------------------------
    # 1️⃣ Detectives collect evidence
    # ----------------------------
    print("Running detectives...")
    repo_investigator = RepoInvestigator(repo_path)
    doc_analyst = DocAnalyst(repo_path)
    vision_inspector = VisionInspector(repo_path)

    # Gather evidence concurrently
    evidence_list = await asyncio.gather(
        repo_investigator.collect_evidence(),
        doc_analyst.collect_evidence(),
        vision_inspector.collect_evidence()
    )
    print(f"Collected evidence from detectives: {len(evidence_list)} sources")

    # ----------------------------
    # 2️⃣ Judges provide opinions
    # ----------------------------
    print("Running judges...")
    prosecutor = Prosecutor(evidence_list)
    defense = Defense(evidence_list)
    tech_lead = TechLead(evidence_list)

    opinions = await asyncio.gather(
        prosecutor.evaluate(),
        defense.evaluate(),
        tech_lead.evaluate()
    )
    print(f"Judges generated {len(opinions)} opinions")

    # ----------------------------
    # 3️⃣ Aggregate evidence/opinions
    # ----------------------------
    print("Aggregating evidence and opinions...")
    aggregator = EvidenceAggregator(evidence_list, opinions)
    aggregated_data = aggregator.aggregate()
    print("Aggregation complete.")

    # ----------------------------
    # 4️⃣ Chief Justice synthesizes verdict
    # ----------------------------
    print("Running ChiefJustice synthesis...")
    chief_justice = ChiefJustice(aggregated_data)
    verdict = chief_justice.synthesize()
    print("Verdict synthesized.")

    # ----------------------------
    # 5️⃣ Report generation
    # ----------------------------
    print("Generating Markdown report...")
    report_writer = ReportWriter(aggregated_data, verdict, OUTPUT_DIR)
    report_file = report_writer.write_markdown()
    print(f"Report saved to: {report_file}")


def main():
    parser = argparse.ArgumentParser(description="Automaton Auditor CLI")
    parser.add_argument(
        "repo_path",
        type=str,
        help="Path to the repository to audit (local path or URL)"
    )
    args = parser.parse_args()

    asyncio.run(run_audit(args.repo_path))


if __name__ == "__main__":
    main()
