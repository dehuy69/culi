# Culi Backend

AI kế toán cho hộ kinh doanh Việt Nam, kết nối MCP KiotViet

## Tech Stack

- FastAPI
- SQLAlchemy + Alembic
- PostgreSQL
- LangChain + LangGraph
- OpenRouter (LLM)
- Google Custom Search API

## Setup

Xem hướng dẫn đầy đủ tại: **[local_dev/README.md](local_dev/README.md)**

**Tóm tắt workflow:**

1. **Tạo virtual environment và cài dependencies:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Cấu hình environment:**
   ```bash
   cp .env.example .env
   # Chỉnh sửa .env với API keys của bạn
   ```

3. **Start dependencies (PostgreSQL trong Docker):**
   ```bash
   cd local_dev
   docker-compose up -d postgres
   ```

4. **Setup database schema:**
   ```bash
   cd ..
   alembic upgrade head
   ```

5. **Start application (local terminal):**
   ```bash
   source venv/bin/activate
   uvicorn app.main:app --reload
   ```

**Workflow:**
- Dependencies (PostgreSQL, Redis, ...) chạy trong Docker
- Application code chạy trực tiếp trên máy local (hot reload)
- Khuyến khích thực hiện manual từng bước để hiểu rõ quy trình

## Development

### Local Development

**Xem hướng dẫn đầy đủ:** [local_dev/README.md](local_dev/README.md)

**Commands cơ bản:**

```bash
# Dependencies
cd local_dev && ./start_dependencies.sh     # Start PostgreSQL, etc.
cd local_dev && ./stop_dependencies.sh      # Stop dependencies

# Application
source venv/bin/activate                    # Activate venv
uvicorn app.main:app --reload               # Start server (hot reload)

# Database
alembic upgrade head                        # Run migrations
alembic revision --autogenerate -m "desc"   # Create migration

# Testing
pytest                                      # Run tests
pytest --cov=app                            # With coverage
```

### Database Access

```bash
# PostgreSQL shell
docker-compose -f local_dev/docker-compose.yml exec postgres psql -U postgres -d culi_db

# pgAdmin (Web GUI)
cd local_dev && docker-compose --profile tools up -d pgadmin
# Access: http://localhost:5050
```

## Project Structure

See `_prompts/ref-folder-tree.md` for detailed structure documentation.

