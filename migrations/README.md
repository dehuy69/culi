# Chính sách Database Migrations

**Ngôn ngữ**: [English](README_en.md) | [Tiếng Việt](README.md)

## ⚠️ Loại trừ Migrations

**Các file migration database KHÔNG được bao gồm trong repository open source này.**

Repository này là open source, và migrations sẽ được quản lý riêng trong các deployment production để cho phép linh hoạt cho các chiến lược deployment khác nhau.

## Chiến lược Migration

### Đối với Open Source Repository

- ✅ **SQLAlchemy models** được bao gồm (`app/models/`)
- ✅ **Alembic configuration** được bao gồm (`alembic.ini`, `migrations/env.py`)
- ❌ **Migration files** bị loại trừ (`migrations/versions/*.py`)
- ✅ **Migration directory structure** được giữ lại (với `.gitkeep`)

### Đối với Production Deployments

Khi deploy lên production, bạn nên:

1. **Generate migrations** từ SQLAlchemy models:
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   ```

2. **Review và customize** migration files theo nhu cầu deployment của bạn

3. **Apply migrations** trong deployment pipeline:
   ```bash
   alembic upgrade head
   ```

4. **Quản lý migrations** trong repository production hoặc hệ thống CI/CD

### Đối với Local Development

Cho local development, generate migrations khi cần:

```bash
# Activate virtual environment
conda activate venv_culi  # hoặc source venv/bin/activate

# Generate migration từ models
alembic revision --autogenerate -m "Mô tả thay đổi"

# Review file migration đã generate
# Chỉnh sửa migrations/versions/XXXX_description.py nếu cần

# Apply migration
alembic upgrade head
```

**Quan trọng:** Các file migration được tạo local sẽ bị git ignore (xem `.gitignore`).

## Cấu trúc Thư mục

```
migrations/
├── README.md          # File này - giải thích chính sách migration
├── env.py             # Cấu hình môi trường Alembic
├── script.py.mako     # Template script migration
└── versions/          # Migration files (bị loại trừ khỏi git)
    └── .gitkeep       # Giữ cấu trúc thư mục
```

## Các Lệnh Migration

### Generate Migration
```bash
alembic revision --autogenerate -m "Mô tả migration của bạn"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback Migration
```bash
alembic downgrade -1  # Rollback một phiên bản
```

### Kiểm tra Phiên bản Hiện tại
```bash
alembic current
```

### Xem Lịch sử Migration
```bash
alembic history
```

## Cấu hình .gitignore

Migration files bị loại trừ qua `.gitignore`:

```
migrations/versions/*.py
migrations/versions/*.pyc
!migrations/versions/.gitkeep
```

Điều này đảm bảo:
- Migration files không được commit vào repository
- Cấu trúc thư mục được giữ lại
- Mỗi deployment có thể quản lý migrations độc lập

## Khuyến nghị Production Deployment

1. **Version Control:** Lưu migrations trong repository riêng hoặc private branch
2. **CI/CD Integration:** Chạy migrations tự động trong deployment pipeline
3. **Backup Strategy:** Luôn backup database trước khi chạy migrations
4. **Testing:** Test migrations trên môi trường staging trước
5. **Rollback Plan:** Chuẩn bị rollback scripts cho các vấn đề production

## Tại sao Cách tiếp cận này?

- **Linh hoạt:** Các deployment khác nhau có thể cần chiến lược migration khác nhau
- **Riêng tư:** Migration files có thể chứa các cấu trúc dữ liệu nhạy cảm
- **Version Control:** Cho phép mỗi deployment theo dõi migrations độc lập
- **Open Source:** Giữ repository sạch sẽ và tập trung vào application code

