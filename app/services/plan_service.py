"""Plan service for handling plan approval and execution."""
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models.user import User
from app.graph.app_graph import get_graph
from app.graph.state import CuliState
from app.core.logging import get_logger

logger = get_logger(__name__)


class PlanService:
    """Service for plan-related operations."""
    
    @staticmethod
    def approve_plan(state: Dict[str, Any]) -> Dict[str, Any]:
        """Approve plan for execution."""
        state["plan_approved"] = True
        logger.info("Plan approved for execution")
        return state
    
    @staticmethod
    def cancel_plan(state: Dict[str, Any]) -> Dict[str, Any]:
        """Cancel plan execution."""
        state["plan"] = {}
        state["plan_approved"] = False
        state["answer"] = "Kế hoạch đã được hủy."
        logger.info("Plan cancelled")
        return state
    
    @staticmethod
    def edit_plan(state: Dict[str, Any], edited_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Edit plan before execution."""
        state["plan"] = edited_plan
        state["plan_approved"] = False  # Require re-approval
        logger.info("Plan edited")
        return state

