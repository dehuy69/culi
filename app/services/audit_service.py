"""Audit service for log retrieval."""
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.agent_run import AgentRun
from app.models.agent_step import AgentStep
from app.core.logging import get_logger

logger = get_logger(__name__)


class AuditService:
    """Service for audit and logging operations."""
    
    @staticmethod
    def get_agent_runs(
        db: Session,
        conversation_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AgentRun]:
        """Get agent runs with optional filtering."""
        query = db.query(AgentRun)
        
        if conversation_id:
            query = query.filter(AgentRun.conversation_id == conversation_id)
        
        return query.order_by(AgentRun.created_at.desc()).limit(limit).offset(offset).all()
    
    @staticmethod
    def get_agent_steps(
        db: Session,
        run_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AgentStep]:
        """Get agent steps with optional filtering."""
        query = db.query(AgentStep)
        
        if run_id:
            query = query.filter(AgentStep.run_id == run_id)
        
        return query.order_by(AgentStep.step_index.asc()).limit(limit).offset(offset).all()

