# ✅ Checklist Setup Local Development

## Prerequisites Check

- [ ] Python 3.10+ installed: `python3 --version`
- [ ] Docker installed: `docker --version`
- [ ] Docker Compose installed: `docker compose version` (hoặc `docker-compose --version`)

## Setup Steps

### 1. Virtual Environment

```bash
cd /home/huy/Documents/culi

# Tạo venv
python3 -m venv venv

# Activate
source venv/bin/activate

# Verify
which python  # Should show path to venv/bin/python
```

**✅ Check:** Prompt terminal có prefix `(venv)`

### 2. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install từ requirements.txt
pip install -r requirements.txt

# Verify
pip list | grep fastapi  # Should show fastapi
```

**✅ Check:** FastAPI và các packages được cài đặt

### 3. Environment Variables

```bash
# Copy .env.example
cp .env.example .env

# Generate encryption key
python scripts/generate_encryption_key.py
# Copy output và paste vào .env

# Generate secret key
openssl rand -hex 32
# Copy output và paste vào .env

# Edit .env file
nano .env  # hoặc dùng editor khác
```

**Cần điền:**
- [ ] `OPENROUTER_API_KEY` - Lấy từ https://openrouter.ai
- [ ] `SECRET_KEY` - Đã generate
- [ ] `ENCRYPTION_KEY` - Đã generate
- [ ] (Optional) `GOOGLE_SEARCH_API_KEY` và `GOOGLE_SEARCH_CX`

**✅ Check:** File `.env` có đầy đủ các giá trị

### 4. Start PostgreSQL

```bash
cd local_dev

# Start PostgreSQL container (Docker Compose v2)
docker compose -f local_dev/docker-compose.yml up -d postgres

# Check status
docker compose -f local_dev/docker-compose.yml ps

# Check logs
docker compose -f local_dev/docker-compose.yml logs postgres

# Test connection
docker compose -f local_dev/docker-compose.yml exec postgres pg_isready -U postgres
```

**✅ Check:** Output là `postgres:5432 - accepting connections`

### 5. Database Migration

**⚠️ Lưu ý:** Migrations không được include trong open source repository. Bạn cần tự tạo migration cho local development.

```bash
cd ..  # Quay về root

# Activate venv nếu chưa
source venv/bin/activate

# Tạo migration đầu tiên từ SQLAlchemy models
alembic revision --autogenerate -m "Initial migration with all models"

# Review migration file trong migrations/versions/ (nếu cần)

# Apply migration để tạo database schema
alembic upgrade head
```

**✅ Check:** 
```bash
# Kiểm tra database có tables chưa
docker compose -f local_dev/docker-compose.yml exec postgres psql -U postgres -d culi_db -c "\dt"
```

**Expected:** Có các tables: users, workspaces, connected_apps, conversations, messages, etc.

**Note:** Migration files được tạo sẽ không được commit vào repository (đã được ignore trong .gitignore)

### 6. Start Server

```bash
# Đảm bảo đã activate venv
source venv/bin/activate

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**✅ Check:** 
- Terminal hiển thị: `Uvicorn running on http://0.0.0.0:8000`
- Mở browser: http://localhost:8000/docs
- Health check: http://localhost:8000/api/v1/health

## Verify Everything Works

### Test 1: Health Check

```bash
curl http://localhost:8000/api/v1/health
```

**Expected:** `{"status":"healthy"}`

### Test 2: API Docs

Mở browser: http://localhost:8000/docs

**Expected:** Swagger UI hiển thị

### Test 3: Register User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword123",
    "full_name": "Test User"
  }'
```

**Expected:** Response với user data và token

## Troubleshooting

### ❌ Lỗi: "Module not found"

**Giải pháp:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### ❌ Lỗi: "Cannot connect to database"

**Giải pháp:**
```bash
cd local_dev
docker compose ps  # Check PostgreSQL đang chạy
docker compose restart postgres  # Restart nếu cần
```

### ❌ Lỗi: "No module named 'app'"

**Giải pháp:**
```bash
# Đảm bảo đang ở root directory
pwd  # Should show: /home/huy/Documents/culi

# Activate venv
source venv/bin/activate

# Install dependencies
pip install -e .
```

### ❌ Lỗi: "alembic: command not found"

**Giải pháp:**
```bash
source venv/bin/activate
pip install alembic
```

### ❌ Lỗi Migration: "Can't locate revision identified by 'head'"

**Giải pháp:**
```bash
# Tạo migration đầu tiên từ models
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

**Lưu ý:** Migrations không có trong repo, bạn cần tự tạo cho local development.

## Daily Workflow

### Start Working

```bash
# 1. Activate venv
source venv/bin/activate

# 2. Start PostgreSQL (nếu chưa chạy)
cd local_dev && docker-compose up -d postgres && cd ..

# 3. Start server
uvicorn app.main:app --reload
```

### Stop Working

```bash
# Ctrl+C để stop server

# (Optional) Stop PostgreSQL
cd local_dev && docker compose down
```

## Quick Reference

```bash
# Activate venv
source venv/bin/activate

# Start PostgreSQL
cd local_dev && docker compose up -d postgres && cd ..

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload

# View database
docker compose -f local_dev/docker-compose.yml exec postgres psql -U postgres -d culi_db

# View logs
docker compose -f local_dev/docker-compose.yml logs -f postgres
```

