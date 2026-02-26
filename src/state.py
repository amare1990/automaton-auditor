# src/state.py
from __future__ import annotations
import operator
from typing import Annotated, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from uuid import uuid4

# -----------------------------
# Evidence Models (Detective Layer)
# -----------------------------

class Evidence(BaseModel):
    """Detective-level evidence record.

    Fields:
    - id: unique identifier for traceability
    - goal: canonical short name for what the detective was trying to find
    - found: whether usable evidence was located
    - content: optional textual excerpt or serialized value
    - location: file path, URL, or commit hash
    - rationale: explanation for why it was recorded
    - confidence: float 0.0–1.0
    """
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique evidence identifier")
    goal: str = Field(description="Canonical goal name for the detective check")
    found: bool = Field(description="True when the detective located supporting evidence")
    content: Optional[str] = Field(default=None, description="Short excerpt or serialized evidence")
    location: str = Field(description="File path, URL, or commit hash where evidence was observed")
    rationale: str = Field(description="Why this evidence was recorded and how it was derived")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0"
    )

# -----------------------------
# Judicial Opinion Models (Judge Layer)
# -----------------------------

class JudicialOpinion(BaseModel):
    judge: Literal["Prosecutor", "Defense", "TechLead"] = Field(description="Role issuing the opinion")
    criterion_id: str = Field(description="Stable rubric criterion identifier")
    score: int = Field(ge=1, le=5, description="Integer score between 1 and 5")
    argument: str = Field(description="Reasoning behind the score")
    cited_evidence: List[str] = Field(description="List of Evidence.id values cited by the judge")

# -----------------------------
# Chief Justice Output Models
# -----------------------------

class CriterionResult(BaseModel):
    dimension_id: str = Field(description="Stable dimension identifier")
    dimension_name: str = Field(description="Human friendly name for the dimension")
    final_score: int = Field(ge=1, le=5, description="Final aggregated score")
    judge_opinions: List[JudicialOpinion] = Field(description="List of judge opinions used to derive final_score")
    dissent_summary: Optional[str] = Field(default=None, description="Summary of dissenting opinion")
    remediation: str = Field(description="Concrete, actionable remediation guidance (file-level preferred)")

class AuditReport(BaseModel):
    repo_url: str
    executive_summary: str
    overall_score: float = Field(ge=1.0, le=5.0)
    criteria: List[CriterionResult]
    remediation_plan: str

class RubricDimension(BaseModel):
    id: str
    name: str
    target_artifact: str

# -----------------------------
# Graph / Agent State (Typed)
# -----------------------------

class AgentState(TypedDict):
    repo_url: str
    pdf_path: str
    rubric_dimensions: List[RubricDimension]
    evidences: Annotated[Dict[str, List[Evidence]], operator.ior]
    opinions: Annotated[List[JudicialOpinion], operator.add]
    final_report: Optional[AuditReport]

class Config:
    frozen = True
