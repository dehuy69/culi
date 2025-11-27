"""Agent step model for logging individual execution steps."""
from sqlalchemy import Column, Integer, ForeignKey, String, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.db.base import BaseModel


class StepStatus(str, enum.Enum):
    """Step execution status."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"


class AgentStep(BaseModel):
    """Agent step log for tracking individual plan execution steps."""
    
    __tablename__ = "agent_steps"
    
    run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=False, index=True)
    step_index = Column(Integer, nullable=False)  # Step order in plan
    action = Column(String(200), nullable=False)  # Action name (e.g., "create_product")
    input_data = Column(JSON, nullable=True)      # Step input parameters
    output_data = Column(JSON, nullable=True)     # Step output result
    status = Column(SQLEnum(StepStatus), nullable=False, default=StepStatus.PENDING)
    error_message = Column(String(1000), nullable=True)  # Error message if failed
    
    # Relationships
    run = relationship("AgentRun", backref="steps")
    
    def __repr__(self):
        return f"<AgentStep(id={self.id}, run_id={self.run_id}, step_index={self.step_index}, status={self.status})>"

