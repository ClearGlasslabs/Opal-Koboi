from __future__ import annotations

import uuid


def new_id() -> str:
    """Return a portable UUID string for database primary keys."""
    return str(uuid.uuid4())
