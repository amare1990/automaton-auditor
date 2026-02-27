# src/nodes/judges.py
from __future__ import annotations
import os
import json
import asyncio
from typing import List

from langchain_openai import ChatOpenAI

from src.config import settings
from src.state import Evidence, JudicialOpinion, AgentState


# =========================================================
# Base Judge
# =========================================================
class JudgeBase:
    """
    Base judicial agent.

    Each judge:
    - receives full Evidence set
    - calls LLM
    - validates JSON into JudicialOpinion
    - appends to AgentState
    """

    persona_prompt: str = ""

    def __init__(self, state: AgentState):
        self.state = state

        OPENAI_KEY = os.getenv("OPENAI_KEY")
        if OPENAI_KEY is None:
            raise ValueError("OPENAI_KEY not set in .env")

        self.llm = ChatOpenAI(
            model=settings.MODEL,
            temperature=settings.TEMP,
            api_key=lambda: OPENAI_KEY,
        )

    async def _call_llm(self, evidence_text: str) -> JudicialOpinion:
        """Call LLM and parse output into JudicialOpinion."""
        prompt = f"""
{self.persona_prompt}

Return ONLY valid JSON matching JudicialOpinion schema.

Evidence:
{evidence_text}
"""
        for _ in range(2):  # simple retry
            try:
                raw = await self.llm.ainvoke(prompt)
                if isinstance(raw, str):
                    # parse JSON into Pydantic model
                    return JudicialOpinion.parse_raw(raw)
                elif isinstance(raw, dict):
                    return JudicialOpinion(**raw)
            except Exception:
                continue

        raise RuntimeError("Judge failed to produce structured output")


    async def review_evidence(self, evidences: List[Evidence]) -> JudicialOpinion:
        raise NotImplementedError


# =========================================================
# Concrete Judges
# =========================================================
class Prosecutor(JudgeBase):
    persona_prompt = """
You are the PROSECUTOR.
Be adversarial and skeptical.
Score LOW unless evidence is strong.
"""

    async def review_evidence(self, evidences: List[Evidence]) -> JudicialOpinion:
        text = "\n".join(e.model_dump_json() for e in evidences)
        opinion = await self._call_llm(text)
        self.state.opinions.append(opinion)
        return opinion


class Defense(JudgeBase):
    persona_prompt = """
You are the DEFENSE.
Reward effort, partial correctness, and creative solutions.
Give benefit of doubt unless evidence proves failure.
"""

    async def review_evidence(self, evidences: List[Evidence]) -> JudicialOpinion:
        text = "\n".join(e.model_dump_json() for e in evidences)
        opinion = await self._call_llm(text)
        self.state.opinions.append(opinion)
        return opinion


class TechLead(JudgeBase):
    persona_prompt = """
You are the TECH LEAD.
Focus on architecture quality, maintainability, modularity.
Evaluate engineering practicality only.
"""

    async def review_evidence(self, evidences: List[Evidence]) -> JudicialOpinion:
        text = "\n".join(e.model_dump_json() for e in evidences)
        opinion = await self._call_llm(text)
        self.state.opinions.append(opinion)
        return opinion


# =========================================================
# Parallel Fan-Out Runner
# =========================================================
async def run_judges(state: AgentState) -> List[JudicialOpinion]:
    judges = [Prosecutor(state), Defense(state), TechLead(state)]

    all_evidence: List[Evidence] = [
        e for bucket in state.evidences.values() for e in bucket
    ]

    return await asyncio.gather(
        *(j.review_evidence(all_evidence) for j in judges)
    )
