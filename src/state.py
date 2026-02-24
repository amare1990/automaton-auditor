from pydantic import BaseModel
from typing import Dict, List, Literal, Optional

class Evidence(BaseModel):
    found: bool
    content: Optional[str]
    location: str
    confidence: float

class JudicialOpinion(BaseModel):
    judge: Literal["Prosecutor", "Defense", "TechLead"]
    score: int
    argument: str
    cited_evidence: List[str]

class AgentState(BaseModel):
    repo_url: str
    pdf_path: str | None = None
    evidences: Dict[str, Evidence] = {}
    opinions: List[JudicialOpinion] = []
    report_path: str | None = None
