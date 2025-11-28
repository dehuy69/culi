# Local Development Guide

Guide for setting up and running Culi Backend in a local development environment.

**Language**: [English](README_en.md) | [Tiếng Việt](README.md)

## Development Architecture

The development workflow uses a **hybrid approach**:
- **Dependencies** (PostgreSQL, Redis, ...) run in Docker containers
- **Application code** (Culi backend) runs directly on local machine with Python

Benefits:
- ✅ Code changes are reflected immediately (hot reload)
- ✅ Easy to debug and use IDE tools
- ✅ Dependencies are managed centrally with Docker
- ✅ No need to rebuild Docker image when code changes

## Prerequisites

Make sure you have installed:

1. **Python 3.10+**
   ```bash
   python3 --version
   ```

2. **Docker & Docker Compose**
   ```bash
   docker --version
   docker-compose --version
   ```

3. **Git**
   ```bash
   git --version
   ```

## Setup Manual - Step by Step

### Step 1: Create Virtual Environment

```bash
# Navigate to project root directory
cd /path/to/culi

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# Verify activation was successful (prompt will have (venv) prefix)
which python  # Linux/Mac
where python  # Windows
```

### Step 2: Install Python Dependencies

```bash
# Make sure venv is activated (prompt shows (venv))
# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation was successful
pip list
```

### Step 3: Create and Configure Environment Variables

```bash
# Copy template file
cp .env.example .env

# Open .env file to edit
# Linux/Mac:
nano .env
# or
vim .env
# or use another editor

# Windows:
notepad .env
```

**Environment variables to configure:**

```env
# Database - keep default
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/culi_db

# JWT Secret - generate random string (minimum 32 characters)
# Example: openssl rand -hex 32
SECRET_KEY=your-random-secret-key-minimum-32-characters-long

# OpenRouter API Key - REQUIRED
# Sign up at: https://openrouter.ai
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Encryption Key - REQUIRED
# Generate with Python:
python scripts/generate_encryption_key.py
# Copy output and paste here
ENCRYPTION_KEY=your-encryption-key-from-script

# Google Search (Optional - for web search features)
GOOGLE_SEARCH_API_KEY=your-google-api-key
GOOGLE_SEARCH_CX=your-search-engine-id

# Logging
LOG_LEVEL=INFO
DEBUG=True

# Application
APP_NAME=culi-backend
APP_VERSION=0.1.0
```

**Generate Encryption Key:**

```bash
# Run script to generate key
python scripts/generate_encryption_key.py

# Copy output and add to .env file
```

### Step 4: Start Dependencies with Docker Compose

```bash
# Navigate to local_dev folder
cd local_dev

# Verify docker-compose.yml exists
ls -la docker-compose.yml

# Start PostgreSQL service
docker-compose up -d postgres

# Check containers are running
docker-compose ps

# View logs to ensure PostgreSQL is ready
docker-compose logs postgres

# Test connection (wait about 3-5 seconds after starting)
docker-compose exec postgres pg_isready -U postgres
```

**Expected output:**
```
postgres:5432 - accepting connections
```

### Step 5: Setup Database Schema

**⚠️ Note:** Migrations are NOT included in the open source repository. You need to create migrations yourself for local development.

```bash
# Return to root directory
cd ..

# Make sure venv is activated
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Create initial migration from SQLAlchemy models
alembic revision --autogenerate -m "Initial migration with all models"

# Review migration file in migrations/versions/ (if needed)

# Apply migration to create database schema
alembic upgrade head

# Verify results
# If successful, you will see tables being created
```

**Note:** Migration files created will not be committed to repository (already ignored in .gitignore).

**Verify database:**

```bash
# Connect to PostgreSQL
docker-compose -f local_dev/docker-compose.yml exec postgres psql -U postgres -d culi_db

# In psql shell, check tables
\dt

# Exit psql
\q
```

### Step 6: Start Development Server

```bash
# Make sure venv is activated
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Start FastAPI development server with hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Server will start and display:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

**Verify server:**

- Open browser and visit:
  - API: http://localhost:8000
  - API Docs: http://localhost:8000/docs
  - Health Check: http://localhost:8000/api/v1/health

**Test API:**

```bash
# In another terminal, test health endpoint
curl http://localhost:8000/api/v1/health

# Or open in browser:
# http://localhost:8000/api/v1/health
```

## Daily Development Workflow

### Morning - Start Working

**1. Start Dependencies (Docker):**

```bash
# Navigate to local_dev folder
cd local_dev

# Start PostgreSQL
docker-compose up -d postgres

