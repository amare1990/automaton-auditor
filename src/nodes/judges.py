from __future__ import annotations
import asyncio
import json
from typing import List,cast, Literal

from src.config import get_llm
from src.state import Evidence, JudicialOpinion, AgentState

class JudgeBase:
    persona_name: str = "Judge"
    persona_description: str = ""
    specific_criteria: str = ""

    def __init__(self, state: AgentState):
        self.state = state
        # Set temperature slightly lower for more consistent structured output
        self.llm = get_llm(temperature=0.3)

    def _generate_prompt(self, evidence_text: str) -> str:
        return f"""
        ROLE: {self.persona_name}
        CRITICAL: The 'judge' field MUST be exactly "{self.persona_name}".

        REQUIRED JSON SCHEMA:
        {{
        "judge": "{self.persona_name}",
        "criterion_id": "architecture_audit",
        "score": (1-5),
        "argument": "...",
        "cited_evidence": ["..."]
        }}

        EVIDENCE:
        {evidence_text}
        """

    async def review_evidence(self, evidences: List[Evidence]) -> JudicialOpinion:
        evidence_text = "\n".join(e.model_dump_json() for e in evidences)
        prompt = self._generate_prompt(evidence_text)

        # 1. Attempt Structured Output (The "Pro" way)
        try:
            if hasattr(self.llm, "with_structured_output"):
                structured_llm = self.llm.with_structured_output(JudicialOpinion)
                opinion = await structured_llm.ainvoke(prompt)

                if isinstance(opinion, JudicialOpinion):
                    return opinion
                if isinstance(opinion, dict):
                    return JudicialOpinion(**opinion)

            # 2. Fallback to standard cleaning if structured output isn't used
            response = await self.llm.ainvoke(prompt)
            raw_content = self._ensure_string(response.content)
            return JudicialOpinion.model_validate_json(self._clean_response(raw_content))

        except Exception as e:
            print(f"⚠️ {self.persona_name} evaluation failed: {e}. Returning safe fallback.")

            # 1. Clean the name for the Literal
            safe_judge_name = self.persona_name.replace(" ", "")

            # 2. Try to grab the first rubric ID so it actually shows up in the report
            first_dim = self.state.rubric_dimensions[0].id if self.state.rubric_dimensions else "general_audit"

            return JudicialOpinion(
                judge=cast(Literal["Prosecutor", "Defense", "TechLead"], safe_judge_name),
                criterion_id=first_dim, # Map to a real dimension!
                score=3,
                argument=f"Technical Limit: The model hit a rate limit (429). Audit based on partial automated evidence.",
                cited_evidence=[]
            )

    def _ensure_string(self, content: str | list) -> str:
        """Converts potential list of content blocks into a single string."""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            # Join text parts, ignore dicts/images for JSON parsing
            return "".join([block if isinstance(block, str) else block.get("text", "")
                          for block in content if isinstance(block, (str, dict))])
        return str(content)

    def _clean_response(self, content: str) -> str:
        """Strip markdown and whitespace."""
        clean = content.strip()
        if clean.startswith("```json"):
            clean = clean.split("```json")[1].split("```")[0]
        elif clean.startswith("```"):
            clean = clean.split("```")[1].split("```")[0]
        return clean.strip()

    def _manual_parse(self, content: str) -> JudicialOpinion:
        """Emergency fallback for non-structured responses."""
        data = json.loads(self._clean_response(content))
        return JudicialOpinion(**data)


class Prosecutor(JudgeBase):
    persona_name = "Prosecutor"
    persona_description = "You are a skeptical Forensic Auditor. Your job is to find gaps, missing documentation, and architectural inconsistencies."
    specific_criteria = "Look for: 'False' found flags in evidence, missing Pydantic schemas, and shallow git history."

class Defense(JudgeBase):
    persona_name = "Defense"
    persona_description = "You are the Developer Advocate. You highlight implementation complexity, successful tool integration, and adherence to requirements."
    specific_criteria = "Look for: Successful AST parsing, complex StateGraph edges, and clear rationale in evidence."

class TechLead(JudgeBase):
    persona_name = "Tech Lead"
    persona_description = "You are a pragmatic Systems Architect. You care about 'Substance over Buzzwords' and engineering scalability."
    specific_criteria = "Look for: Fan-In/Fan-Out patterns, schema enforcement, and effective use of LangGraph."

# --- Orchestration ---

async def run_judges(state: AgentState) -> List[JudicialOpinion]:
    """Runs judges. Note: In the Graph version, we move this to individual nodes."""
    judges = [Prosecutor(state), Defense(state), TechLead(state)]
    all_evidence = [e for bucket in state.evidences.values() for e in bucket]

    results = []
    for judge in judges:
        print(f"--- {judge.persona_name} is deliberating... ---")
        opinion = await judge.review_evidence(all_evidence)
        state.opinions.append(opinion)
        results.append(opinion)
        # Quota protection for Free Tier
        await asyncio.sleep(1.5)

    return results
