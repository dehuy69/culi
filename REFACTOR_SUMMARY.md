# Refactor Summary: Adapter Pattern Architecture

## Tổng quan

Refactor toàn bộ codebase từ hardcoded MCP connection sang **adapter pattern** với **domain layer**. Hệ thống giờ đây hỗ trợ nhiều loại apps với các phương thức kết nối khác nhau (API, MCP).

## Các thay đổi chính

### 1. Domain Layer (NEW)

**Location**: `app/domain/apps/`

#### 1.1 Base Classes (`base.py`)
- `AppCategory`: POS_SIMPLE, ACCOUNTING, UNKNOWN
- `ConnectionMethod`: API, MCP
- `ConnectedAppConfig`: Pydantic model cho app config
- `AppReadIntent`: Intent đọc dữ liệu
- `PlanStep`, `Plan`, `StepResult`: Models cho plan execution
- `BaseAppAdapter`: Protocol interface cho tất cả adapters

#### 1.2 Adapter Registry (`registry.py`)
- `ADAPTER_REGISTRY`: Dictionary chứa adapters
- `register_adapter()`: Đăng ký adapter
- `get_adapter()`: Lấy adapter, fallback về UnknownAppAdapter

#### 1.3 Unknown Adapter (`unknown/adapter.py`)
- Generic adapter cho apps chưa phân loại
- Hạn chế operations, chỉ hỗ trợ read cơ bản

#### 1.4 KiotViet Adapter (`kiotviet/`)
- **`config.py`**: KiotVietConfig model
- **`api_client.py`**: KiotVietApiClient (refactor từ kiotviet_direct_client.py)
- **`mappers.py`**: Mapper functions để normalize data
- **`adapter.py`**: KiotVietAdapter implements BaseAppAdapter

### 2. Database Models

#### 2.1 ConnectedApp Model (NEW)
**File**: `app/models/connected_app.py`
- Thay thế `AppConnection` model cũ
- Fields: `app_id`, `app_category`, `connection_method`
- Hỗ trợ cả API và MCP connections

#### 2.2 AppConnection Model (DEPRECATED)
**File**: `app/models/app_connection.py`
- Giữ lại để backward compatibility
- Không nên dùng trong code mới

### 3. LangGraph State

**File**: `app/graph/state.py`

#### Thay đổi:
- ❌ Remove: `mcp_connection`, `app_connections`, `active_connection`, `active_connection_type`, `active_client`
- ✅ Add: `connected_app: Optional[ConnectedApp]`
- ✅ Change: `mcp_data` → `app_data`
- ✅ Change: `needs_mcp` → `needs_app`
- ✅ Update intents: `mcp_read` → `app_read`, `mcp_plan` → `app_plan`
- ✅ Add: `intent = "no_app"`

### 4. LangGraph Nodes

#### 4.1 New Nodes
- **`intent_router_node.py`**: Router với intents mới (general_qa, tax_qa, app_read, app_plan, no_app)
- **`app_plan_node.py`**: Plan generation với strategy theo app category
- **`load_context_node.py`**: Load workspace, connected app, conversation history

#### 4.2 Refactored Nodes
- **`app_read_node.py`**: Generic, sử dụng adapter pattern
- **`execute_plan_node.py`**: Generic, sử dụng adapter pattern
- **`answer_node.py`**: Update để dùng `app_data` thay vì `mcp_data`
- **`context_node.py`**: Update routing logic

#### 4.3 Deprecated Nodes (kept for backward compatibility)
- **`router_node.py`** → Use `intent_router_node.py`
- **`mcp_read_node.py`** → Use `app_read_node.py`
- **`planner_node.py`** → Use `app_plan_node.py`
- **`connection_resolver_node.py`** → Logic moved to `load_context_node.py` (DELETED)

### 5. Graph Flow

**File**: `app/graph/app_graph.py`

#### Routing mới:
- Entry: `intent_router_node`
- Routes:
  - `general_qa` → `context_node` → `answer_node`
  - `tax_qa` → `web_search_node` → `answer_node`
  - `app_read` → `context_node` → `app_read_node` → `answer_node`
  - `app_plan` → `context_node` → `app_plan_node` → `present_plan_node` → `execute_plan_node`
  - `no_app` → `answer_node` (thông báo cần cấu hình app)

### 6. Services

#### 6.1 ChatService
**File**: `app/services/chat_service.py`
- Update để load `ConnectedApp` từ DB
- Map to `ConnectedAppConfig` và set vào state
- Remove old `mcp_connection` logic

#### 6.2 ConnectedAppService (NEW)
**File**: `app/services/connected_app_service.py`
- Service cho connected apps
- Methods: `create_connected_app()`, `test_connection()`, `set_default_connection()`
- Sử dụng adapter để test connections

