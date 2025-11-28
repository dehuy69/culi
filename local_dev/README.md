# Local Development Guide

Hướng dẫn setup và chạy Culi Backend trong môi trường local development.

## Kiến trúc Development

Development workflow sử dụng **hybrid approach**:
- **Dependencies** (PostgreSQL, Redis, ...) chạy trong Docker containers
- **Application code** (Culi backend) chạy trực tiếp trên máy local với Python

Lợi ích:
- ✅ Code changes được phản ánh ngay lập tức (hot reload)
- ✅ Dễ dàng debug và sử dụng IDE tools
- ✅ Dependencies được quản lý tập trung bằng Docker
- ✅ Không cần rebuild Docker image khi code thay đổi

## Prerequisites

Đảm bảo bạn đã cài đặt:

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

## Setup Manual - Từng bước

### Bước 1: Tạo Virtual Environment

```bash
# Di chuyển vào root directory của project
cd /path/to/culi

# Tạo virtual environment
python3 -m venv venv

# Activate virtual environment
# Trên Linux/Mac:
source venv/bin/activate

# Trên Windows:
venv\Scripts\activate

# Kiểm tra đã activate thành công (prompt sẽ có prefix (venv))
which python  # Linux/Mac
where python  # Windows
```

### Bước 2: Cài đặt Dependencies Python

```bash
# Đảm bảo đã activate venv (prompt có (venv))
# Upgrade pip
pip install --upgrade pip

# Cài đặt các dependencies
pip install -r requirements.txt

# Kiểm tra cài đặt thành công
pip list
```

### Bước 3: Tạo và Cấu hình Environment Variables

```bash
# Copy file template
cp .env.example .env

# Mở file .env để chỉnh sửa
# Linux/Mac:
nano .env
# hoặc
vim .env
# hoặc dùng editor khác

# Windows:
notepad .env
```

**Các biến môi trường cần cấu hình:**

```env
# Database - giữ nguyên default
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/culi_db

# JWT Secret - tạo random string (tối thiểu 32 ký tự)
# Ví dụ: openssl rand -hex 32
SECRET_KEY=your-random-secret-key-minimum-32-characters-long

# OpenRouter API Key - REQUIRED
# Đăng ký tại: https://openrouter.ai
OPENROUTER_API_KEY=your-openrouter-api-key-here

# Encryption Key - REQUIRED
# Generate bằng Python:
python scripts/generate_encryption_key.py
# Copy output và paste vào đây
ENCRYPTION_KEY=your-encryption-key-from-script

# Google Search (Optional - cho web search features)
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
# Chạy script generate key
python scripts/generate_encryption_key.py

# Copy output và thêm vào .env file
```

### Bước 4: Start Dependencies với Docker Compose

```bash
# Di chuyển vào folder local_dev
cd local_dev

# Kiểm tra docker-compose.yml có tồn tại
ls -la docker-compose.yml

# Start PostgreSQL service
docker-compose up -d postgres

# Kiểm tra container đang chạy
docker-compose ps

# Xem logs để đảm bảo PostgreSQL đã sẵn sàng
docker-compose logs postgres

# Test connection (chờ khoảng 3-5 giây sau khi start)
docker-compose exec postgres pg_isready -U postgres
```

**Expected output:**
```
postgres:5432 - accepting connections
```

### Bước 5: Setup Database Schema

**⚠️ Lưu ý:** Migrations không được include trong open source repository. Bạn cần tự tạo migration cho local development.

```bash
# Quay về root directory
cd ..

# Đảm bảo đã activate venv
source venv/bin/activate  # Linux/Mac
# hoặc: venv\Scripts\activate  # Windows

# Tạo migration đầu tiên từ SQLAlchemy models
alembic revision --autogenerate -m "Initial migration with all models"

# Review migration file trong migrations/versions/ (nếu cần)

# Apply migration để tạo database schema
alembic upgrade head

# Kiểm tra kết quả
# Nếu thành công, sẽ thấy các bảng được tạo
```

**Note:** Migration files được tạo sẽ không được commit vào repository (đã được ignore trong .gitignore).

**Verify database:**

```bash
# Kết nối vào PostgreSQL
docker-compose -f local_dev/docker-compose.yml exec postgres psql -U postgres -d culi_db

# Trong psql shell, kiểm tra tables
\dt

# Thoát khỏi psql
\q
```

### Bước 6: Start Development Server

```bash
# Đảm bảo đã activate venv
source venv/bin/activate  # Linux/Mac
# hoặc: venv\Scripts\activate  # Windows

# Start FastAPI development server với hot reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Server sẽ start và hiển thị:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
```

**Kiểm tra server:**

- Mở browser và truy cập:
  - API: http://localhost:8000
  - API Docs: http://localhost:8000/docs
  - Health Check: http://localhost:8000/api/v1/health

