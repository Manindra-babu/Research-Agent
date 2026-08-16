import json
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class AgentLog(BaseModel):
    timestamp: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))
    agent: str
    action: str
    status: str = "in-progress" # pending, in-progress, completed, failed
    details: Optional[str] = ""


class SourceItem(BaseModel):
    id: str
    title: str
    url: str
    snippet: str
    content: Optional[str] = ""
    credibility: str = "Medium" # High, Medium, Low
    relevance_score: float = 0.5
    subtopic: Optional[str] = ""


class FindingItem(BaseModel):
    subtopic: str
    key_takeaway: str
    details: str
    citations: List[str] = Field(default_factory=list) # List of source IDs or URLs


class FactCheckItem(BaseModel):
    claim: str
    verified: bool
    confidence_score: int # 0 to 100
    source_count: int
    flagged: bool = False
    supporting_sources: List[str] = Field(default_factory=list)
    notes: Optional[str] = ""


class ChartDataItem(BaseModel):
    title: str
    chart_type: str # bar, line, pie
    categories: List[str]
    values: List[float]
    unit: Optional[str] = ""


class TaskItem(BaseModel):
    id: str
    agent: str
    description: str
    status: str = "pending" # pending, in-progress, completed
    result: Optional[str] = ""


class ResearchState(BaseModel):
    """
    Unified state machine model passed through the LangGraph agent flow.
    """
    session_id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    research_goal: str = ""
    depth: str = "standard" # quick, standard, deep
    
    subtopics: List[str] = Field(default_factory=list)
    tasks: List[TaskItem] = Field(default_factory=list)
    
    sources: List[SourceItem] = Field(default_factory=list)
    findings: List[FindingItem] = Field(default_factory=list)
    fact_checks: List[FactCheckItem] = Field(default_factory=list)
    chart_data: List[ChartDataItem] = Field(default_factory=list)
    
    report_sections: Dict[str, str] = Field(default_factory=dict)
    final_report_md: str = ""
    pdf_path: str = ""
    quality_score: int = 0
    
    current_step: str = "initialized"
    agent_logs: List[AgentLog] = Field(default_factory=list)

    def log(self, agent: str, action: str, status: str = "in-progress", details: str = ""):
        """Appends a new activity log entry."""
        log_entry = AgentLog(
            agent=agent,
            action=action,
            status=status,
            details=details
        )
        self.agent_logs.append(log_entry)

    def save_to_disk(self, filepath: Optional[str] = None) -> str:
        """Persists state to JSON file."""
        os.makedirs("outputs/reports", exist_ok=True)
        if not filepath:
            filepath = os.path.join("outputs/reports", f"session_{self.session_id}.json")
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.model_dump_json(indent=2))
        return filepath

    @classmethod
    def load_from_disk(cls, filepath: str) -> "ResearchState":
        """Loads state from JSON file."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(**data)
