"""Workspace schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WorkspaceCreate(BaseModel):
    """Workspace creation request."""
    name: str = Field(..., min_length=1, max_length=200)


class WorkspaceUpdate(BaseModel):
    """Workspace update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)


class WorkspaceOut(BaseModel):
    """Workspace response."""
    id: int
    name: str
    owner_id: int
    created_at: datetime

    class Config:
        from_attributes = True