# Check status
docker-compose ps

# If containers are already running, you can skip this step
```

**2. Activate Virtual Environment:**

```bash
# Return to root directory
cd ..

# Activate venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows
```

**3. Start Development Server:**

```bash
# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Keep this terminal open, server will automatically reload when code changes
```

### While Coding

- Server is running with `--reload` flag
- All code changes will automatically reload the server
- View logs in terminal to debug
- Test at: http://localhost:8000/docs

### Evening - End Working

**1. Stop Development Server:**

```bash
# In terminal running server, press:
Ctrl + C
```

**2. Stop Dependencies (Optional):**

```bash
# Navigate to local_dev folder
cd local_dev

# Stop PostgreSQL (optional - can keep running)
docker-compose down

# Or just stop without deleting volumes
docker-compose stop
```

## Database Operations

### Access PostgreSQL Database

**Method 1: Use psql from Docker**

```bash
# Navigate to local_dev folder
cd local_dev

# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d culi_db

# In psql shell:
\dt              # List all tables
\d users         # Describe users table
SELECT * FROM users LIMIT 5;  # Query example
\q               # Quit
```

**Method 2: Use psql from local (if installed)**

```bash
# Connect directly
psql postgresql://postgres:postgres@localhost:5432/culi_db
```

### pgAdmin - Database GUI (Optional)

```bash
# Navigate to local_dev folder
cd local_dev

# Start pgAdmin with tools profile
docker-compose --profile tools up -d pgadmin

# Open browser and visit:
# http://localhost:5050

# Login:
# Email: admin@culi.local
# Password: admin

# Add server in pgAdmin:
# Host: postgres (service name in docker-compose)
# Port: 5432
# Database: culi_db
# Username: postgres
# Password: postgres
```

### Database Migrations

**Create new migration:**

```bash
# Make sure venv is activated
source venv/bin/activate

# Create migration from model changes
alembic revision --autogenerate -m "describe your changes"

# Migration file will be created in migrations/versions/
# Review and edit if needed
```

**View migration files:**

```bash
ls -la migrations/versions/
```

**Apply migrations:**

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>

# View migration history
alembic history
```

**Rollback migration:**

```bash
# Rollback one step
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all
alembic downgrade base
```

**Reset Database (DELETE ALL DATA):**

```bash
# Step 1: Stop and remove PostgreSQL container + volumes
cd local_dev
docker-compose down -v postgres

# Step 2: Start PostgreSQL again
docker-compose up -d postgres

# Step 3: Wait for PostgreSQL to be ready (about 3-5 seconds)
sleep 5

# Step 4: Check connection
docker-compose exec postgres pg_isready -U postgres

# Step 5: Run migrations again
cd ..
alembic upgrade head
```

## Testing

### Run Tests

```bash
# Make sure venv is activated
source venv/bin/activate

# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_api/test_auth.py

# Run specific test function
pytest tests/test_api/test_auth.py::test_register

# Run tests with coverage
pytest --cov=app --cov-report=html

# View coverage report
# Open file: htmlcov/index.html in browser
```

### Test Database (Separate from Dev)

If you need a separate test database:

```bash
# Create test database in PostgreSQL
docker-compose -f local_dev/docker-compose.yml exec postgres psql -U postgres -c "CREATE DATABASE culi_test_db;"

# Update .env with test database URL
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/culi_test_db

# Run migrations on test DB
alembic upgrade head
```

## Code Quality

### Format Code

```bash
# Make sure venv is activated
source venv/bin/activate

# Format code with black
black app/ tests/

# Check format without changing
black --check app/ tests/
```

### Lint Code

```bash
# Lint with ruff
ruff check app/ tests/

# Auto-fix fixable errors
ruff check --fix app/ tests/
```

### Type Checking

```bash
# Type check with mypy
mypy app/

# If there are errors, fix each file
```

## Troubleshooting

### PostgreSQL Cannot Connect

**1. Check container is running:**

```bash
cd local_dev
docker-compose ps
```

**If container is not running:**

```bash
# Start again
docker-compose up -d postgres

# View logs
docker-compose logs postgres
```

**2. Check port 5432:**

```bash
# Linux/Mac
lsof -i :5432

# If another process is using the port
# Kill process or change port in docker-compose.yml
```

**3. Test connection:**

```bash
# Test from Docker
docker-compose exec postgres pg_isready -U postgres

# Test from local
psql postgresql://postgres:postgres@localhost:5432/culi_db -c "SELECT 1;"
```

### Port 8000 Already in Use

**1. Find process using port:**