**Test API:**

```bash
# Trong terminal khác, test health endpoint
curl http://localhost:8000/api/v1/health

# Hoặc dùng browser mở:
# http://localhost:8000/api/v1/health
```

## Development Workflow Hàng Ngày

### Sáng - Bắt đầu làm việc

**1. Start Dependencies (Docker):**

```bash
# Di chuyển vào folder local_dev
cd local_dev

# Start PostgreSQL
docker-compose up -d postgres

# Kiểm tra status
docker-compose ps

# Nếu container đã chạy rồi, có thể skip bước này
```

**2. Activate Virtual Environment:**

```bash
# Quay về root directory
cd ..

# Activate venv
source venv/bin/activate  # Linux/Mac
# hoặc: venv\Scripts\activate  # Windows
```

**3. Start Development Server:**

```bash
# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Giữ terminal này mở, server sẽ tự động reload khi code thay đổi
```

### Trong khi code

- Server đang chạy với `--reload` flag
- Mọi thay đổi code sẽ tự động reload server
- Xem logs trong terminal để debug
- Test tại: http://localhost:8000/docs

### Tối - Kết thúc làm việc

**1. Stop Development Server:**

```bash
# Trong terminal đang chạy server, nhấn:
Ctrl + C
```

**2. Stop Dependencies (Optional):**

```bash
# Di chuyển vào folder local_dev
cd local_dev

# Stop PostgreSQL (optional - có thể giữ chạy)
docker-compose down

# Hoặc chỉ stop mà không xóa volumes
docker-compose stop
```

## Database Operations

### Access PostgreSQL Database

**Cách 1: Dùng psql từ Docker**

```bash
# Di chuyển vào folder local_dev
cd local_dev

# Kết nối vào PostgreSQL
docker-compose exec postgres psql -U postgres -d culi_db

# Trong psql shell:
\dt              # List all tables
\d users         # Describe users table
SELECT * FROM users LIMIT 5;  # Query example
\q               # Quit
```

**Cách 2: Dùng psql từ local (nếu đã cài)**

```bash
# Kết nối trực tiếp
psql postgresql://postgres:postgres@localhost:5432/culi_db
```

### pgAdmin - Database GUI (Optional)

```bash
# Di chuyển vào folder local_dev
cd local_dev

# Start pgAdmin với profile tools
docker-compose --profile tools up -d pgadmin

# Mở browser và truy cập:
# http://localhost:5050

# Login:
# Email: admin@culi.local
# Password: admin

# Add server trong pgAdmin:
# Host: postgres (tên service trong docker-compose)
# Port: 5432
# Database: culi_db
# Username: postgres
# Password: postgres
```

### Database Migrations

**Tạo migration mới:**

```bash
# Đảm bảo đã activate venv
source venv/bin/activate

# Tạo migration từ thay đổi models
alembic revision --autogenerate -m "describe your changes"

# Migration file sẽ được tạo trong migrations/versions/
# Kiểm tra và chỉnh sửa nếu cần
```

**Xem migration files:**

```bash
ls -la migrations/versions/
```

**Apply migrations:**

```bash
# Apply tất cả pending migrations
alembic upgrade head

# Apply migration cụ thể
alembic upgrade <revision_id>

# Xem migration history
alembic history
```

**Rollback migration:**

```bash
# Rollback 1 bước
alembic downgrade -1

# Rollback về revision cụ thể
alembic downgrade <revision_id>

# Rollback tất cả
alembic downgrade base
```

**Reset Database (XÓA TẤT CẢ DATA):**

```bash
# Bước 1: Stop và xóa PostgreSQL container + volumes
cd local_dev
docker-compose down -v postgres

# Bước 2: Start lại PostgreSQL
docker-compose up -d postgres

# Bước 3: Đợi PostgreSQL sẵn sàng (khoảng 3-5 giây)
sleep 5

# Bước 4: Kiểm tra connection
docker-compose exec postgres pg_isready -U postgres

# Bước 5: Chạy lại migrations
cd ..
alembic upgrade head
```

## Testing

### Run Tests

```bash
# Đảm bảo đã activate venv
source venv/bin/activate

# Chạy tất cả tests
pytest

# Chạy test với verbose output
pytest -v

# Chạy test file cụ thể
pytest tests/test_api/test_auth.py

# Chạy test function cụ thể
pytest tests/test_api/test_auth.py::test_register

# Chạy test với coverage
pytest --cov=app --cov-report=html

# Xem coverage report
# Mở file: htmlcov/index.html trong browser
```

### Test Database (Separate from Dev)

Nếu cần test database riêng:

```bash
# Tạo test database trong PostgreSQL
docker-compose -f local_dev/docker-compose.yml exec postgres psql -U postgres -c "CREATE DATABASE culi_test_db;"

# Update .env với test database URL
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/culi_test_db

# Chạy migrations trên test DB
alembic upgrade head
```

