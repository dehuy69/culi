"""LangGraph state definition."""
from typing import TypedDict, List, Optional, Dict, Any
from app.domain.apps.base import ConnectedAppConfig, Plan


class ConnectedApp(TypedDict, total=False):
    """Connected app information in state."""
    id: str
    name: str                  # "KiotViet", "Misa eShop", ...
    category: str              # "POS_SIMPLE" | "ACCOUNTING" | "UNKNOWN"
    connection_method: str     # "api" | "mcp"
    config: Dict[str, Any]     # api_base_url, credentials hoặc mcp_url, tool_ids,...


class CuliState(TypedDict, total=False):
    """State that flows through the LangGraph workflow."""
    
    # Technical context
    user_id: str
    workspace_id: str
    conversation_id: str
    
    # Input from FE
    user_input: str
    messages: List[Dict[str, Any]]  # OpenAI format chat history
    
    # App hiện đang dùng trong workspace
    connected_app: Optional[ConnectedApp]  # Connected app configuration
    
    # Phân loại intent
    intent: str           # "general_qa", "tax_qa", "app_read", "app_plan", "no_app"
    needs_web: bool       # Cần web search
    needs_app: bool       # Cần đụng tới app bên ngoài (KiotViet, Misa,...)
    needs_plan: bool      # Cần lập plan
    
    # Ngữ cảnh
    chat_context: str     # Summarized history
    kb_context: str       # RAG results (optional)
    
    # Kết quả từ web
    web_results: List[Dict[str, Any]]
    
    # Kết quả từ app bên ngoài (POS / accounting)
    app_data: Dict[str, Any]   # invoices, balances, items,...
    
    # Plan (chiến lược thao tác trên app)
    plan: Optional[Dict[str, Any]]  # Plan dict with steps
    plan_approved: bool
    current_step_index: int
    step_results: List[Dict[str, Any]]
    
    # Output cuối
    answer: str
    error: Optional[str]
    stream_events: List[Dict[str, Any]]  # For streaming

