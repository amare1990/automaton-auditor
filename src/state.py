from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime

# -----------------------------
# Evidence Models (Detective Layer)
# -----------------------------

class EvidenceType(str, Enum):
    CODE = "code"
    DOC = "doc"
    DIAGRAM = "diagram"
    METADATA = "metadata"

class Evidence(BaseModel):
    id: str
    type: EvidenceType
    source: str                 # file path, PDF page, or repo URL
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, str]] = {}

# -----------------------------
# Judicial Opinion Models (Judge Layer)
# -----------------------------

class Criterion(str, Enum):
    ARCHITECTURE = "architecture"
    SAFE_TOOLING = "safe_tooling"
    STRUCTURED_OUTPUT = "structured_output"
    DIALECTICAL_SYNTHESIS = "dialectical_synthesis"
    STATE_SYNCHRONIZATION = "state_synchronization"

class JudicialOpinion(BaseModel):
    judge: str                   # Prosecutor, Defense, TechLead
    criterion: Criterion
    score: int                   # 0-10
    argument: str
    cited_evidence: List[str]    # List of Evidence IDs
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# -----------------------------
# Aggregator / Chief Justice Models
# -----------------------------

class CriterionResult(BaseModel):
    criterion: Criterion
    avg_score: float
    opinions: List[JudicialOpinion]
    notes: Optional[str] = None

class AuditReport(BaseModel):
    repo_url: str
    overall_score: float
    criteria: List[CriterionResult]
    executive_summary: Optional[str] = None
    remediation_plan: Optional[str] = None
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# -----------------------------
# Agent / Runtime State
# -----------------------------

class AgentState(BaseModel):
    detective_evidence: Dict[str, Evidence] = {}
    judicial_opinions: Dict[str, JudicialOpinion] = {}
    audit_report: Optional[AuditReport] = None
    current_node: Optional[str] = None
    branch_context: Optional[str] = None
    fan_out_nodes: List[str] = []
    fan_in_ready: bool = False
