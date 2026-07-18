from __future__ import annotations

import secrets
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.database import get_db

DbSession = Annotated[Session, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def require_api_key(
    settings: AppSettings,
    x_control_plane_key: Annotated[str | None, Header()] = None,
) -> None:
    if x_control_plane_key is None or not secrets.compare_digest(
        x_control_plane_key, settings.api_key
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid control-plane credential",
        )


Authorized = Annotated[None, Depends(require_api_key)]
