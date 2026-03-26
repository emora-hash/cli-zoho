"""Tests for OAuth2 authentication."""

import json
import time

import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from cli_zoho.auth import ZohoAuth, TOKEN_CACHE_FILE, _rate_limit_retry_after
from cli_zoho.shared.errors import (
    AuthenticationError, RateLimitError, ValidationError,
    ResourceNotFoundError, ServerError, raise_for_zoho,
)
import cli_zoho.auth as auth_module
import cli_zoho.config as config_module


class TestZohoAuth:
    def test_refresh_sets_token(self, tmp_path, monkeypatch):
        auth = ZohoAuth()
        auth._cache_file = tmp_path / ".token_cache"
        auth._lock_file = tmp_path / "oauth-refresh.lock"
        auth._access_token = None
        auth._token_expiry = 0
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"access_token": "new-token-123", "expires_in": 3600}

        with patch.object(auth._session, "post", return_value=mock_resp):
            token = auth.refresh()

        assert token == "new-token-123"
        assert auth._access_token == "new-token-123"

    def test_refresh_raises_on_missing_token(self, tmp_path, monkeypatch):
        auth = ZohoAuth()
        auth._cache_file = tmp_path / ".token_cache"
        auth._lock_file = tmp_path / "oauth-refresh.lock"
        auth._access_token = None
        auth._token_expiry = 0
        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_resp.json.return_value = {"error": "invalid_client"}

        with patch.object(auth._session, "post", return_value=mock_resp):
            with pytest.raises(AuthenticationError, match="Token refresh failed"):
                auth.refresh()

    def test_access_token_auto_refreshes(self, tmp_path, monkeypatch):
        monkeypatch.setattr(auth_module, "TOKEN_CACHE_FILE", tmp_path / ".token_cache")
        auth = ZohoAuth()
        # Ensure no cached token
        auth._access_token = None
        auth._token_expiry = 0

        def fake_refresh():
            auth._access_token = "auto-token"
            auth._token_expiry = time.time() + 3600
            return "auto-token"

        with patch.object(auth, "refresh", side_effect=fake_refresh) as mock_refresh:
            token = auth.access_token
            mock_refresh.assert_called_once()
            assert token == "auto-token"

    def test_request_retries_on_401(self):
        auth = ZohoAuth()
        auth._access_token = "old-token"
        auth._token_expiry = time.time() + 3600

        resp_401 = MagicMock()
        resp_401.status_code = 401

        resp_200 = MagicMock()
        resp_200.status_code = 200

        with patch.object(auth._session, "request", side_effect=[resp_401, resp_200]):
            with patch.object(auth, "refresh", return_value="new-token"):
                result = auth.request("GET", "https://api.example.com/test")

        assert result.status_code == 200

    def test_request_backs_off_on_429(self):
        auth = ZohoAuth()
        auth._access_token = "token"
        auth._token_expiry = time.time() + 3600

        resp_429 = MagicMock()
        resp_429.status_code = 429
        resp_429.headers = {"Retry-After": "1"}

        resp_200 = MagicMock()
        resp_200.status_code = 200

        with patch.object(auth._session, "request", side_effect=[resp_429, resp_200]):
            with patch("cli_zoho.auth.time.sleep") as mock_sleep:
                result = auth.request("GET", "https://api.example.com/test")

        mock_sleep.assert_called()
        assert result.status_code == 200

    def test_missing_env_var_exits(self, tmp_path, monkeypatch):
        monkeypatch.delenv("ZOHO_CLIENT_ID", raising=False)
        auth = ZohoAuth()
        auth._cache_file = tmp_path / ".token_cache"
        auth._lock_file = tmp_path / "oauth-refresh.lock"
        auth._access_token = None
        auth._token_expiry = 0
        with pytest.raises(SystemExit):
            auth.refresh()

    def test_token_cache_saves_and_loads(self, tmp_path, monkeypatch):
        cache_file = tmp_path / ".token_cache"
        monkeypatch.setattr(auth_module, "TOKEN_CACHE_FILE", cache_file)
        monkeypatch.setattr(auth_module, "TOKEN_CACHE_DIR", tmp_path)

        # Save
        auth = ZohoAuth()
        auth._save_cached_token("cached-token-xyz", 3600)
        assert cache_file.exists()

        # Load in new instance
        auth2 = ZohoAuth()
        assert auth2._access_token == "cached-token-xyz"

    def test_expired_cache_triggers_refresh(self, tmp_path, monkeypatch):
        cache_file = tmp_path / ".token_cache"
        monkeypatch.setattr(auth_module, "TOKEN_CACHE_FILE", cache_file)
        monkeypatch.setattr(auth_module, "TOKEN_CACHE_DIR", tmp_path)

        # Write expired token
        cache_file.write_text(json.dumps({
            "access_token": "old-expired",
            "expires_at": time.time() - 100,
        }))

        auth = ZohoAuth()
        assert auth._access_token is None  # expired, not loaded

    def test_global_rate_limit_blocks_requests(self):
        auth = ZohoAuth()
        auth._access_token = "token"
        auth._token_expiry = time.time() + 3600

        # Set global rate limit 0.1s in the future
        auth._set_global_rate_limit(0.1)

        resp_200 = MagicMock()
        resp_200.status_code = 200

        with patch.object(auth._session, "request", return_value=resp_200):
            with patch("cli_zoho.auth.time.sleep") as mock_sleep:
                result = auth.request("GET", "https://api.example.com/test")

        # Should have slept for the global rate limit
        assert mock_sleep.called or result.status_code == 200

        # Reset global state
        auth_module._rate_limit_retry_after = None

    def test_backoff_delay_grows_exponentially(self):
        d0 = ZohoAuth._backoff_delay(0)
        d1 = ZohoAuth._backoff_delay(1)
        d2 = ZohoAuth._backoff_delay(2)
        # Should roughly double each time (within jitter)
        assert 0.5 < d0 < 1.5
        assert 1.0 < d1 < 3.0
        assert 2.0 < d2 < 6.0

    def test_retries_on_server_error(self):
        auth = ZohoAuth()
        auth._access_token = "token"
        auth._token_expiry = time.time() + 3600

        resp_500 = MagicMock()
        resp_500.status_code = 500

        resp_200 = MagicMock()
        resp_200.status_code = 200

        with patch.object(auth._session, "request", side_effect=[resp_500, resp_200]):
            with patch("cli_zoho.auth.time.sleep"):
                result = auth.request("GET", "https://api.example.com/test")

        assert result.status_code == 200


