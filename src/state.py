from __future__ import annotations

import operator
from datetime import datetime
from typing import Annotated, Dict, List, Literal, Optional

from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# =====================================================
# Detective Layer — Evidence
# =====================================================

class Evidence(BaseModel):
    """Atomic forensic fact produced by a detective.

    Designed to be:
    - append-only
    - citeable by judges
    - deterministic across runs
    """

    id: str = Field(description="Stable unique evidence id (uuid/hash)")
    goal: str = Field(description="Canonical goal name for the detective check")

    found: bool = Field(description="Whether evidence supporting the goal was found")

    content: Optional[str] = Field(
        default=None,
        description="Short excerpt / snippet / serialized value (truncated)",
    )

    location: str = Field(
        description="File path, URL, or commit hash where evidence was observed"
    )

    rationale: str = Field(
        description="Explanation of how this evidence was derived"
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0",
    )

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp evidence was produced",
    )


# =====================================================
# Judicial Layer — Opinions
# =====================================================

class JudicialOpinion(BaseModel):
    """A single judge's reasoning for one rubric criterion."""

    id: str = Field(description="Unique opinion id")

    judge: Literal["Prosecutor", "Defense", "TechLead"] = Field(
        description="Role issuing the opinion"
    )

    criterion_id: str = Field(description="Stable rubric criterion identifier")

    score: int = Field(
        ge=1,
        le=5,
        description="Integer score between 1 and 5",
    )

    argument: str = Field(description="Reasoning behind the score")

    cited_evidence: List[str] = Field(
        description="List of Evidence.id values referenced"
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Judge confidence in this assessment",
    )


# =====================================================
# Chief Justice — Aggregation
# =====================================================

class CriterionResult(BaseModel):
    """Final synthesized result for one rubric dimension."""

    dimension_id: str
    dimension_name: str

    final_score: int = Field(ge=1, le=5)

    judge_opinions: List[JudicialOpinion]

    dissent_summary: Optional[str] = None

    remediation: str = Field(
        description="Concrete actionable remediation guidance"
    )


class AuditReport(BaseModel):
    """Top-level deliverable artifact."""

    repo_url: str
    executive_summary: str

    overall_score: float = Field(ge=1.0, le=5.0)

    criteria: List[CriterionResult]

    remediation_plan: str


class RubricDimension(BaseModel):
    """Machine-readable rubric dimension descriptor."""

    id: str
    name: str
    target_artifact: str


# =====================================================
# LangGraph Shared State
# =====================================================
# Reducers:
#   - evidences → dict union (parallel detectives)
#   - opinions  → list append (parallel judges)
#

class AgentState(TypedDict, total=False):
    """
    Mutable state passed between LangGraph nodes.

    total=False allows partial state during early graph stages.
    """

    # inputs
    repo_url: str
    pdf_path: str
    rubric_dimensions: List[RubricDimension]

    # detective outputs (parallel safe)
    evidences: Annotated[
        Dict[str, List[Evidence]],
        operator.ior,  # merge dicts
    ]

    # judge outputs (parallel safe)
    opinions: Annotated[
        List[JudicialOpinion],
        operator.add,  # append lists
    ]

    # final synthesis
    final_report: AuditReport


# =====================================================
# Helpers (recommended for deterministic initialization)
# =====================================================

def initial_state(repo_url: str, pdf_path: str) -> AgentState:
    """Safe initializer to avoid missing keys during first reducer merge."""
    return {
        "repo_url": repo_url,
        "pdf_path": pdf_path,
        "evidences": {},
        "opinions": [],
    }
