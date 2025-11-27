# Local Development Setup Guide

## Prerequisites

- Python 3.10+
- Docker and Docker Compose
- Git

## Quick Start

### Option 1: Local Development (Python venv)

1. **Setup environment:**
   ```bash
   make setup
   # or
   ./scripts/setup_local_dev.sh
   ```

2. **Start PostgreSQL:**
   ```bash
   make up
   # or
   docker-compose -f docker-compose-local-dev.yml up -d
   ```

3. **Setup database schema:**
   ```bash
   # Migrations are not included in repository - generate first
   alembic revision --autogenerate -m "Initial migration"
   # Then apply
   alembic upgrade head
   ```
   
   **Note:** Migrations are managed separately in production. See [MIGRATIONS.md](../MIGRATIONS.md) for details.

4. **Start development server:**
   ```bash
   make dev
   # or
   uvicorn app.main:app --reload
   ```

5. **Access API:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - Health: http://localhost:8000/api/v1/health

### Option 2: Docker Development

1. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Generate encryption key:**
   ```bash
   make gen-key
   # Copy the generated key to .env as ENCRYPTION_KEY
   ```

3. **Start everything:**
   ```bash
   make dev-docker
   # or
   ./scripts/docker_dev.sh up
   ```

4. **Access services:**
   - API: http://localhost:8000
   - Docs: http://localhost:8000/docs
   - PostgreSQL: localhost:5432

## Environment Variables

Copy `.env.example` to `.env` and configure:

### Required

- `OPENROUTER_API_KEY` - Get from https://openrouter.ai
- `SECRET_KEY` - Random string (min 32 chars) for JWT
- `ENCRYPTION_KEY` - Generate with `make gen-key`

### Optional

- `GOOGLE_SEARCH_API_KEY` - For web search features
- `GOOGLE_SEARCH_CX` - Google Custom Search Engine ID
- `DATABASE_URL` - Defaults to local PostgreSQL

## Database Management

### Access Database

**Local:**
```bash
psql postgresql://postgres:postgres@localhost:5432/culi_db
```

**Docker:**
```bash
make db
# or
docker-compose exec postgres psql -U postgres -d culi_db
```

### pgAdmin (Web GUI)

```bash
make pgadmin
# Access at http://localhost:5050
# Email: admin@culi.local
# Password: admin
```

### Create Migration

**Note:** Migration files are excluded from repository. Generated migrations are for local development only.

```bash
alembic revision --autogenerate -m "your migration description"
# Review generated file in migrations/versions/
# Apply migration
alembic upgrade head
```

### Reset Database

```bash
make reset-db
# WARNING: This deletes all data!
```

## Useful Commands

### Makefile Commands

```bash
make help           # Show all available commands
make setup          # Initial setup
make dev            # Run local dev server
make dev-docker     # Run in Docker
make up             # Start PostgreSQL
make down           # Stop services
make logs           # View logs
make shell          # Shell into container
make migrate        # Run migrations
make test           # Run tests
make lint           # Run linters
make format         # Format code
make clean          # Clean Docker resources
```

### Docker Script Commands

```bash
./scripts/docker_dev.sh up              # Start environment
./scripts/docker_dev.sh down            # Stop environment
./scripts/docker_dev.sh logs            # View logs
./scripts/docker_dev.sh shell           # Open shell
./scripts/docker_dev.sh db              # Open PostgreSQL shell
./scripts/docker_dev.sh migrate         # Run migrations
./scripts/docker_dev.sh migrate-create  # Create migration
./scripts/docker_dev.sh test            # Run tests
./scripts/docker_dev.sh clean           # Clean up
```

## Development Workflow

1. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make changes and test:**
   ```bash
   make dev
   # Test your changes at http://localhost:8000/docs
   ```

3. **Run tests:**
   ```bash
   make test
   ```

4. **Format code:**
   ```bash
   make format
   ```

5. **Check linter:**
   ```bash
   make lint
   ```

6. **Create migration if needed:**
   ```bash
   alembic revision --autogenerate -m "add new field"
   alembic upgrade head
   ```
   
   **Note:** Migration files are not committed to repository.

## Troubleshooting

### Database Connection Issues

1. Check if PostgreSQL is running:
   ```bash
   docker-compose -f docker-compose-local-dev.yml ps
   ```

2. Check database logs:
   ```bash
   docker-compose -f docker-compose-local-dev.yml logs postgres
   ```

3. Restart PostgreSQL:
   ```bash
   docker-compose -f docker-compose-local-dev.yml restart postgres
   ```

### Port Already in Use

If port 8000 or 5432 is already in use:

1. Find process using port:
   ```bash
   lsof -i :8000
   lsof -i :5432
   ```

2. Kill the process or change ports in docker-compose files

### Migration Issues

1. Reset database:
   ```bash
   make reset-db
   ```

2. Or manually:
   ```bash
   docker-compose -f docker-compose-local-dev.yml down -v postgres
   docker-compose -f docker-compose-local-dev.yml up -d postgres
   alembic upgrade head
   ```

### Import Errors

1. Ensure virtual environment is activated:
   ```bash
   source venv/bin/activate
   ```

2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Project Structure

```
culi/
├── app/                    # Application code
├── migrations/             # Database migrations
├── scripts/                # Development scripts
├── tests/                  # Tests
├── docker-compose.yml      # Docker setup
├── Dockerfile.dev         # Development Dockerfile
├── Makefile               # Development commands
└── .env                   # Environment variables (create from .env.example)
```

## Next Steps

1. Read [IMPLEMENTATION_STATUS.md](../IMPLEMENTATION_STATUS.md) for current status
2. Check [README.md](../README.md) for project overview
3. Explore API docs at http://localhost:8000/docs when server is running

