# Database Migrations

## ⚠️ Migration Management

**Migrations are NOT included in this open source repository.**

Database migrations should be managed separately in production deployments.

### For Open Source Contributors

- Database schema is defined in SQLAlchemy models under `app/models/`
- Migrations are excluded from the repository via `.gitignore`

### For Production Deployments

When deploying to production:

1. **Generate migrations** from SQLAlchemy models:
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   ```

2. **Review and customize** migration files as needed

3. **Apply migrations**:
   ```bash
   alembic upgrade head
   ```

4. **Manage migrations** in your production repository/CI pipeline

### Local Development

For local development, you can generate migrations:

```bash
# Activate virtual environment
conda activate venv_culi  # or source venv/bin/activate

# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

**Note:** Migration files generated locally should not be committed to the repository.

### Migration Files Structure

```
migrations/
├── env.py              # Alembic environment configuration
├── script.py.mako      # Migration script template
└── versions/           # Migration files (excluded from git)
    └── .gitkeep        # Keep directory structure
```

