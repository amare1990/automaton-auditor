from __future__ import annotations

import operator
from typing import Annotated, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict

# -----------------------------
# Evidence Models (Detective Layer)
# -----------------------------

class Evidence(BaseModel):
    """Detective-level evidence record.

    Fields
    - `goal`: short canonical name for what the detective was trying to find
    - `found`: whether the detective found usable evidence for the `goal`
    - `content`: an optional short textual excerpt or serialized value (truncated)
    - `location`: file path, URL, or commit hash where the evidence was observed
    - `rationale`: human-readable explanation for why the item was recorded
    - `confidence`: estimated confidence in the finding (0.0 - 1.0)
    """
    goal: str = Field(description="Canonical goal name for the detective check")
    found: bool = Field(description="True when the detective located supporting evidence")
    content: Optional[str] = Field(default=None, description="Short excerpt or serialized evidence")
    location: str = Field(description="File path, URL, or commit hash where evidence was observed")
    rationale: str = Field(description="Why this evidence was recorded and how it was derived")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0")


# -----------------------------
# Judicial Opinion Models (Judge Layer)
# -----------------------------

class JudicialOpinion(BaseModel):
    """A judge's opinion on a single rubric criterion.

    - `judge`: role of the opinion author
    - `criterion_id`: stable identifier for the rubric criterion
    - `score`: integer score (1-5)
    - `argument`: rationale supplied by the judge
    - `cited_evidence`: list of Evidence.goal keys or ids referenced
    """
    judge: Literal["Prosecutor", "Defense", "TechLead"] = Field(description="Role issuing the opinion")
    criterion_id: str = Field(description="Stable rubric criterion identifier")
    score: int = Field(ge=1, le=5, description="Integer score between 1 and 5")
    argument: str = Field(description="Reasoning behind the score")
    cited_evidence: List[str] = Field(description="List of evidence keys cited by the judge")


# -----------------------------
# Chief Justice Output Models
# -----------------------------

class CriterionResult(BaseModel):
    """Aggregated result for a rubric dimension/criterion."""
    dimension_id: str = Field(description="Stable dimension identifier")
    dimension_name: str = Field(description="Human friendly name for the dimension")
    final_score: int = Field(ge=1, le=5, description="Final aggregated score")
    judge_opinions: List[JudicialOpinion] = Field(description="List of judge opinions used to derive final_score")
    dissent_summary: Optional[str] = Field(
        default=None,
        description="Summary of dissenting opinion when judge variance is large",
    )
    remediation: str = Field(description="Concrete, actionable remediation guidance (file-level preferred)")


class AuditReport(BaseModel):
    repo_url: str
    executive_summary: str
    overall_score: float
    criteria: List[CriterionResult]
    remediation_plan: str


# -----------------------------
# Graph / Agent State (Typed)
# -----------------------------

class AgentState(TypedDict):
    """In-memory orchestrator state shared across detective / judge nodes.

    Keys
    - `repo_url`: repository location to analyze
    - `pdf_path`: path to the written audit / report PDF
    - `rubric_dimensions`: list of rubric dimension descriptors
    - `evidences`: mapping of detective name -> list of Evidence records. Reducer is set to allow safe merges in parallel flows.
    - `opinions`: list of `JudicialOpinion` values aggregated from judge nodes
    - `final_report`: optional `AuditReport` produced by the Chief Justice
    """
    repo_url: str
    pdf_path: str
    rubric_dimensions: List[Dict]
    evidences: Annotated[Dict[str, List[Evidence]], operator.ior]
    opinions: Annotated[List[JudicialOpinion], operator.add]
    final_report: Optional[AuditReport]

