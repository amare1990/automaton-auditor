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
    repo_url: Optional[str] = None
    executive_summary: str
    overall_score: float = Field(ge=1.0, le=5.0)
    criteria: List[CriterionResult]
    remediation_plan: str

class RubricDimension(BaseModel):
    id: str
    name: str
    target_artifact: str


# =====================================================
# Agent State (LangGraph State)
# =====================================================

class AgentState(BaseModel):
    repo_url: str | None = None
    pdf_path: str | None = None

    rubric_dimensions: List[RubricDimension] = Field(default_factory=list)
    evidences: Dict[str, List[Evidence]] = Field(default_factory=dict)
    opinions: List[JudicialOpinion] = Field(default_factory=list)
    final_report: Optional[AuditReport] = None
    final_report_md: Optional[str] = None
    flat_evidences: List[Evidence] = Field(default_factory=list)

class Config:
    frozen = True
