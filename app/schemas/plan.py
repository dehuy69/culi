"""Plan schemas."""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class PlanStep(BaseModel):
    """Plan step schema."""
    id: int
    action: str
    target: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)
    description: Optional[str] = None


class PlanView(BaseModel):
    """Plan view schema."""
    description: str
    steps: List[PlanStep]
    estimated_time: Optional[str] = None
    risks: Optional[List[str]] = None


class PlanDecisionRequest(BaseModel):
    """Plan decision request."""
    decision: str = Field(..., pattern="^(approve|edit|cancel)$")
    plan: Optional[PlanView] = None  # Required if decision is "edit"


class PlanExecutionStep(BaseModel):
    """Plan execution step result."""
    step_id: int
    status: str  # "success", "failed", "pending"
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

