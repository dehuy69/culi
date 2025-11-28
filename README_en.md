# Culi Backend

AI accounting assistant for Vietnamese small businesses, connecting with sales management and accounting applications.

![Culi Web Interface](docs/web-interface-screenshot.png)

**Language**: [English](README_en.md) | [Tiếng Việt](README.md)

## 📖 Overview

Culi Backend is an AI agent that assists with accounting for small businesses in Vietnam. The system connects with external applications (such as KiotViet, Misa eShop, etc.) to read data, generate reports, and perform automated operations.

### Key Features

- 🤖 **AI Assistant**: Answers questions about accounting, taxes, and sales management
- 🔌 **App Connections**: Supports connections with sales management and accounting applications
- 📊 **Data Reading**: Retrieves product lists, invoices, reports from connected applications
- 🎯 **Planning & Execution**: Creates and executes complex plans to operate on applications
- 🌐 **Web Search**: Searches for information about taxes and regulations

## 🚀 Quick Start

### Requirements

- Python 3.10+
- Docker & Docker Compose
- Git

### Quick Installation

1. **Clone repository:**
   ```bash
   git clone <repository-url>
   cd culi
   ```

2. **Setup environment:**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or: venv\Scripts\activate  # Windows

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Start dependencies:**
   ```bash
   cd local_dev
   docker compose up -d postgres
   cd ..
   ```

5. **Setup database:**
   ```bash
   # Create initial migration
   alembic revision --autogenerate -m "Initial migration"
   
   # Apply migration
   alembic upgrade head
   ```

6. **Start server:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

Server will run at: http://localhost:8000  
API Documentation: http://localhost:8000/docs

### 📚 Detailed Guides

- **[Local Development Setup](local_dev/README_en.md)** - Step-by-step setup and development guide
- **[Architecture Documentation](docs/ARCHITECTURE_en.md)** - System design, LangGraph, adapter pattern
- **[Database Migrations](migrations/README_en.md)** - Database migration management

## 🏗️ Architecture

### Tech Stack

- **FastAPI** - Web framework
- **SQLAlchemy + Alembic** - ORM and database migrations
- **PostgreSQL** - Database
- **LangChain + LangGraph** - AI agent orchestration
- **OpenRouter** - LLM provider (GPT-4, Llama, etc.)
- **Google Custom Search API** - Web search

### Overall Architecture

```
┌─────────────────┐
│   FastAPI App   │
└────────┬────────┘
         │
         ├─── API Routes (REST)
         ├─── Services (Business Logic)
         └─── LangGraph (AI Agent)
                  │
                  ├─── Intent Router
                  ├─── Context Loading
                  ├─── App Adapters (KiotViet, ...)
                  ├─── Web Search
                  └─── Answer Generation
```

### LangGraph Workflow

The system uses LangGraph to manage the workflow for processing user questions:

```
User Input
    ↓
Intent Router (classify intent)
    ↓
┌─────────────────────────────────────┐
│ general_qa → Context → Answer       │
│ tax_qa → Web Search → Answer        │
│ app_read → App Read → Answer        │
│ app_plan → Plan → Execute → Answer  │
└─────────────────────────────────────┘
```

See details at: **[docs/ARCHITECTURE_en.md](docs/ARCHITECTURE_en.md)**

### Adapter Pattern

The system uses the adapter pattern to support multiple types of applications:

- **Supported Apps** (API): KiotViet, Misa eShop, etc. - have their own source code
- **Custom Apps** (MCP): Model Context Protocol servers - generic integration
- **App Categories**: POS_SIMPLE, ACCOUNTING, UNKNOWN

See details at: **[docs/ARCHITECTURE_en.md](docs/ARCHITECTURE_en.md#adapter-pattern)**

## 📁 Project Structure

```
culi/
├── app/                      # Application code
│   ├── api/                  # API routes
│   │   └── v1/               # API version 1
│   ├── core/                 # Core configuration
│   ├── db/                   # Database setup
│   ├── domain/               # Domain logic
│   │   └── apps/             # App adapters
│   │       ├── base.py       # Base adapter interface
│   │       ├── registry.py   # Adapter registry
│   │       └── kiotviet/     # KiotViet adapter
│   ├── graph/                # LangGraph definitions
│   │   ├── state.py          # State definition
│   │   ├── nodes/            # Graph nodes
│   │   └── app_graph.py      # Graph builder
│   ├── models/               # Database models
│   ├── repositories/         # Data access layer
│   ├── services/             # Business logic
│   └── utils/                # Utilities
├── docs/                     # Documentation
│   ├── ARCHITECTURE.md       # Architecture documentation (Vietnamese)
│   ├── ARCHITECTURE_en.md    # Architecture documentation (English)
│   ├── langgraph_chart.mmd   # LangGraph visualization
│   └── web-interface-screenshot.png  # Web interface screenshot
├── local_dev/                # Local development
│   ├── docker-compose.yml    # Docker services
│   ├── README.md             # Local setup guide (Vietnamese)
│   └── README_en.md          # Local setup guide (English)
├── migrations/               # Database migrations
│   ├── README.md             # Migration policy (Vietnamese)
│   └── README_en.md          # Migration policy (English)
├── scripts/                  # Utility scripts
├── tests/                    # Tests
├── requirements.txt          # Python dependencies
├── README.md                 # This file (Vietnamese)
└── README_en.md              # This file (English)
```

## 🔧 Development

### Local Development Workflow

The system uses a **hybrid approach**:
- **Dependencies** (PostgreSQL, Redis) run in Docker
- **Application code** runs directly on local machine (hot reload)

See detailed guide: **[local_dev/README_en.md](local_dev/README_en.md)**

### Common Commands

```bash
# Start dependencies
cd local_dev && docker compose up -d postgres

# Start development server
uvicorn app.main:app --reload --port 8000

# Run tests
pytest

# Format code
black app/ tests/

# Lint code
ruff check app/ tests/
```

## 📝 Database Migrations

Migrations are **NOT included** in the open source repository. Each deployment manages migrations independently.

See details: **[migrations/README_en.md](migrations/README_en.md)**

## 🔐 Environment Variables

Important environment variables:

- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT secret key (minimum 32 characters)
- `OPENROUTER_API_KEY` - OpenRouter API key (required)
- `ENCRYPTION_KEY` - Fernet key to encrypt sensitive data (generate with `scripts/generate_encryption_key.py`)
- `GOOGLE_SEARCH_API_KEY` - Google Custom Search API key (optional)
- `GOOGLE_SEARCH_CX` - Google Custom Search Engine ID (optional)

See `.env.example` file for all environment variables.

## 🤝 Contributing

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Create Pull Request

## 📄 License

[Your License Here]

## 🔗 Links

- **API Documentation**: http://localhost:8000/docs (when server is running)
- **Architecture Docs**: [docs/ARCHITECTURE_en.md](docs/ARCHITECTURE_en.md)
- **Local Setup Guide**: [local_dev/README_en.md](local_dev/README_en.md)
- **Migration Policy**: [migrations/README_en.md](migrations/README_en.md)

## 🆘 Troubleshooting

If you encounter issues, see the Troubleshooting section in:
- **[local_dev/README_en.md](local_dev/README_en.md#troubleshooting)** - Common issues when setting up locally

---

**Made with ❤️ for Vietnamese small businesses**

