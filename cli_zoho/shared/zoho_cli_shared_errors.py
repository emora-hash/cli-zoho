"""Structured Zoho API error hierarchy + friendly message mapping."""


# ─── Error Classes ────────────────────────────────────────────────────────────


class ZohoAPIError(Exception):
    """Base class for all Zoho API errors."""

    def __init__(self, message: str, status_code: int = 0, code: str = ""):
        self.status_code = status_code
        self.code = code
        super().__init__(message)


class AuthenticationError(ZohoAPIError):
    """401 — invalid or expired token."""
    pass


class RateLimitError(ZohoAPIError):
    """429 — too many requests."""

    def __init__(self, message: str, retry_after: float = 60.0, **kwargs):
        self.retry_after = retry_after
        super().__init__(message, status_code=429, **kwargs)


class ValidationError(ZohoAPIError):
    """400 — bad request / missing params."""
    pass


class ResourceNotFoundError(ZohoAPIError):
    """404 — record or endpoint not found."""
    pass


class ServerError(ZohoAPIError):
    """500+ — Zoho server error."""
    pass


def raise_for_zoho(resp) -> None:
    """Parse a Zoho error response and raise the appropriate typed exception."""
    if resp.status_code < 400:
        return

    try:
        body = resp.json()
    except Exception:
        body = {}

    message = body.get("message", body.get("error_description", "Unknown error"))
    code = body.get("code", body.get("error", ""))

    match resp.status_code:
        case 401:
            raise AuthenticationError(message, status_code=401, code=code)
        case 429:
            retry_after = float(resp.headers.get("Retry-After", 60))
            raise RateLimitError(message, retry_after=retry_after, code=code)
        case 400:
            raise ValidationError(message, status_code=400, code=code)
        case 404:
            raise ResourceNotFoundError(message, status_code=404, code=code)
        case s if s >= 500:
            raise ServerError(message, status_code=s, code=code)
        case _:
            raise ZohoAPIError(message, status_code=resp.status_code, code=code)


# ─── Friendly Message Map ────────────────────────────────────────────────────


ZOHO_ERROR_MAP = {
    "INVALID_TOKEN": "OAuth token is invalid or expired. Run: cli-zoho auth refresh",
    "INVALID_DATA": "Request data failed validation. Check field names and types.",
    "MANDATORY_NOT_FOUND": "Required field is missing from the request data.",
    "DUPLICATE_DATA": "A record with this data already exists.",
    "RECORD_NOT_FOUND": "No record found with the given ID.",
    "MODULE_NOT_FOUND": "Invalid module name. Run: cli-zoho crm modules",
    "NO_PERMISSION": "Insufficient permissions for this operation.",
    "LIMIT_EXCEEDED": "API rate limit exceeded. Wait and retry.",
    "INTERNAL_ERROR": "Zoho internal error. Retry after a moment.",
}


def friendly_error(resp_json: dict) -> str:
    """Extract a user-friendly error from a Zoho error response."""
    if isinstance(resp_json, dict):
        code = resp_json.get("code", "")
        if code in ZOHO_ERROR_MAP:
            return ZOHO_ERROR_MAP[code]
        message = resp_json.get("message", "")
        if message:
            return message
        data = resp_json.get("data", [])
        if isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, dict):
                return first.get("message", str(resp_json))
    return str(resp_json)