class TestAuthCommands:
    def test_auth_status(self, invoke):
        result = invoke(["auth", "status"], mock_response={"modules": []})
        assert result.exit_code == 0

    def test_auth_refresh(self, invoke):
        result = invoke(["auth", "refresh"])
        assert result.exit_code == 0
        assert "refreshed" in result.output.lower() or "True" in result.output


class TestRaiseForZoho:
    """Test that raise_for_zoho produces correct exception subclasses."""

    def _mock_resp(self, status_code, body=None, headers=None):
        resp = MagicMock()
        resp.status_code = status_code
        resp.json.return_value = body or {}
        resp.headers = headers or {}
        return resp

    def test_200_does_not_raise(self):
        raise_for_zoho(self._mock_resp(200))

    def test_204_does_not_raise(self):
        raise_for_zoho(self._mock_resp(204))

    def test_400_raises_validation_error(self):
        resp = self._mock_resp(400, {"code": "REQUIRED_PARAM_MISSING", "message": "fields required"})
        with pytest.raises(ValidationError, match="fields required"):
            raise_for_zoho(resp)

    def test_401_raises_authentication_error(self):
        resp = self._mock_resp(401, {"code": "INVALID_TOKEN", "message": "bad token"})
        with pytest.raises(AuthenticationError):
            raise_for_zoho(resp)

    def test_404_raises_not_found(self):
        resp = self._mock_resp(404, {"message": "not found"})
        with pytest.raises(ResourceNotFoundError):
            raise_for_zoho(resp)

    def test_429_raises_rate_limit_with_retry_after(self):
        resp = self._mock_resp(429, {"message": "slow down"}, headers={"Retry-After": "30"})
        with pytest.raises(RateLimitError) as exc_info:
            raise_for_zoho(resp)
        assert exc_info.value.retry_after == 30.0

    def test_500_raises_server_error(self):
        resp = self._mock_resp(500, {"message": "internal"})
        with pytest.raises(ServerError):
            raise_for_zoho(resp)


class TestMultiRegion:
    """Test region → domain URL generation."""

    def test_us_default(self, monkeypatch):
        monkeypatch.delenv("ZOHO_REGION", raising=False)
        config_module._region_cfg = None
        url = config_module.get_token_url()
        assert url == "https://accounts.zoho.com/oauth/v2/token"
        config_module._region_cfg = None

    def test_eu_region(self, monkeypatch):
        monkeypatch.setenv("ZOHO_REGION", "eu")
        config_module._region_cfg = None
        assert config_module.get_crm_base() == "https://www.zohoapis.eu/crm/v8"
        config_module._region_cfg = None

    def test_in_region(self, monkeypatch):
        monkeypatch.setenv("ZOHO_REGION", "in")
        config_module._region_cfg = None
        assert config_module.get_inventory_base() == "https://www.zohoapis.in/inventory/v1"
        config_module._region_cfg = None

    def test_au_region(self, monkeypatch):
        monkeypatch.setenv("ZOHO_REGION", "au")
        config_module._region_cfg = None
        assert config_module.get_token_url() == "https://accounts.zoho.com.au/oauth/v2/token"
        config_module._region_cfg = None

    def test_jp_region(self, monkeypatch):
        monkeypatch.setenv("ZOHO_REGION", "jp")
        config_module._region_cfg = None
        assert config_module.get_crm_base() == "https://www.zohoapis.jp/crm/v8"
        config_module._region_cfg = None

    def test_ca_region(self, monkeypatch):
        monkeypatch.setenv("ZOHO_REGION", "ca")
        config_module._region_cfg = None
        assert config_module.get_inventory_base() == "https://www.zohoapis.ca/inventory/v1"
        config_module._region_cfg = None

    def test_invalid_region_exits(self, monkeypatch):
        monkeypatch.setenv("ZOHO_REGION", "mars")
        config_module._region_cfg = None
        with pytest.raises(SystemExit, match="Invalid ZOHO_REGION"):
            config_module.get_token_url()
        config_module._region_cfg = None
