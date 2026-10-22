import re
from datetime import datetime, timezone

EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$')


def utcnow():
    """UTC atual como datetime naive (as colunas do banco são naive)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def calculate_percentage(part, total):
    if total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    return isinstance(email, str) and bool(EMAIL_PATTERN.match(email))
