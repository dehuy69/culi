"""Time utility functions."""
from datetime import datetime, timezone, timedelta

# Vietnam timezone
VIETNAM_TZ = timezone(timedelta(hours=7))


def now_vietnam() -> datetime:
    """Get current time in Vietnam timezone."""
    return datetime.now(VIETNAM_TZ)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string."""
    return dt.strftime(format_str)

