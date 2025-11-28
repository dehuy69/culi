# Culi Backend Architecture

This document describes the architecture and design of Culi Backend.

**Language**: [English](ARCHITECTURE_en.md) | [Tiếng Việt](ARCHITECTURE.md)

## 📋 Table of Contents

1. [Overview](#overview)
2. [Overall Architecture](#overall-architecture)
3. [LangGraph Architecture](#langgraph-architecture)
4. [Adapter Pattern](#adapter-pattern)
5. [Database Models](#database-models)
6. [API Layer](#api-layer)
7. [Security](#security)

## Overview

Culi Backend is an AI agent backend built with:
- **FastAPI** for REST API
- **LangGraph** for AI agent orchestration
- **Adapter Pattern** to support multiple types of external applications
- **Domain-Driven Design** for code organization

## Overall Architecture

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

LangGraph manages the workflow for processing user questions.

### Graph Flow

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ intent_router│ ◄─── Classify intent from user input
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

Classify intent from user input:
- **general_qa**: General questions, no app needed
- **tax_qa**: Tax questions, needs web search
- **app_read**: Read data from app
- **app_plan**: Plan operations on app
- **no_app**: App not configured

#### 2. `context_node`

Collect context:
- Conversation history (maximum 3 recent messages)
- Workspace information
- Connected app configuration

#### 3. `app_read_node`

Read data from connected app:
- Uses adapter pattern
- Dispatch based on `AppReadIntent.kind`
- Examples: LIST_PRODUCTS, LIST_INVOICES, SUMMARY_REVENUE

#### 4. `app_plan_node`

Create execution plan:
- Different strategies based on `app.category`:
  - `POS_SIMPLE`: Create products, invoices
  - `ACCOUNTING`: Map accounts, journal entries
  - `UNKNOWN`: Limited operations

#### 5. `execute_plan_node`

Execute plan step by step:
- Uses adapter pattern
- Execute each `PlanStep` in order
- Accumulate `StepResult` to create answer

#### 6. `answer_node`

Generate final answer:
- Synthesize context, app_data, web_results, step_results
- Use LLM to generate natural language response
- Format markdown, tables, lists

#### 7. `web_search_node`

Search for information on web:
- Uses Google Custom Search API
- For tax questions, regulations

#### 8. `present_plan_node`

Display plan for user approval:
- Only used in production with checkpoints
- Local development: auto-approve

### State

`CuliState` (TypedDict) contains all data flowing through the graph:

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

To generate LangGraph diagram:

```bash
python scripts/generate_langgraph_chart.py --format mermaid --output docs/langgraph_chart.mmd
```

Mermaid file can be rendered at [Mermaid Live Editor](https://mermaid.live/).

## Adapter Pattern

The adapter pattern allows the system to support multiple types of external applications in a generic way.

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

All adapters implement this interface:

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

Apps are categorized:

- **POS_SIMPLE**: KiotViet, Misa eShop, Sapo - simple sales management
- **ACCOUNTING**: MISA, Fast, Bravo - accounting software
- **UNKNOWN**: Uncategorized apps

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

Adapters are registered at startup:

```python
from app.domain.apps.kiotviet.adapter import KiotVietAdapter
from app.domain.apps.registry import register_adapter

register_adapter("kiotviet", KiotVietAdapter())
```

Used in graph nodes:

```python
from app.domain.apps.registry import get_adapter

adapter = get_adapter(app_config.app_id)
data = adapter.read(intent, app_config)
```

## Database Models

### Core Models

1. **User**: User
2. **Workspace**: Workspace (each user can have multiple workspaces)
3. **Conversation**: Conversation
4. **Message**: Message in conversation
5. **AgentRun**: LangGraph run
6. **AgentStep**: LangGraph step

### ConnectedApp Model

Replaces `AppConnection`, new model:

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
- `POST /api/v1/auth/register` - Register
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Current user information

#### Workspace
- `GET /api/v1/workspaces` - List workspaces
- `POST /api/v1/workspaces` - Create workspace
- `GET /api/v1/workspaces/{id}` - Workspace details

#### Connected Apps
- `GET /api/v1/workspaces/{workspace_id}/connected-apps` - List apps
- `POST /api/v1/workspaces/{workspace_id}/connected-apps` - Create app connection
- `GET /api/v1/workspaces/{workspace_id}/connected-apps/{id}` - App details
- `PUT /api/v1/workspaces/{workspace_id}/connected-apps/{id}` - Update app
- `DELETE /api/v1/workspaces/{workspace_id}/connected-apps/{id}` - Delete app
- `POST /api/v1/workspaces/{workspace_id}/connected-apps/{id}/test` - Test connection

#### Chat
- `POST /api/v1/workspaces/{workspace_id}/chat` - Send message
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
- **Workspace ownership**: Users can only access their own workspaces
- **Token expiration**: Configurable (default 30 minutes)

### Encryption

Sensitive data is encrypted before storing in database:
- `client_secret` (OAuth credentials)
- `mcp_auth_config` (MCP authentication)

Uses **Fernet** (symmetric encryption) with key from `ENCRYPTION_KEY` environment variable.

### API Security

- **CORS**: Configurable origins
- **Rate limiting**: (Future: Redis-based)
- **Input validation**: Pydantic schemas

## Performance Considerations

### LLM Token Optimization

- **Conversation history**: Limit to 3 most recent messages
- **App data**: Limit number of items (e.g., first 5 products)
- **Model selection**: Use cheaper models for intent classification and simple tasks

### Caching (Future)

- **OAuth tokens**: Redis cache to avoid constant refresh
- **API responses**: Cache results from external APIs
- **LLM responses**: Cache responses for similar questions

## Future Enhancements

1. **Redis Integration**: OAuth token caching, rate limiting
2. **RAG (Retrieval-Augmented Generation)**: Knowledge base for domain-specific questions
3. **Streaming Responses**: Real-time streaming from LangGraph
4. **Multi-language Support**: Support English, Vietnamese
5. **More App Adapters**: Misa eShop, Sapo, MISA accounting

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Adapter Pattern](https://refactoring.guru/design-patterns/adapter)
- [Domain-Driven Design](https://martinfowler.com/bliki/DomainDrivenDesign.html)

---

**Last updated**: 2025-01-XX

