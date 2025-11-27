# Hướng dẫn chạy Culi ở Local - Quick Start

## Prerequisites

Đảm bảo bạn đã cài:
- ✅ Python 3.10+ (`python3 --version`)
- ✅ Docker & Docker Compose (`docker --version`, `docker-compose --version`)

## Checklist Setup

### Bước 1: Tạo Virtual Environment

```bash
cd /home/huy/Documents/culi

# Tạo venv
python3 -m venv venv

# Activate venv
source venv/bin/activate  # Linux/Mac

# Kiểm tra đã activate (prompt sẽ có prefix (venv))
which python
```

### Bước 2: Cài đặt Python Dependencies

```bash
# Đảm bảo đã activate venv (prompt có (venv))

# Upgrade pip
pip install --upgrade pip

# Cài đặt dependencies
pip install -r requirements.txt

# Verify
pip list | grep fastapi
```

### Bước 3: Tạo file .env

```bash
# Kiểm tra có .env.example không
ls -la .env.example

# Nếu có, copy từ example
cp .env.example .env

# Nếu không có, tạo file .env mới
touch .env
```

**Cấu hình file `.env` với các biến sau:**

```env
# Database - giữ nguyên default (PostgreSQL trong Docker)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/culi_db

# JWT Secret - tạo random string (32+ ký tự)
# Generate: openssl rand -hex 32
SECRET_KEY=your-secret-key-here-change-in-production-minimum-32-characters

# OpenRouter API Key - REQUIRED
# Đăng ký tại: https://openrouter.ai
OPENROUTER_API_KEY=

# Encryption Key - REQUIRED (32 bytes)
# Generate bằng script:
# python scripts/generate_encryption_key.py
ENCRYPTION_KEY=

# Google Search (Optional - cho web search features)
GOOGLE_SEARCH_API_KEY=
GOOGLE_SEARCH_CX=

# Logging
LOG_LEVEL=INFO
DEBUG=True

# Application
APP_NAME=culi-backend
APP_VERSION=0.1.0
```

**Generate Encryption Key:**
```bash
python scripts/generate_encryption_key.py
# Copy output và paste vào .env
```

**Generate Secret Key:**
```bash
openssl rand -hex 32
# Copy output và paste vào .env
```

### Bước 4: Start PostgreSQL với Docker

```bash
# Di chuyển vào folder local_dev
cd local_dev

# Start PostgreSQL container
docker-compose up -d postgres

# Kiểm tra container đang chạy
docker-compose ps

# Xem logs
docker-compose logs postgres

# Test connection (đợi 3-5 giây sau khi start)
docker-compose exec postgres pg_isready -U postgres
```

**Expected output:**
```
postgres:5432 - accepting connections
```

### Bước 5: Tạo Database Schema (Migration)

**⚠️ Lưu ý:** Migrations không được include trong open source repository. Bạn cần tự tạo migration cho local development.

```bash
# Quay về root directory
cd ..

# Đảm bảo đã activate venv
source venv/bin/activate  # Nếu chưa activate

# Tạo migration đầu tiên từ SQLAlchemy models
alembic revision --autogenerate -m "Initial migration with all models"

# Review migration file trong migrations/versions/ (nếu cần)

# Apply migration để tạo database schema
alembic upgrade head
```

**Note:** Migration files được tạo sẽ không được commit vào repository (đã được ignore).

**Verify database:**
```bash
# Kết nối vào PostgreSQL
docker-compose -f local_dev/docker-compose.yml exec postgres psql -U postgres -d culi_db

# Trong psql, kiểm tra tables
\dt

# Thoát
\q
```

### Bước 6: Start Development Server

```bash
# Đảm bảo đã activate venv
source venv/bin/activate

# Start FastAPI server với hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Bước 7: Test Application

Mở browser và truy cập:
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Troubleshooting

### Lỗi: Database connection failed

```bash
# Kiểm tra PostgreSQL đang chạy
docker-compose -f local_dev/docker-compose.yml ps

# Kiểm tra logs
docker-compose -f local_dev/docker-compose.yml logs postgres

# Restart PostgreSQL
docker-compose -f local_dev/docker-compose.yml restart postgres
```

### Lỗi: Module not found

```bash
# Đảm bảo đã activate venv
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Lỗi: Migration errors

```bash
# Xem migration hiện tại
alembic current

# Xem migration history
alembic history

# Nếu cần reset (CẨN THẬN - sẽ mất data)
# Chỉ làm trong development
alembic downgrade base
alembic upgrade head
```

### Lỗi: Port 8000 đã được sử dụng

```bash
# Tìm process đang dùng port 8000
lsof -i :8000  # Linux/Mac

# Hoặc dùng port khác
uvicorn app.main:app --reload --port 8001
```

## Common Commands

```bash
# Activate venv
source venv/bin/activate

# Start PostgreSQL
cd local_dev && docker-compose up -d postgres

# Stop PostgreSQL
cd local_dev && docker-compose down

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload

# View database
docker-compose -f local_dev/docker-compose.yml exec postgres psql -U postgres -d culi_db

# View logs
docker-compose -f local_dev/docker-compose.yml logs -f postgres
```

## Next Steps

Sau khi setup xong:
1. ✅ Test API endpoints tại http://localhost:8000/docs
2. ✅ Tạo user account qua `/api/v1/auth/register`
3. ✅ Login và lấy JWT token
4. ✅ Tạo workspace
5. ✅ Kết nối KiotViet app (cần client_id và client_secret)
6. ✅ Test chat API

## Tham khảo thêm

- Chi tiết hơn: [local_dev/README.md](local_dev/README.md)
- Development guide: [docs/LOCAL_DEV_SETUP.md](docs/LOCAL_DEV_SETUP.md)

