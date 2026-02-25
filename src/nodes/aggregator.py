# src/nodes/aggregator.py
from typing import List
import asyncio

from src.state import Evidence, Opinion, AgentState

class EvidenceAggregator:
    """
    Aggregates evidence from Detective agents and opinions from Judges.
    Ensures fan-in barrier is complete before proceeding to ChiefJustice.
    """
    def __init__(self, agent_state: AgentState):
        self.agent_state = agent_state

    async def collect_evidence(self, detective_tasks: List[asyncio.Task]) -> List[Evidence]:
        """
        Wait for all Detective agents to finish and gather their evidence.
        """
        completed = await asyncio.gather(*detective_tasks)
        # Flatten results and append to agent state
        for evidence_list in completed:
            self.agent_state.evidences.extend(evidence_list)
        return self.agent_state.evidences

    async def collect_opinions(self, judge_tasks: List[asyncio.Task]) -> List[Opinion]:
        """
        Wait for all Judges to finish reviewing evidence.
        """
        completed = await asyncio.gather(*judge_tasks)
        # Flatten results and append to agent state
        for opinion_list in completed:
            # In case each judge returns a list of opinions (or single opinion)
            if isinstance(opinion_list, list):
                self.agent_state.opinions.extend(opinion_list)
            else:
                self.agent_state.opinions.append(opinion_list)
        return self.agent_state.opinions

    async def aggregate(self, detective_tasks: List[asyncio.Task], judge_tasks: List[asyncio.Task]):
        """
        Full aggregation workflow: wait for detectives, then judges, then consolidate.
        """
        await self.collect_evidence(detective_tasks)
        await self.collect_opinions(judge_tasks)
        # Optional: here you could normalize scores, remove duplicates, etc.
        return {
            "evidences": self.agent_state.evidences,
            "opinions": self.agent_state.opinions
        }
