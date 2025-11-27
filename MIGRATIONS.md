# Database Migrations Policy

## ⚠️ Migrations Exclusion

**Database migration files are NOT included in this open source repository.**

This repository is open source, and migrations should be managed separately in production deployments to allow flexibility for different deployment strategies.

## Migration Strategy

### For Open Source Repository

- ✅ **SQLAlchemy models** are included (`app/models/`)
- ✅ **Alembic configuration** is included (`alembic.ini`, `migrations/env.py`)
- ❌ **Migration files** are excluded (`migrations/versions/*.py`)
- ✅ **Migration directory structure** is kept (with `.gitkeep`)

### For Production Deployments

When deploying to production, you should:

1. **Generate migrations** from SQLAlchemy models:
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   ```

2. **Review and customize** migration files as needed for your deployment

3. **Apply migrations** in your deployment pipeline:
   ```bash
   alembic upgrade head
   ```

4. **Manage migrations** in your production repository or CI/CD system

### For Local Development

For local development, generate migrations as needed:

```bash
# Activate virtual environment
conda activate venv_culi  # or source venv/bin/activate

# Generate migration from models
alembic revision --autogenerate -m "Description of changes"

# Review the generated migration file
# Edit migrations/versions/XXXX_description.py if needed

# Apply migration
alembic upgrade head
```

**Important:** Migration files generated locally are ignored by git (see `.gitignore`).

## Directory Structure

```
migrations/
├── README.md          # This file - migration policy explanation
├── env.py             # Alembic environment configuration
├── script.py.mako     # Migration script template
└── versions/          # Migration files (excluded from git)
    └── .gitkeep       # Keep directory structure
```

## Migration Commands

### Generate Migration
```bash
alembic revision --autogenerate -m "Your migration description"
```

### Apply Migrations
```bash
alembic upgrade head
```

### Rollback Migration
```bash
alembic downgrade -1  # Rollback one version
```

### Check Current Version
```bash
alembic current
```

### View Migration History
```bash
alembic history
```

## .gitignore Configuration

Migration files are excluded via `.gitignore`:

```
migrations/versions/*.py
migrations/versions/*.pyc
!migrations/versions/.gitkeep
```

This ensures that:
- Migration files are not committed to the repository
- Directory structure is preserved
- Each deployment can manage migrations independently

## Production Deployment Recommendations

1. **Version Control:** Store migrations in a separate repository or private branch
2. **CI/CD Integration:** Run migrations automatically in your deployment pipeline
3. **Backup Strategy:** Always backup database before running migrations
4. **Testing:** Test migrations on staging environment first
5. **Rollback Plan:** Keep rollback scripts ready for production issues

## Why This Approach?

- **Flexibility:** Different deployments may need different migration strategies
- **Privacy:** Migration files might contain sensitive data structures
- **Version Control:** Allows each deployment to track migrations independently
- **Open Source:** Keeps repository clean and focused on application code

