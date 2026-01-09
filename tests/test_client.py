"""
Tests for Scrappey client.

These tests verify the client initialization and basic functionality
without making actual API calls (mocked).
"""

import pytest

from scrappey import (
    AsyncScrappey,
    Scrappey,
    ScrappeyAuthenticationError,
    ScrappeyError,
)


class TestScrappeyInit:
    """Test Scrappey client initialization."""

    def test_init_with_api_key(self):
        """Client should initialize with API key."""
        client = Scrappey(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == Scrappey.DEFAULT_BASE_URL
        assert client.timeout == Scrappey.DEFAULT_TIMEOUT
        client.close()

    def test_init_with_custom_base_url(self):
        """Client should accept custom base URL."""
        client = Scrappey(api_key="test_key", base_url="https://custom.api.com")
        assert client.base_url == "https://custom.api.com"
        client.close()

    def test_init_with_custom_timeout(self):
        """Client should accept custom timeout."""
        client = Scrappey(api_key="test_key", timeout=60)
        assert client.timeout == 60
        client.close()

    def test_init_without_api_key_raises(self):
        """Client should raise error without API key."""
        with pytest.raises(ScrappeyAuthenticationError):
            Scrappey(api_key="")

    def test_init_with_none_api_key_raises(self):
        """Client should raise error with None API key."""
        with pytest.raises(ScrappeyAuthenticationError):
            Scrappey(api_key=None)  # type: ignore

    def test_context_manager(self):
        """Client should work as context manager."""
        with Scrappey(api_key="test_key") as client:
            assert client.api_key == "test_key"


class TestAsyncScrappeyInit:
    """Test AsyncScrappey client initialization."""

    def test_init_with_api_key(self):
        """Async client should initialize with API key."""
        client = AsyncScrappey(api_key="test_key")
        assert client.api_key == "test_key"
        assert client.base_url == AsyncScrappey.DEFAULT_BASE_URL

    def test_init_without_api_key_raises(self):
        """Async client should raise error without API key."""
        with pytest.raises(ScrappeyAuthenticationError):
            AsyncScrappey(api_key="")


class TestScrappeyMethods:
    """Test Scrappey client methods (structure only, no API calls)."""

    def test_get_method_exists(self):
        """Get method should exist and be callable."""
        client = Scrappey(api_key="test_key")
        assert callable(client.get)
        client.close()

    def test_post_method_exists(self):
        """Post method should exist and be callable."""
        client = Scrappey(api_key="test_key")
        assert callable(client.post)
        client.close()

    def test_create_session_method_exists(self):
        """Create session method should exist."""
        client = Scrappey(api_key="test_key")
        assert callable(client.create_session)
        client.close()

    def test_destroy_session_method_exists(self):
        """Destroy session method should exist."""
        client = Scrappey(api_key="test_key")
        assert callable(client.destroy_session)
        client.close()

    def test_browser_action_method_exists(self):
        """Browser action method should exist."""
        client = Scrappey(api_key="test_key")
        assert callable(client.browser_action)
        client.close()

    def test_screenshot_method_exists(self):
        """Screenshot method should exist."""
        client = Scrappey(api_key="test_key")
        assert callable(client.screenshot)
        client.close()


class TestExceptions:
    """Test exception classes."""

    def test_scrappey_error(self):
        """ScrappeyError should be raiseable."""
        with pytest.raises(ScrappeyError):
            raise ScrappeyError("Test error")

    def test_scrappey_error_with_response(self):
        """ScrappeyError should accept response data."""
        error = ScrappeyError("Test error", response={"data": "error"}, status_code=500)
        assert error.message == "Test error"
        assert error.response == {"data": "error"}
        assert error.status_code == 500

    def test_authentication_error(self):
        """ScrappeyAuthenticationError should be a ScrappeyError."""
        with pytest.raises(ScrappeyError):
            raise ScrappeyAuthenticationError("Invalid key")
