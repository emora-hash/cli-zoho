"""Shared OAuth2 authentication for Zoho CRM and Inventory.

Features (inspired by kkeeling/zoho-mcp):
- Disk-based token cache at ~/.cli-zoho/.token_cache
- Global rate limit state — all requests wait after a 429
- Exponential backoff with ±25% jitter, 3 retries max
- 401 auto-refresh with single retry
- Structured error hierarchy
"""

import json
import logging
import os
import random
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests

from cli_zoho import config
from cli_zoho.shared.errors import (
    AuthenticationError,
    RateLimitError,
    raise_for_zoho,
)

logger = logging.getLogger(__name__)

# ─── Constants ────────────────────────────────────────────────────────────────

TOKEN_CACHE_DIR = Path.home() / ".cli-zoho"
TOKEN_CACHE_FILE = TOKEN_CACHE_DIR / ".token_cache"
TOKEN_EXPIRY_BUFFER = 60  # seconds before expiry to trigger refresh

MAX_RETRIES = 3
INITIAL_BACKOFF = 1.0
MAX_BACKOFF = 60.0
BACKOFF_MULTIPLIER = 2.0

# ─── Global Rate Limit State ─────────────────────────────────────────────────
# When a 429 hits, ALL subsequent requests wait until this time passes.

_rate_limit_retry_after: datetime | None = None


class ZohoAuth:
    """Manages OAuth2 access tokens via refresh token grant."""

    def __init__(self):
        self._access_token: str | None = None
        self._token_expiry: float = 0
        self._session = requests.Session()
        self._load_cached_token()

    # ─── Token Cache ──────────────────────────────────────────────────────

    def _load_cached_token(self) -> None:
        """Load token from disk cache if still valid."""
        if not TOKEN_CACHE_FILE.exists():
            return
        try:
            data = json.loads(TOKEN_CACHE_FILE.read_text())
            expires_at = data.get("expires_at", 0)
            if time.time() < expires_at - TOKEN_EXPIRY_BUFFER:
                self._access_token = data["access_token"]
                self._token_expiry = expires_at
                logger.debug("Loaded cached token (expires %s)", datetime.fromtimestamp(expires_at))
        except (json.JSONDecodeError, KeyError, OSError):
            pass  # corrupt cache — will refresh

    def _save_cached_token(self, access_token: str, expires_in: int) -> None:
        """Persist token to disk."""
        TOKEN_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        expires_at = time.time() + expires_in
        TOKEN_CACHE_FILE.write_text(json.dumps({
            "access_token": access_token,
            "expires_at": expires_at,
        }))
        os.chmod(TOKEN_CACHE_FILE, 0o600)  # owner-only read/write
        self._token_expiry = expires_at

    # ─── Token Refresh ────────────────────────────────────────────────────

    def refresh(self) -> str:
        """Force a token refresh and return the new access token."""
        resp = self._session.post(
            config.get_token_url(),
            data={
                "refresh_token": config.get_refresh_token(),
                "client_id": config.get_client_id(),
                "client_secret": config.get_client_secret(),
                "grant_type": "refresh_token",
            },
        )
        data = resp.json()
        if resp.status_code != 200 or "access_token" not in data:
            error = data.get("error", "unknown")
            desc = data.get("error_description", data.get("message", ""))
            raise AuthenticationError(f"Token refresh failed: {error} — {desc}", status_code=resp.status_code, code=error)

        self._access_token = data["access_token"]
        expires_in = data.get("expires_in", 3600)
        self._save_cached_token(self._access_token, expires_in)
        logger.info("Zoho access token refreshed (expires in %ds)", expires_in)
        return self._access_token

    @property
    def access_token(self) -> str:
        if self._access_token is None or time.time() >= self._token_expiry - TOKEN_EXPIRY_BUFFER:
            self.refresh()
        return self._access_token

    # ─── Rate Limit Handling ──────────────────────────────────────────────

    @staticmethod
    def _check_global_rate_limit() -> None:
        """If a 429 was recently received, sleep until the cooldown expires."""
        global _rate_limit_retry_after
        if _rate_limit_retry_after is None:
            return
        now = datetime.now()
        if now < _rate_limit_retry_after:
            wait = (_rate_limit_retry_after - now).total_seconds()
            logger.warning("Global rate limit active, sleeping %.1fs", wait)
            time.sleep(wait)
        _rate_limit_retry_after = None

    @staticmethod
    def _set_global_rate_limit(seconds: float) -> None:
        """Set the global cooldown after receiving a 429."""
        global _rate_limit_retry_after
        _rate_limit_retry_after = datetime.now() + timedelta(seconds=seconds)

    @staticmethod
    def _backoff_delay(attempt: int) -> float:
        """Exponential backoff with ±25% jitter."""
        base = min(INITIAL_BACKOFF * (BACKOFF_MULTIPLIER ** attempt), MAX_BACKOFF)
        jitter = base * 0.25 * (2 * random.random() - 1)
        return base + jitter

    # ─── HTTP Request ─────────────────────────────────────────────────────

    def request(
        self,
        method: str,
        url: str,
        headers: dict | None = None,
        **kwargs,
    ) -> requests.Response:
        """Make an authenticated request with auto-refresh, rate limit handling,
        and exponential backoff with jitter."""
        self._check_global_rate_limit()

        merged = {**(headers or {}), "Authorization": f"Zoho-oauthtoken {self.access_token}"}

        for attempt in range(MAX_RETRIES + 1):
            resp = self._session.request(method, url, headers=merged, **kwargs)

            # 401 — refresh token and retry once
            if resp.status_code == 401 and attempt == 0:
                logger.warning("Got 401, refreshing token")
                self.refresh()
                merged["Authorization"] = f"Zoho-oauthtoken {self.access_token}"
                continue

            # 429 — exponential backoff with global cooldown
            if resp.status_code == 429 and attempt < MAX_RETRIES:
                delay = self._backoff_delay(attempt)
                retry_after = resp.headers.get("Retry-After")
                if retry_after:
                    try:
                        delay = float(retry_after)
                    except ValueError:
                        pass
                self._set_global_rate_limit(delay)
                logger.warning("Rate limited (429), attempt %d/%d, sleeping %.1fs", attempt + 1, MAX_RETRIES, delay)
                time.sleep(delay)
                continue

            # 5xx — retry with backoff
            if resp.status_code >= 500 and attempt < MAX_RETRIES:
                delay = self._backoff_delay(attempt)
                logger.warning("Server error %d, attempt %d/%d, sleeping %.1fs", resp.status_code, attempt + 1, MAX_RETRIES, delay)
                time.sleep(delay)
                continue

            # Success or non-retryable error — raise typed exception on 4xx
            raise_for_zoho(resp)
            return resp

        # Exhausted retries — raise typed exception
        raise_for_zoho(resp)
        return resp

    # ─── Status Check ─────────────────────────────────────────────────────

    def status(self) -> dict:
        """Check auth status by hitting a lightweight CRM endpoint."""
        try:
            resp = self.request("GET", f"{config.get_crm_base()}/settings/modules", params={"per_page": 1})
            return {
                "authenticated": resp.status_code == 200,
                "status_code": resp.status_code,
                "has_token": self._access_token is not None,
            }
        except Exception as e:
            return {
                "authenticated": False,
                "status_code": getattr(e, "status_code", 0),
                "has_token": self._access_token is not None,
                "error": str(e),
            }
