"""Authentication endpoint — simple token-based login."""

from __future__ import annotations

import hashlib
import hmac
import os
import time

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel

router = APIRouter(tags=["auth"])

# Stored as "salt:hash" in env var
_CREDENTIAL_HASH = os.getenv("DASHBOARD_PASSWORD_HASH", "")
_DASHBOARD_USER = os.getenv("DASHBOARD_USER", "bayit")
_TOKEN_SECRET = os.getenv("TOKEN_SECRET", "bayit-dashboard-dev-secret")


class LoginRequest(BaseModel):
    """Login request body."""

    username: str
    password: str


def _verify_password(password: str) -> bool:
    """Verify password against stored salt:hash."""
    if not _CREDENTIAL_HASH or ":" not in _CREDENTIAL_HASH:
        return False
    salt, stored_hash = _CREDENTIAL_HASH.split(":", 1)
    computed = hashlib.sha256((salt + password).encode()).hexdigest()
    return hmac.compare_digest(computed, stored_hash)


def _create_token(username: str) -> str:
    """Create a signed session token (username:timestamp:signature)."""
    ts = str(int(time.time()))
    payload = f"{username}:{ts}"
    sig = hmac.new(_TOKEN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]
    return f"{payload}:{sig}"


def verify_token(token: str) -> bool:
    """Verify a session token is valid and not expired (24h)."""
    if not token:
        return False
    parts = token.split(":")
    if len(parts) != 3:
        return False
    username, ts_str, sig = parts
    # Check signature
    payload = f"{username}:{ts_str}"
    expected = hmac.new(_TOKEN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()[:32]
    if not hmac.compare_digest(sig, expected):
        return False
    # Check expiry (24 hours)
    try:
        ts = int(ts_str)
        if time.time() - ts > 86400:
            return False
    except ValueError:
        return False
    return True


@router.post("/login")
async def login(body: LoginRequest, response: Response) -> dict:
    """Authenticate and set session cookie."""
    if body.username != _DASHBOARD_USER or not _verify_password(body.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = _create_token(body.username)
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=86400,
    )
    return {"status": "ok"}


@router.get("/auth/check")
async def auth_check(request: Request) -> dict:
    """Check if the current session is valid."""
    token = request.cookies.get("session", "")
    if verify_token(token):
        return {"authenticated": True}
    raise HTTPException(status_code=401, detail="Not authenticated")


@router.post("/logout")
async def logout(response: Response) -> dict:
    """Clear session cookie."""
    response.delete_cookie("session")
    return {"status": "ok"}
