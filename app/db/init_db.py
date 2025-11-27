"""Database initialization and seeding."""
from app.db.session import SessionLocal, init_db
from app.db.base import Base
from app.core.logging import get_logger

logger = get_logger(__name__)


def init_database():
    """Initialize database tables."""
    logger.info("Initializing database tables...")
    init_db()
    logger.info("Database tables initialized successfully.")


if __name__ == "__main__":
    init_database()

