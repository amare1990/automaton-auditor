# src/nodes/judges.py
from typing import List
import asyncio

from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser

from src.state import Evidence, JudicialOpinion, AgentState

# -----------------------------
# Base Judge Interface
# -----------------------------
class JudgeBase:
    """
    Base class for all Judicial agents.
    Each judge forms a JudicialOpinion based on collected Evidence.
    """
    def __init__(self, state: AgentState, llm_model=None):
        self.state = state
        self.llm_model = llm_model or ChatOpenAI(temperature=0)  # deterministic

    async def review_evidence(self, evidences: List[Evidence]) -> JudicialOpinion:
        """
        Analyze evidence and produce a JudicialOpinion.
        Must be implemented by subclasses.
        """
        raise NotImplementedError


# -----------------------------
# Concrete Judge Agents (LLM-ready)
# -----------------------------
class Prosecutor(JudgeBase):
    """Focuses on potential issues, violations, or non-compliance."""
    async def review_evidence(self, evidences: List[Evidence]) -> JudicialOpinion:
        parser = PydanticOutputParser(pydantic_object=JudicialOpinion)
        prompt_text = f"""
        You are a Prosecutor judge. Review the following evidence and score each rubric criterion (1-5):
        Evidence: {evidences}
        Provide argument, score, criterion_id, and cited_evidence as structured output.
        """
        chain = LLMChain(llm=self.llm_model, prompt=prompt_text, output_parser=parser)
        opinion = await chain.arun()
        self.state.setdefault("opinions", []).append(opinion)
        return opinion


class Defense(JudgeBase):
    """Focuses on justification, correctness, or compliance mitigation."""
    async def review_evidence(self, evidences: List[Evidence]) -> JudicialOpinion:
        parser = PydanticOutputParser(pydantic_object=JudicialOpinion)
        prompt_text = f"""
        You are a Defense judge. Review the following evidence and defend correct practices.
        Provide argument, score, criterion_id, and cited_evidence as structured output.
        Evidence: {evidences}
        """
        chain = LLMChain(llm=self.llm_model, prompt=prompt_text, output_parser=parser)
        opinion = await chain.arun()
        self.state.setdefault("opinions", []).append(opinion)
        return opinion


class TechLead(JudgeBase):
    """Focuses on technical quality, best practices, and maintainability."""
    async def review_evidence(self, evidences: List[Evidence]) -> JudicialOpinion:
        parser = PydanticOutputParser(pydantic_object=JudicialOpinion)
        prompt_text = f"""
        You are a TechLead judge. Analyze the evidence for technical quality,
        maintainability, and adherence to best practices.
        Provide argument, score, criterion_id, and cited_evidence as structured output.
        Evidence: {evidences}
        """
        chain = LLMChain(llm=self.llm_model, prompt=prompt_text, output_parser=parser)
        opinion = await chain.arun()
        self.state.setdefault("opinions", []).append(opinion)
        return opinion


# -----------------------------
# Utility to Run All Judges
# -----------------------------
async def run_judges(state: AgentState, llm_model=None) -> List[JudicialOpinion]:
    """
    Fan-out all judges concurrently and collect their opinions.
    """
    judges = [
        Prosecutor(state, llm_model),
        Defense(state, llm_model),
        TechLead(state, llm_model),
    ]
    all_evidence: List[Evidence] = []
    for sublist in state.get("evidences", {}).values():
        all_evidence.extend(sublist)

    results = await asyncio.gather(*(j.review_evidence(all_evidence) for j in judges))
    return results