```bash
# Linux/Mac
lsof -i :8000

# Kill process
kill -9 <PID>
```

**2. Or change port:**

```bash
uvicorn app.main:app --reload --port 8001
```

### Migration Errors

**1. View migration history:**

```bash
alembic history
```

**2. Check current revision:**

```bash
# In database
docker-compose -f local_dev/docker-compose.yml exec postgres psql -U postgres -d culi_db -c "SELECT * FROM alembic_version;"
```

**3. Reset and run again:**

```bash
# Delete all migrations and reset database
cd local_dev
docker-compose down -v postgres
docker-compose up -d postgres
sleep 5
cd ..
alembic upgrade head
```

### Import Errors / Module Not Found

**1. Check venv is activated:**

```bash
which python  # Should show venv path
# or
where python  # Windows
```

**2. Reinstall dependencies:**

```bash
# Deactivate venv first
deactivate

# Delete old venv (if needed)
rm -rf venv  # Linux/Mac
# or: rmdir /s venv  # Windows

# Recreate venv
python3 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac

# Reinstall
pip install --upgrade pip
pip install -r requirements.txt
```

### Environment Variables Not Loaded

**1. Check .env file exists:**

```bash
ls -la .env
```

**2. Check .env format:**

```bash
# No spaces around =
# Correct: KEY=value
# Wrong:  KEY = value

# No quotes (unless value has spaces)
# Correct: KEY=value
# Wrong:  KEY="value"
```

**3. Reload environment:**

```bash
# Stop server (Ctrl+C)
# Start server again
uvicorn app.main:app --reload
```

### Virtual Environment Issues

**1. Venv won't activate:**

```bash
# Check activate file exists
ls -la venv/bin/activate  # Linux/Mac
# or
dir venv\Scripts\activate  # Windows

# If not, recreate venv
python3 -m venv venv
```

**2. Python version incorrect:**

```bash
# Check version
python3 --version  # Should be 3.10+

# If incorrect, install Python 3.10+ first
```

## Project Structure

```
culi/
├── app/                    # Application code
│   ├── api/               # API routes
│   ├── core/              # Core configuration
│   ├── db/                # Database setup
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   └── ...
├── local_dev/             # Local development files
│   ├── docker-compose.yml # Dependencies configuration
│   └── README.md          # This file
├── migrations/            # Database migrations
├── scripts/               # Utility scripts
├── tests/                 # Tests
├── venv/                  # Virtual environment (gitignored)
├── .env                   # Environment variables (gitignored)
└── requirements.txt       # Python dependencies
```

## Useful Commands Reference

### Dependencies Management

```bash
# Start PostgreSQL
cd local_dev && docker-compose up -d postgres

# Stop PostgreSQL
cd local_dev && docker-compose down

# View logs
cd local_dev && docker-compose logs -f postgres

# Check status
cd local_dev && docker-compose ps

# Restart PostgreSQL
cd local_dev && docker-compose restart postgres
```

### Application Development

```bash
# Activate venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Start server
uvicorn app.main:app --reload

# Run migrations
alembic upgrade head

# Create migration
alembic revision --autogenerate -m "description"
```

### Database Operations

```bash
# Access PostgreSQL
docker-compose -f local_dev/docker-compose.yml exec postgres psql -U postgres -d culi_db

# Start pgAdmin
cd local_dev && docker-compose --profile tools up -d pgadmin
```

### Testing & Quality

```bash
# Run tests
pytest

# Format code
black app/ tests/

# Lint code
ruff check app/ tests/
```

## Tips & Best Practices

1. **Keep dependencies running all day** - Only stop when not in use to avoid having to set up again

2. **Use separate terminal for server** - Easy to track logs, not mixed with other commands

3. **Auto-reload enabled** - Server automatically reloads when code changes, no manual restart needed

4. **IDE Integration** - Setup Python interpreter in IDE to point to `venv/bin/python` for autocomplete and debugging

5. **Debugging** - Use IDE debugger (VS Code, PyCharm) to debug local Python process

6. **Environment Variables** - Don't commit `.env` file, keep secrets local

7. **Migrations** - Always review migration files before applying, especially auto-generated ones

## Next Steps

- Explore API docs at http://localhost:8000/docs when server is running
- Read [Architecture Documentation](../docs/ARCHITECTURE_en.md) to understand system design
- See [Main README](../README_en.md) for project overview

## Getting Help

If you encounter issues:
1. Check the Troubleshooting section above
2. View logs: `docker-compose logs` or server logs in terminal
3. Check `.env` file and database connection
4. Make sure you followed the setup steps correctly