## Code Quality

### Format Code

```bash
# Đảm bảo đã activate venv
source venv/bin/activate

# Format code với black
black app/ tests/

# Check format mà không thay đổi
black --check app/ tests/
```

### Lint Code

```bash
# Lint với ruff
ruff check app/ tests/

# Auto-fix các lỗi có thể fix được
ruff check --fix app/ tests/
```

### Type Checking

```bash
# Type check với mypy
mypy app/

# Nếu có errors, fix từng file
```

## Troubleshooting

### PostgreSQL không kết nối được

**1. Kiểm tra container đang chạy:**

```bash
cd local_dev
docker-compose ps
```

**Nếu container không chạy:**

```bash
# Start lại
docker-compose up -d postgres

# Xem logs
docker-compose logs postgres
```

**2. Kiểm tra port 5432:**

```bash
# Linux/Mac
lsof -i :5432

# Nếu có process khác đang dùng port
# Kill process hoặc đổi port trong docker-compose.yml
```

**3. Test connection:**

```bash
# Test từ Docker
docker-compose exec postgres pg_isready -U postgres

# Test từ local
psql postgresql://postgres:postgres@localhost:5432/culi_db -c "SELECT 1;"
```

### Port 8000 đã được sử dụng

**1. Tìm process đang dùng port:**

```bash
# Linux/Mac
lsof -i :8000

# Kill process
kill -9 <PID>
```

**2. Hoặc đổi port:**

```bash
uvicorn app.main:app --reload --port 8001
```

### Migration errors

**1. Xem migration history:**

```bash
alembic history
```

**2. Check current revision:**

```bash
# Trong database
docker-compose -f local_dev/docker-compose.yml exec postgres psql -U postgres -d culi_db -c "SELECT * FROM alembic_version;"
```

**3. Reset và chạy lại:**

```bash
# Xóa tất cả migrations và reset database
cd local_dev
docker-compose down -v postgres
docker-compose up -d postgres
sleep 5
cd ..
alembic upgrade head
```

### Import errors / Module not found

**1. Kiểm tra venv đã activate:**

```bash
which python  # Should show venv path
# hoặc
where python  # Windows
```

**2. Reinstall dependencies:**

```bash
# Deactivate venv trước
deactivate

# Xóa venv cũ (nếu cần)
rm -rf venv  # Linux/Mac
# hoặc: rmdir /s venv  # Windows

# Tạo lại venv
python3 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac

# Install lại
pip install --upgrade pip
pip install -r requirements.txt
```

### Environment variables không được load

**1. Kiểm tra file .env tồn tại:**

```bash
ls -la .env
```

**2. Kiểm tra format .env:**

```bash
# Không có spaces quanh dấu =
# Đúng: KEY=value
# Sai:  KEY = value

# Không có quotes (trừ khi value có spaces)
# Đúng: KEY=value
# Sai:  KEY="value"
```

**3. Reload environment:**

```bash
# Stop server (Ctrl+C)
# Start lại server
uvicorn app.main:app --reload
```

### Virtual environment issues

**1. Venv không activate:**

```bash
# Kiểm tra file activate tồn tại
ls -la venv/bin/activate  # Linux/Mac
# hoặc
dir venv\Scripts\activate  # Windows

# Nếu không có, tạo lại venv
python3 -m venv venv
```

**2. Python version không đúng:**

```bash
# Kiểm tra version
python3 --version  # Should be 3.10+

# Nếu không đúng, cài Python 3.10+ trước
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

1. **Giữ dependencies chạy suốt ngày** - Chỉ stop khi không dùng nữa để tránh phải setup lại

2. **Dùng terminal riêng cho server** - Dễ theo dõi logs, không bị lẫn với commands khác

3. **Auto-reload enabled** - Server tự động reload khi code thay đổi, không cần restart thủ công

4. **IDE Integration** - Setup Python interpreter trong IDE trỏ đến `venv/bin/python` để có autocomplete và debugging

5. **Debugging** - Sử dụng IDE debugger (VS Code, PyCharm) để debug local Python process

6. **Environment Variables** - Không commit file `.env`, giữ các secrets local

7. **Migrations** - Luôn review migration files trước khi apply, đặc biệt là auto-generated

## Next Steps

- Explore API docs tại http://localhost:8000/docs khi server đang chạy
- Đọc [Architecture Documentation](../docs/ARCHITECTURE.md) để hiểu thiết kế hệ thống
- Xem [Main README](../README.md) để tổng quan về project

## Getting Help

Nếu gặp vấn đề:
1. Kiểm tra phần Troubleshooting ở trên
2. Xem logs: `docker-compose logs` hoặc server logs trong terminal
3. Kiểm tra file `.env` và database connection
4. Đảm bảo đã follow đúng các bước setup
