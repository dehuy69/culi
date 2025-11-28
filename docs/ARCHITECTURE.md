# Culi Backend Architecture

Tài liệu này mô tả kiến trúc và thiết kế của Culi Backend.

## 📋 Mục lục

1. [Tổng quan](#tổng-quan)
2. [Kiến trúc tổng thể](#kiến-trúc-tổng-thể)
3. [LangGraph Architecture](#langgraph-architecture)
4. [Adapter Pattern](#adapter-pattern)
5. [Database Models](#database-models)
6. [API Layer](#api-layer)
7. [Security](#security)

## Tổng quan

Culi Backend là một AI agent backend được xây dựng với:
- **FastAPI** cho REST API
- **LangGraph** cho AI agent orchestration
- **Adapter Pattern** để hỗ trợ nhiều loại ứng dụng bên ngoài
- **Domain-Driven Design** để tổ chức code

## Kiến trúc tổng thể

```
┌─────────────────────────────────────────────────────────┐
│                     Frontend Client                      │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────────┐
│                   FastAPI Application                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ API Routes   │→ │  Services    │→ │  LangGraph   │  │
│  └──────────────┘  └──────────────┘  └──────┬───────┘  │
└───────────────────────────────────────────────┼──────────┘
                                                │
┌───────────────────────────────────────────────▼──────────┐
│              Domain Layer (Adapters)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ KiotViet     │  │  Misa eShop  │  │  MCP Client  │  │
│  │  Adapter     │  │  Adapter     │  │  (Generic)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└──────────────────────────────────────────────────────────┘
                                                │
┌───────────────────────────────────────────────▼──────────┐
│              External Systems                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  KiotViet    │  │  Misa eShop  │  │  MCP Server  │  │
│  │     API      │  │     API      │  │   (Custom)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                    Infrastructure                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ PostgreSQL   │  │    Redis     │  │ OpenRouter   │  │
│  │  Database    │  │    (Future)  │  │    (LLM)     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### Layers

1. **API Layer** (`app/api/`): REST endpoints, request/response handling
2. **Service Layer** (`app/services/`): Business logic, orchestration
3. **Domain Layer** (`app/domain/apps/`): App adapters, domain logic
4. **Data Layer** (`app/models/`, `app/repositories/`): Database models, data access
5. **Graph Layer** (`app/graph/`): LangGraph workflow, nodes, state management

## LangGraph Architecture

LangGraph quản lý workflow xử lý câu hỏi của người dùng.

### Graph Flow

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ intent_router│ ◄─── Phân loại intent từ user input
└──────┬──────┘
       │
       ├─── general_qa ────┐
       ├─── tax_qa ────────┤
       ├─── app_read ──────┤
       ├─── app_plan ──────┤
       └─── no_app ────────┤
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
┌──────────┐        ┌──────────┐        ┌──────────┐
│ context  │        │web_search│        │  answer  │
└────┬─────┘        └────┬─────┘        └──────────┘
     │                   │                    ▲
     ├─── answer ────────┘                    │
     ├─── app_read                            │
     └─── app_plan                            │
           │                                  │
           ▼                                  │
     ┌──────────┐                            │
     │app_read  │                            │
     └────┬─────┘                            │
          │                                  │
          └──────────────────────────────────┘
                      │
                      ▼
                 ┌──────────┐
                 │app_plan  │
                 └────┬─────┘
                      │
                      ▼
              ┌──────────────┐
              │present_plan  │
              └──────┬───────┘
                     │
          ┌──────────┼──────────┐
          │          │          │
          ▼          ▼          ▼
     ┌────────┐  ┌────────┐  ┌──────┐
     │execute │  │cancel  │  │answer│
     └────┬───┘  └───┬────┘  └──────┘
          │          │
          ▼          ▼
     ┌────────┐  ┌──────┐
     │continue│  │answer│
     └───┬────┘  └──┬───┘
         │          │
         └──────┬───┘
                │
                ▼
           ┌─────────┐
           │  END    │
           └─────────┘
```

### Nodes

#### 1. `intent_router_node`

Phân loại intent từ user input:
- **general_qa**: Câu hỏi chung, không cần app
- **tax_qa**: Câu hỏi về thuế, cần web search
- **app_read**: Đọc dữ liệu từ app
- **app_plan**: Lập kế hoạch thao tác trên app
- **no_app**: Chưa cấu hình app

#### 2. `context_node`

Thu thập context:
- Conversation history (tối đa 3 messages gần nhất)
- Workspace information
- Connected app configuration

#### 3. `app_read_node`

Đọc dữ liệu từ connected app:
- Sử dụng adapter pattern
- Dispatch theo `AppReadIntent.kind`
- Ví dụ: LIST_PRODUCTS, LIST_INVOICES, SUMMARY_REVENUE

#### 4. `app_plan_node`

Tạo execution plan:
- Strategy khác nhau theo `app.category`:
  - `POS_SIMPLE`: Tạo sản phẩm, hóa đơn
  - `ACCOUNTING`: Mapping tài khoản, định khoản
  - `UNKNOWN`: Limited operations

#### 5. `execute_plan_node`

Thực thi plan từng bước:
- Sử dụng adapter pattern
- Execute từng `PlanStep` theo thứ tự
- Tích lũy `StepResult` để tạo answer

#### 6. `answer_node`

Tạo câu trả lời cuối cùng:
- Tổng hợp context, app_data, web_results, step_results
- Sử dụng LLM để generate natural language response
- Format markdown, tables, lists

#### 7. `web_search_node`

Tìm kiếm thông tin trên web:
- Sử dụng Google Custom Search API
- Cho câu hỏi về thuế, quy định

#### 8. `present_plan_node`

Hiển thị plan cho user approval:
- Chỉ dùng trong production với checkpoints
- Local development: auto-approve

### State

`CuliState` (TypedDict) chứa tất cả data flow qua graph:

```python
class CuliState(TypedDict, total=False):
    # Technical context
    user_id: str
    workspace_id: str
    conversation_id: str
    
    # Input
    user_input: str
    messages: List[Dict[str, Any]]  # Chat history
    
    # Connected app
    connected_app: Optional[ConnectedApp]
    
    # Intent classification
    intent: str  # "general_qa", "tax_qa", "app_read", "app_plan", "no_app"
    needs_web: bool
    needs_app: bool
    needs_plan: bool
    
    # Context
    chat_context: str
    kb_context: str
    
    # Results
    web_results: List[Dict[str, Any]]
    app_data: Dict[str, Any]
    
    # Plan
    plan: Optional[Dict[str, Any]]
    plan_approved: bool
    current_step_index: int
    step_results: List[Dict[str, Any]]
    
    # Output
    answer: str
    error: Optional[str]
    stream_events: List[Dict[str, Any]]
```

### Visualize Graph

Để generate biểu đồ LangGraph:

```bash
python scripts/generate_langgraph_chart.py --format mermaid --output docs/langgraph_chart.mmd
```

File Mermaid có thể được render tại [Mermaid Live Editor](https://mermaid.live/).

## Adapter Pattern

Adapter pattern cho phép hệ thống hỗ trợ nhiều loại ứng dụng bên ngoài một cách generic.

### Architecture

```
┌─────────────────────────────────────┐
│      LangGraph Nodes                │
│  (app_read_node, execute_plan_node) │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Adapter Registry               │
│  get_adapter(app_id)                │
└──────────────┬──────────────────────┘
               │
       ┌───────┼───────┐
       │       │       │
       ▼       ▼       ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│KiotViet  │ │ Misa     │ │ Unknown  │
│ Adapter  │ │ Adapter  │ │ Adapter  │
└────┬─────┘ └────┬─────┘ └────┬─────┘
     │            │            │
     ▼            ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│KiotViet  │ │  Misa    │ │   MCP    │
│   API    │ │   API    │ │  Server  │
└──────────┘ └──────────┘ └──────────┘
```

### BaseAppAdapter Interface

Tất cả adapters implement interface:

```python
class BaseAppAdapter(Protocol):
    def read(self, intent: AppReadIntent, config: ConnectedAppConfig) -> Dict[str, Any]:
        """Read data from app based on intent."""
        ...
    
    def execute_step(self, step: PlanStep, config: ConnectedAppConfig) -> StepResult:
        """Execute a single plan step."""
        ...
    
    def supports_action(self, action: str) -> bool:
        """Check if adapter supports a specific action."""
        ...
```

### App Categories

Apps được phân loại:

- **POS_SIMPLE**: KiotViet, Misa eShop, Sapo - quản lý bán hàng đơn giản
- **ACCOUNTING**: MISA, Fast, Bravo - phần mềm kế toán
- **UNKNOWN**: Apps chưa phân loại

### Connection Methods

- **API**: Direct API calls (KiotViet, Misa eShop)
- **MCP**: Model Context Protocol server (custom apps)

### KiotViet Adapter Example

```python
class KiotVietAdapter:
    def read(self, intent: AppReadIntent, config: ConnectedAppConfig) -> Dict[str, Any]:
        client = KiotVietApiClient(config)
        
        if intent.kind == "LIST_PRODUCTS":
            products = client.list_products(...)
            return {"products": products}
        elif intent.kind == "LIST_INVOICES":
            invoices = client.list_invoices(...)
            return {"invoices": invoices}
        ...
    
    def execute_step(self, step: PlanStep, config: ConnectedAppConfig) -> StepResult:
        client = KiotVietApiClient(config)
        
        if step.action == "CREATE_PRODUCT":
            product = client.create_product(step.params)
            return StepResult(success=True, data=product)
        ...
```

### Adapter Registry

Adapters được đăng ký tại startup:

```python
from app.domain.apps.kiotviet.adapter import KiotVietAdapter
from app.domain.apps.registry import register_adapter

register_adapter("kiotviet", KiotVietAdapter())
```

Sử dụng trong graph nodes:

```python
from app.domain.apps.registry import get_adapter

adapter = get_adapter(app_config.app_id)
data = adapter.read(intent, app_config)
```

## Database Models

### Core Models

1. **User**: Người dùng
2. **Workspace**: Workspace (mỗi user có thể có nhiều workspace)
3. **Conversation**: Cuộc trò chuyện
4. **Message**: Tin nhắn trong conversation
5. **AgentRun**: LangGraph run
6. **AgentStep**: LangGraph step

### ConnectedApp Model

Thay thế `AppConnection`, model mới:

```python
class ConnectedApp(BaseModel):
    workspace_id: int
    app_id: str  # "kiotviet", "misa_eshop", ...
    name: str
    app_category: AppCategory  # POS_SIMPLE, ACCOUNTING, UNKNOWN
    connection_method: ConnectionMethod  # API, MCP
    
    # API connection fields
    client_id: Optional[str]
    client_secret_encrypted: Optional[str]
    retailer: Optional[str]  # For KiotViet
    
    # MCP connection fields
    mcp_url: Optional[str]
    mcp_auth_config_encrypted: Optional[str]
    
    # Status
    status: ConnectionStatus  # ACTIVE, INACTIVE, ERROR
```

### Relationships

```
User ──┬── Workspace ──┬── Conversation ──┬── Message
       │               │                  └── AgentRun ── AgentStep
       │               │
       │               └── ConnectedApp
       │
       └── (direct login)
```

## API Layer

### REST Endpoints

#### Authentication
- `POST /api/v1/auth/register` - Đăng ký
- `POST /api/v1/auth/login` - Đăng nhập
- `GET /api/v1/auth/me` - Thông tin user hiện tại

#### Workspace
- `GET /api/v1/workspaces` - List workspaces
- `POST /api/v1/workspaces` - Tạo workspace
- `GET /api/v1/workspaces/{id}` - Chi tiết workspace

#### Connected Apps
- `GET /api/v1/workspaces/{workspace_id}/connected-apps` - List apps
- `POST /api/v1/workspaces/{workspace_id}/connected-apps` - Tạo app connection
- `GET /api/v1/workspaces/{workspace_id}/connected-apps/{id}` - Chi tiết app
- `PUT /api/v1/workspaces/{workspace_id}/connected-apps/{id}` - Update app
- `DELETE /api/v1/workspaces/{workspace_id}/connected-apps/{id}` - Xóa app
- `POST /api/v1/workspaces/{workspace_id}/connected-apps/{id}/test` - Test connection

#### Chat
- `POST /api/v1/workspaces/{workspace_id}/chat` - Gửi message
- `GET /api/v1/workspaces/{workspace_id}/conversations` - List conversations
- `GET /api/v1/workspaces/{workspace_id}/conversations/{id}/messages` - Get messages

### Request/Response Flow

```
Client Request
    ↓
API Route (FastAPI)
    ↓
Service Layer (ChatService, ConnectedAppService, ...)
    ↓
Repository Layer (MessageRepository, ConnectedAppRepository, ...)
    ↓
Database (PostgreSQL)
```

## Security

### Authentication & Authorization

- **JWT tokens**: User authentication
- **Workspace ownership**: Users chỉ có thể access workspaces của họ
- **Token expiration**: Configurable (default 30 minutes)

### Encryption

Sensitive data được encrypt trước khi lưu database:
- `client_secret` (OAuth credentials)
- `mcp_auth_config` (MCP authentication)

Sử dụng **Fernet** (symmetric encryption) với key từ `ENCRYPTION_KEY` environment variable.

### API Security

- **CORS**: Configurable origins
- **Rate limiting**: (Future: Redis-based)
- **Input validation**: Pydantic schemas

## Performance Considerations

### LLM Token Optimization

- **Conversation history**: Giới hạn 3 messages gần nhất
- **App data**: Giới hạn số lượng items (ví dụ: 5 products đầu tiên)
- **Model selection**: Sử dụng models rẻ hơn cho intent classification và simple tasks

### Caching (Future)

- **OAuth tokens**: Redis cache để tránh refresh liên tục
- **API responses**: Cache kết quả từ external APIs
- **LLM responses**: Cache responses cho câu hỏi tương tự

## Future Enhancements

1. **Redis Integration**: OAuth token caching, rate limiting
2. **RAG (Retrieval-Augmented Generation)**: Knowledge base cho domain-specific questions
3. **Streaming Responses**: Real-time streaming từ LangGraph
4. **Multi-language Support**: Hỗ trợ tiếng Anh, tiếng Việt
5. **More App Adapters**: Misa eShop, Sapo, MISA accounting

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Adapter Pattern](https://refactoring.guru/design-patterns/adapter)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)

---

**Last updated**: 2025-01-XX