#### 6.3 AppConnectionService (DEPRECATED)
**File**: `app/services/app_connection_service.py`
- Giữ lại để backward compatibility

### 7. API & Schemas

#### 7.1 Connected App Router (NEW)
**File**: `app/api/v1/connected_app_router.py`
- Endpoints:
  - `GET /workspaces/{id}/connected-apps/supported` - List supported apps
  - `POST /workspaces/{id}/connected-apps/connect` - Create connection
  - `GET /workspaces/{id}/connected-apps/connections` - List connections
  - `GET /workspaces/{id}/connected-apps/connections/{id}` - Get connection
  - `PUT /workspaces/{id}/connected-apps/connections/{id}` - Update connection
  - `DELETE /workspaces/{id}/connected-apps/connections/{id}` - Delete connection
  - `POST /workspaces/{id}/connected-apps/connections/{id}/test` - Test connection
  - `POST /workspaces/{id}/connected-apps/connections/{id}/set-default` - Set default

#### 7.2 Schemas (NEW)
**File**: `app/schemas/connected_app.py`
- `ConnectedAppCreate`, `ConnectedAppUpdate`
- `ConnectedAppResponse`, `SupportedAppResponse`
- `TestConnectionResponse`

#### 7.3 App Connection Router (DEPRECATED)
**File**: `app/api/v1/app_connection_router.py`
- Giữ lại để backward compatibility

### 8. Repositories

#### 8.1 ConnectedAppRepository (NEW)
**File**: `app/repositories/connected_app_repo.py`
- CRUD operations cho `ConnectedApp` model
- Filter by `app_category`, `connection_method`

#### 8.2 AppConnectionRepository (DEPRECATED)
**File**: `app/repositories/app_connection_repo.py`
- Giữ lại để backward compatibility

## File Structure

```
app/
├── domain/                          # NEW: Domain layer
│   └── apps/
│       ├── base.py                  # Base classes, enums, interfaces
│       ├── registry.py              # Adapter registry
│       ├── kiotviet/                # KiotViet implementation
│       │   ├── config.py
│       │   ├── api_client.py        # Refactored from kiotviet_direct_client.py
│       │   ├── mappers.py
│       │   └── adapter.py
│       └── unknown/
│           └── adapter.py
├── models/
│   ├── connected_app.py             # NEW: Replaces AppConnection
│   └── app_connection.py            # DEPRECATED: Kept for backward compatibility
├── repositories/
│   ├── connected_app_repo.py        # NEW
│   └── app_connection_repo.py       # DEPRECATED
├── services/
│   ├── connected_app_service.py     # NEW
│   └── app_connection_service.py    # DEPRECATED
├── graph/
│   ├── state.py                     # Updated with connected_app
│   ├── nodes/
│   │   ├── intent_router_node.py    # NEW: Replaces router_node
│   │   ├── app_read_node.py         # Refactored to use adapter
│   │   ├── app_plan_node.py         # NEW: Replaces planner_node
│   │   ├── execute_plan_node.py     # Refactored to use adapter
│   │   └── load_context_node.py     # NEW
│   └── app_graph.py                 # Updated routing
└── api/v1/
    ├── connected_app_router.py      # NEW
    └── app_connection_router.py     # DEPRECATED
```

## Migration Notes

1. **Database**: Table `connected_apps` sẽ được tạo trong migration đầu tiên
2. **Backward Compatibility**: Các file cũ được giữ lại và đánh dấu DEPRECATED
3. **Adapter Registration**: Adapters được đăng ký trong `app/domain/apps/__init__.py`
4. **Import Order**: Domain apps được import trong `app/main.py` startup để đảm bảo adapters được register

## Next Steps

1. ✅ Domain layer foundation
2. ✅ KiotViet adapter implementation
3. ✅ State & models refactor
4. ✅ Graph nodes refactor
5. ✅ Graph flow update
6. ✅ Services & API update
7. ✅ Cleanup (partial - deprecated files kept for now)

## Testing Checklist

- [ ] Test KiotViet adapter với real API
- [ ] Test graph flow end-to-end
- [ ] Test API endpoints
- [ ] Test adapter registry
- [ ] Test với multiple app categories

## Breaking Changes

- State structure đã thay đổi: `mcp_connection` → `connected_app`
- Intent values: `mcp_read` → `app_read`, `mcp_plan` → `app_plan`
- Model: `AppConnection` → `ConnectedApp` (nhưng DB table có thể giữ tên cũ nếu cần)

## Backward Compatibility

- Các file deprecated được giữ lại
- Old intents được map sang new intents trong routing
- `mcp_data` field vẫn được giữ trong state để compatibility (nhưng nên dùng `app_data`)

