from __future__ import annotations
import asyncio
import json
from typing import List

from src.config import get_llm
from src.state import Evidence, JudicialOpinion, AgentState

class JudgeBase:
    persona_prompt: str = ""

    def __init__(self, state: AgentState):
        self.state = state
        # Initialize the LLM via our factory
        self.llm = get_llm(temperature=0.7)

    async def _call_llm(self, evidence_text: str) -> JudicialOpinion:
        """Call LLM and parse output into JudicialOpinion safely."""
        prompt = f"""
{self.persona_prompt}
Return ONLY valid JSON matching JudicialOpinion schema.
Evidence:
{evidence_text}
"""
        # 1. Invoke LLM
        response = await self.llm.ainvoke(prompt)
        content = response.content

        # 2. Handle the "str | list" type return from LangChain
        if isinstance(content, list):
            content_str = "".join([c if isinstance(c, str) else str(c) for c in content])
        else:
            content_str = str(content)

        # 3. Strip Markdown code blocks if present (e.g., ```json ... ```)
        clean_json = content_str.strip()
        if clean_json.startswith("```"):
            # Remove opening ```json or ``` and closing ```
            lines = clean_json.splitlines()
            if len(lines) > 2:
                clean_json = "\n".join(lines[1:-1])

        # 4. Parse into Pydantic model
        try:
            return JudicialOpinion.model_validate_json(clean_json)
        except Exception:
            # Fallback for manual parsing if validation fails
            data = json.loads(clean_json)
            return JudicialOpinion(**data)

    async def review_evidence(self, evidences: List[Evidence]) -> JudicialOpinion:
        raise NotImplementedError

# Concrete Judge implementations (Prosecutor, Defense, TechLead)
class Prosecutor(JudgeBase):
    persona_prompt = "You are the PROSECUTOR. Be adversarial and skeptical."
    async def review_evidence(self, evidences: List[Evidence]) -> JudicialOpinion:
        text = "\n".join(e.model_dump_json() for e in evidences)
        opinion = await self._call_llm(text)
        self.state.opinions.append(opinion)
        return opinion

class Defense(JudgeBase):
    persona_prompt = "You are the DEFENSE. Give benefit of doubt."
    async def review_evidence(self, evidences: List[Evidence]) -> JudicialOpinion:
        text = "\n".join(e.model_dump_json() for e in evidences)
        opinion = await self._call_llm(text)
        self.state.opinions.append(opinion)
        return opinion

class TechLead(JudgeBase):
    persona_prompt = "You are the TECH LEAD. Focus on engineering practicality."
    async def review_evidence(self, evidences: List[Evidence]) -> JudicialOpinion:
        text = "\n".join(e.model_dump_json() for e in evidences)
        opinion = await self._call_llm(text)
        self.state.opinions.append(opinion)
        return opinion

async def run_judges(state: AgentState) -> List[JudicialOpinion]:
    judges = [Prosecutor(state), Defense(state), TechLead(state)]
    all_evidence: List[Evidence] = [e for bucket in state.evidences.values() for e in bucket]
    return await asyncio.gather(*(j.review_evidence(all_evidence) for j in judges))
