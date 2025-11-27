"""Base classes, enums, and DTOs for app adapters."""
from enum import Enum
from typing import Protocol, Dict, Any, List, Literal, Optional
from pydantic import BaseModel


class AppCategory(str, Enum):
    """App category classification."""
    POS_SIMPLE = "POS_SIMPLE"      # KiotViet, Misa eShop, Sapo
    ACCOUNTING = "ACCOUNTING"      # MISA, Fast, Bravo
    UNKNOWN = "UNKNOWN"            # Apps chưa phân loại


class ConnectionMethod(str, Enum):
    """Connection method to external app."""
    API = "api"                    # Direct API calls
    MCP = "mcp"                    # Model Context Protocol server


class ConnectedAppConfig(BaseModel):
    """Configuration for a connected app."""
    app_id: str                    # "kiotviet", "misa_eshop", ...
    name: str                      # Display name: "KiotViet", "Misa eShop"
    category: AppCategory          # App category
    connection_method: ConnectionMethod  # How to connect
    credentials: Dict[str, Any]    # OAuth credentials, API keys, etc.
    extra: Dict[str, Any] = {}     # Additional configuration
    
    class Config:
        use_enum_values = True


class AppReadIntent(BaseModel):
    """Intent for reading data from app."""
    kind: str                      # "LIST_INVOICES", "SUMMARY_REVENUE", "LIST_PRODUCTS", ...
    params: Dict[str, Any] = {}    # Parameters for the read operation
    
    class Config:
        use_enum_values = True


class PlanStep(BaseModel):
    """A single step in an execution plan."""
    id: int
    action: str                    # "CREATE_PRODUCT", "CREATE_INVOICE", "CREATE_CATEGORY", ...
    params: Dict[str, Any]         # Parameters for the action


class Plan(BaseModel):
    """Execution plan with multiple steps."""
    description: str               # Human-readable description
    steps: List[PlanStep]          # List of steps to execute


class StepResult(BaseModel):
    """Result of executing a plan step."""
    step_id: int
    status: Literal["success", "failed"]
    message: str                   # Success or error message
    raw: Dict[str, Any] = {}       # Raw response from app API


class BaseAppAdapter(Protocol):
    """
    Protocol for app adapters.
    All app-specific adapters must implement this interface.
    """
    
    def read(self, intent: AppReadIntent, config: ConnectedAppConfig) -> Dict[str, Any]:
        """
        Read data from the app based on intent.
        
        Args:
            intent: What to read (invoices, products, revenue, etc.)
            config: App configuration with credentials
            
        Returns:
            Dictionary with read data
        """
        ...
    
    def execute_step(
        self,
        step: PlanStep,
        config: ConnectedAppConfig
    ) -> StepResult:
        """
        Execute a single plan step.
        
        Args:
            step: The step to execute
            config: App configuration with credentials
            
        Returns:
            Result of the execution
        """
        ...
    
    def supports_action(self, action: str) -> bool:
        """
        Check if adapter supports a specific action.
        
        Args:
            action: Action name (e.g., "CREATE_PRODUCT")
            
        Returns:
            True if supported, False otherwise
        """
        ...

