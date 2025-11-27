"""Common schemas."""
from typing import Optional
from pydantic import BaseModel


class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = 1
    page_size: int = 50


class PaginationResponse(BaseModel):
    """Pagination response metadata."""
    page: int
    page_size: int
    total: int
    pages: int


class ErrorResponse(BaseModel):
    """Error response schema."""
    error: str
    detail: Optional[str] = None

