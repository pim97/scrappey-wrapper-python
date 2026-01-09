"""
Tests for Scrappey requests-compatible API.

These tests verify that the requests-compatible API provides the same
interface as the popular `requests` library.
"""

import os
from datetime import timedelta
from unittest.mock import MagicMock, patch

import pytest

from scrappey import requests
from scrappey.requests import (
    ConnectionError,
    HTTPError,
    PreparedRequest,
    RequestException,
    RequestsCookieJar,
    Response,
    Session,
    Timeout,
    _build_url_with_params,
)


# =============================================================================
# Test Response Object
# =============================================================================


class TestResponse:
    """Test Response object compatibility with requests.Response."""

    @pytest.fixture
    def mock_scrappey_response(self):
        """Create a mock Scrappey API response."""
        return {
            "solution": {
                "verified": True,
                "statusCode": 200,
                "response": '{"key": "value", "number": 42}',
                "currentUrl": "https://example.com/page",
                "cookies": [
                    {"name": "session_id", "value": "abc123"},
                    {"name": "token", "value": "xyz789"},
                ],
                "cookieString": "session_id=abc123; token=xyz789",
                "userAgent": "Mozilla/5.0",
                "responseHeaders": {
                    "content-type": "application/json; charset=utf-8",
                    "x-custom-header": "custom-value",
                },
            },
            "timeElapsed": 1500,
            "data": "success",
            "session": "test-session-id",
        }

    @pytest.fixture
    def response(self, mock_scrappey_response):
        """Create a Response object from mock data."""
        return Response(mock_scrappey_response)

    def test_status_code(self, response):
        """Response should have status_code attribute."""
        assert response.status_code == 200

    def test_text(self, response):
        """Response should have text property."""
        assert response.text == '{"key": "value", "number": 42}'

    def test_content(self, response):
        """Response should have content property (bytes)."""
        assert isinstance(response.content, bytes)
        assert response.content == b'{"key": "value", "number": 42}'

    def test_json(self, response):
        """Response should have json() method."""
        data = response.json()
        assert data == {"key": "value", "number": 42}

    def test_json_caching(self, response):
        """JSON parsing should be cached."""
        data1 = response.json()
        data2 = response.json()
        assert data1 is data2

    def test_json_invalid_raises(self):
        """json() should raise ValueError for invalid JSON."""
        response = Response({
            "solution": {
                "statusCode": 200,
                "response": "not valid json",
            },
            "data": "success",
        })
        with pytest.raises(ValueError) as exc_info:
            response.json()
        assert "not valid JSON" in str(exc_info.value)

    def test_headers(self, response):
        """Response should have headers dict."""
        assert "content-type" in response.headers
        assert response.headers["content-type"] == "application/json; charset=utf-8"
        assert response.headers["x-custom-header"] == "custom-value"

    def test_headers_lowercase(self, response):
        """Headers should be lowercase."""
        for key in response.headers:
            assert key == key.lower()

    def test_cookies(self, response):
        """Response should have cookies as RequestsCookieJar."""
        assert isinstance(response.cookies, RequestsCookieJar)
        assert response.cookies.get("session_id") == "abc123"
        assert response.cookies.get("token") == "xyz789"

    def test_url(self, response):
        """Response should have url attribute."""
        assert response.url == "https://example.com/page"

    def test_ok_true(self, response):
        """Response.ok should be True for 2xx status codes."""
        assert response.ok is True

    def test_ok_false(self):
        """Response.ok should be False for 4xx/5xx status codes."""
        response = Response({
            "solution": {"statusCode": 404, "response": ""},
            "data": "success",
        })
        assert response.ok is False

    def test_elapsed(self, response):
        """Response should have elapsed timedelta."""
        assert isinstance(response.elapsed, timedelta)
        assert response.elapsed.total_seconds() == 1.5

    def test_encoding(self, response):
        """Response should detect encoding from headers."""
        assert response.encoding == "utf-8"

    def test_encoding_default(self):
        """Response should default to utf-8 if not specified."""
        response = Response({
            "solution": {
                "statusCode": 200,
                "response": "test",
                "responseHeaders": {},
            },
            "data": "success",
        })
        assert response.encoding == "utf-8"

    def test_reason(self, response):
        """Response should have reason phrase."""
        assert response.reason == "OK"

    def test_reason_404(self):
        """Response should have correct reason for 404."""
        response = Response({
            "solution": {"statusCode": 404, "response": ""},
            "data": "success",
        })
        assert response.reason == "Not Found"

    def test_is_redirect(self):
        """Response.is_redirect should detect redirect status codes."""
        for code in [301, 302, 303, 307, 308]:
            response = Response({
                "solution": {"statusCode": code, "response": ""},
                "data": "success",
            })
            assert response.is_redirect is True

    def test_is_not_redirect(self, response):
        """Response.is_redirect should be False for non-redirect codes."""
        assert response.is_redirect is False

    def test_raise_for_status_ok(self, response):
        """raise_for_status should not raise for 2xx."""
        response.raise_for_status()  # Should not raise

    def test_raise_for_status_error(self):
        """raise_for_status should raise HTTPError for 4xx/5xx."""
        response = Response({
            "solution": {
                "statusCode": 404,
                "response": "",
                "currentUrl": "https://example.com/missing",
            },
            "data": "success",
        })
        with pytest.raises(HTTPError) as exc_info:
            response.raise_for_status()
        assert "404" in str(exc_info.value)
        assert exc_info.value.response is response

    def test_iter_content(self, response):
        """iter_content should yield response content."""
        chunks = list(response.iter_content())
        assert len(chunks) == 1
        assert chunks[0] == response.content

    def test_iter_lines(self, response):
        """iter_lines should yield response lines."""
        lines = list(response.iter_lines())
        assert len(lines) >= 1

    def test_repr(self, response):
        """Response should have readable repr."""
        assert repr(response) == "<Response [200]>"

    def test_bool_true(self, response):
        """Response should be truthy for ok status."""
        assert bool(response) is True

    def test_bool_false(self):
        """Response should be falsy for error status."""
        response = Response({
            "solution": {"statusCode": 500, "response": ""},
            "data": "success",
        })
        assert bool(response) is False

    def test_context_manager(self, response):
        """Response should work as context manager."""
        with response as r:
            assert r.status_code == 200

    def test_request_attribute(self, response):
        """Response should have request attribute."""
        assert isinstance(response.request, PreparedRequest)

    def test_history_empty(self, response):
        """Response.history should be empty list."""
        assert response.history == []


# =============================================================================
# Test RequestsCookieJar
# =============================================================================


class TestRequestsCookieJar:
    """Test RequestsCookieJar compatibility."""

    def test_set_and_get(self):
        """Should be able to set and get cookies."""
        jar = RequestsCookieJar()
        jar.set("name", "value")
        assert jar.get("name") == "value"

    def test_get_default(self):
        """get() should return default for missing cookie."""
        jar = RequestsCookieJar()
        assert jar.get("missing") is None
        assert jar.get("missing", "default") == "default"

    def test_dict_access(self):
        """Should support dict-like access."""
        jar = RequestsCookieJar()
        jar["name"] = "value"
        assert jar["name"] == "value"

    def test_iteration(self):
        """Should be iterable."""
        jar = RequestsCookieJar()
        jar.set("a", "1")
        jar.set("b", "2")
        assert set(jar) == {"a", "b"}

    def test_len(self):
        """Should support len()."""
        jar = RequestsCookieJar()
        assert len(jar) == 0
        jar.set("name", "value")
        assert len(jar) == 1

    def test_contains(self):
        """Should support 'in' operator."""
        jar = RequestsCookieJar()
        jar.set("name", "value")
        assert "name" in jar
        assert "other" not in jar

    def test_update_dict(self):
        """Should update from dict."""
        jar = RequestsCookieJar()
        jar.update({"a": "1", "b": "2"})
        assert jar.get("a") == "1"
        assert jar.get("b") == "2"

    def test_update_jar(self):
        """Should update from another jar."""
        jar1 = RequestsCookieJar()
        jar1.set("a", "1")
        jar2 = RequestsCookieJar()
        jar2.update(jar1)
        assert jar2.get("a") == "1"

    def test_get_dict(self):
        """get_dict() should return dict copy."""
        jar = RequestsCookieJar()
        jar.set("a", "1")
        jar.set("b", "2")
        d = jar.get_dict()
        assert d == {"a": "1", "b": "2"}
        assert isinstance(d, dict)

    def test_items(self):
        """items() should return cookie items."""
        jar = RequestsCookieJar()
        jar.set("a", "1")
        items = list(jar.items())
        assert ("a", "1") in items


# =============================================================================
# Test URL Building
# =============================================================================


class TestBuildUrlWithParams:
    """Test URL parameter building."""

    def test_no_params(self):
        """URL should be unchanged with no params."""
        url = _build_url_with_params("https://example.com", None)
        assert url == "https://example.com"

    def test_dict_params(self):
        """Should append dict params to URL."""
        url = _build_url_with_params("https://example.com", {"key": "value"})
        assert "key=value" in url

    def test_multiple_params(self):
        """Should handle multiple params."""
        url = _build_url_with_params("https://example.com", {"a": "1", "b": "2"})
        assert "a=1" in url
        assert "b=2" in url

    def test_existing_query_string(self):
        """Should merge with existing query string."""
        url = _build_url_with_params("https://example.com?existing=yes", {"new": "param"})
        assert "existing=yes" in url
        assert "new=param" in url

    def test_list_params(self):
        """Should handle list of tuples."""
        url = _build_url_with_params("https://example.com", [("key", "value")])
        assert "key=value" in url


# =============================================================================
# Test PreparedRequest
# =============================================================================


class TestPreparedRequest:
    """Test PreparedRequest compatibility."""

    def test_init(self):
        """Should initialize with all attributes."""
        req = PreparedRequest(
            method="POST",
            url="https://example.com",
            headers={"Content-Type": "application/json"},
            body='{"key": "value"}',
        )
        assert req.method == "POST"
        assert req.url == "https://example.com"
        assert req.headers == {"Content-Type": "application/json"}
        assert req.body == '{"key": "value"}'

    def test_path_url(self):
        """Should parse path_url from URL."""
        req = PreparedRequest(url="https://example.com/path/to/resource?query=1")
        assert req.path_url == "/path/to/resource"

    def test_defaults(self):
        """Should have sensible defaults."""
        req = PreparedRequest()
        assert req.method == ""
        assert req.url == ""
        assert req.headers == {}
        assert req.body is None


# =============================================================================
# Test Exceptions
# =============================================================================


class TestExceptions:
    """Test requests-compatible exceptions."""

    def test_http_error(self):
        """HTTPError should be raiseable."""
        with pytest.raises(HTTPError):
            raise HTTPError("404 Not Found")

    def test_http_error_with_response(self):
        """HTTPError should include response."""
        response = MagicMock()
        error = HTTPError("Error", response=response)
        assert error.response is response

    def test_connection_error(self):
        """ConnectionError should be raiseable."""
        with pytest.raises(ConnectionError):
            raise ConnectionError("Connection failed")

    def test_timeout(self):
        """Timeout should be raiseable."""
        with pytest.raises(Timeout):
            raise Timeout("Request timed out")

    def test_request_exception(self):
        """RequestException should be raiseable."""
        with pytest.raises(RequestException):
            raise RequestException("General error")


# =============================================================================
# Test Module-Level Functions
# =============================================================================


class TestModuleFunctions:
    """Test that module-level functions exist and are callable."""

    def test_get_exists(self):
        """requests.get should exist."""
        assert callable(requests.get)

    def test_post_exists(self):
        """requests.post should exist."""
        assert callable(requests.post)

    def test_put_exists(self):
        """requests.put should exist."""
        assert callable(requests.put)

    def test_delete_exists(self):
        """requests.delete should exist."""
        assert callable(requests.delete)

    def test_patch_exists(self):
        """requests.patch should exist."""
        assert callable(requests.patch)

    def test_head_exists(self):
        """requests.head should exist."""
        assert callable(requests.head)

    def test_options_exists(self):
        """requests.options should exist."""
        assert callable(requests.options)

    def test_request_exists(self):
        """requests.request should exist."""
        assert callable(requests.request)

    def test_session_exists(self):
        """requests.Session should exist."""
        assert requests.Session is not None


# =============================================================================
# Test Session
# =============================================================================


class TestSession:
    """Test Session class compatibility."""

    def test_init_with_api_key(self):
        """Session should initialize with API key."""
        session = Session(api_key="test_key")
        assert session._api_key == "test_key"
        # Don't close - no actual session created yet

    def test_init_from_env(self):
        """Session should read API key from environment."""
        with patch.dict(os.environ, {"SCRAPPEY_API_KEY": "env_key"}):
            session = Session()
            assert session._api_key == "env_key"

    def test_init_no_key_raises(self):
        """Session should raise error without API key."""
        with patch.dict(os.environ, {"SCRAPPEY_API_KEY": ""}, clear=True):
            with pytest.raises(ValueError) as exc_info:
                Session()
            assert "API key required" in str(exc_info.value)

    def test_session_headers(self):
        """Session should have headers dict."""
        session = Session(api_key="test_key")
        assert isinstance(session.headers, dict)
        session.headers["X-Custom"] = "value"
        assert session.headers["X-Custom"] == "value"

    def test_session_cookies(self):
        """Session should have cookies jar."""
        session = Session(api_key="test_key")
        assert isinstance(session.cookies, RequestsCookieJar)
        session.cookies.set("name", "value")
        assert session.cookies.get("name") == "value"

    def test_session_request_type(self):
        """Session should accept request_type parameter."""
        session = Session(api_key="test_key", request_type="request")
        assert session._request_type == "request"

    def test_session_request_type_default(self):
        """Session should default request_type to None (browser mode)."""
        session = Session(api_key="test_key")
        assert session._request_type is None

    def test_session_methods_exist(self):
        """Session should have HTTP methods."""
        session = Session(api_key="test_key")
        assert callable(session.get)
        assert callable(session.post)
        assert callable(session.put)
        assert callable(session.delete)
        assert callable(session.patch)
        assert callable(session.head)
        assert callable(session.options)
        assert callable(session.request)
        assert callable(session.close)

    def test_session_repr(self):
        """Session should have readable repr."""
        session = Session(api_key="test_key")
        assert "Session" in repr(session)


# =============================================================================
# Test Request Function with Mocked Scrappey Client
# =============================================================================


class TestRequestWithMock:
    """Test request function with mocked Scrappey client."""

    @pytest.fixture
    def mock_scrappey(self):
        """Create a mock Scrappey client."""
        with patch("scrappey.requests.Scrappey") as MockScrappey:
            mock_client = MagicMock()
            mock_client.get.return_value = {
                "solution": {
                    "statusCode": 200,
                    "response": '{"message": "success"}',
                    "currentUrl": "https://example.com",
                    "cookies": [],
                    "responseHeaders": {"content-type": "application/json"},
                },
                "timeElapsed": 100,
                "data": "success",
            }
            mock_client.post.return_value = mock_client.get.return_value
            MockScrappey.return_value = mock_client
            yield MockScrappey, mock_client

    def test_get_returns_response(self, mock_scrappey):
        """get() should return Response object."""
        MockScrappey, mock_client = mock_scrappey
        
        with patch.dict(os.environ, {"SCRAPPEY_API_KEY": "test_key"}):
            response = requests.get("https://example.com")
        
        assert isinstance(response, Response)
        assert response.status_code == 200

    def test_get_calls_scrappey(self, mock_scrappey):
        """get() should call Scrappey.get()."""
        MockScrappey, mock_client = mock_scrappey
        
        with patch.dict(os.environ, {"SCRAPPEY_API_KEY": "test_key"}):
            requests.get("https://example.com")
        
        mock_client.get.assert_called_once()
        call_kwargs = mock_client.get.call_args[1]
        assert call_kwargs["url"] == "https://example.com"

    def test_post_with_data(self, mock_scrappey):
        """post() should pass form data."""
        MockScrappey, mock_client = mock_scrappey
        
        with patch.dict(os.environ, {"SCRAPPEY_API_KEY": "test_key"}):
            requests.post("https://example.com", data={"key": "value"})
        
        mock_client.post.assert_called_once()
        call_kwargs = mock_client.post.call_args[1]
        assert "postData" in call_kwargs

    def test_post_with_json(self, mock_scrappey):
        """post() should pass JSON data."""
        MockScrappey, mock_client = mock_scrappey
        
        with patch.dict(os.environ, {"SCRAPPEY_API_KEY": "test_key"}):
            requests.post("https://example.com", json={"key": "value"})
        
        mock_client.post.assert_called_once()
        call_kwargs = mock_client.post.call_args[1]
        assert call_kwargs["postData"] == {"key": "value"}

    def test_custom_headers(self, mock_scrappey):
        """Should pass custom headers to Scrappey."""
        MockScrappey, mock_client = mock_scrappey
        
        with patch.dict(os.environ, {"SCRAPPEY_API_KEY": "test_key"}):
            requests.get("https://example.com", headers={"X-Custom": "value"})
        
        call_kwargs = mock_client.get.call_args[1]
        assert call_kwargs["customHeaders"] == {"X-Custom": "value"}

    def test_cookies(self, mock_scrappey):
        """Should pass cookies to Scrappey."""
        MockScrappey, mock_client = mock_scrappey
        
        with patch.dict(os.environ, {"SCRAPPEY_API_KEY": "test_key"}):
            requests.get("https://example.com", cookies={"session": "abc123"})
        
        call_kwargs = mock_client.get.call_args[1]
        assert "cookies" in call_kwargs
        assert "session=abc123" in call_kwargs["cookies"]

    def test_proxies(self, mock_scrappey):
        """Should pass proxy to Scrappey."""
        MockScrappey, mock_client = mock_scrappey
        
        with patch.dict(os.environ, {"SCRAPPEY_API_KEY": "test_key"}):
            requests.get("https://example.com", proxies={"https": "http://proxy:8080"})
        
        call_kwargs = mock_client.get.call_args[1]
        assert call_kwargs["proxy"] == "http://proxy:8080"

    def test_timeout(self, mock_scrappey):
        """Should pass timeout to Scrappey."""
        MockScrappey, mock_client = mock_scrappey
        
        with patch.dict(os.environ, {"SCRAPPEY_API_KEY": "test_key"}):
            requests.get("https://example.com", timeout=30)
        
        call_kwargs = mock_client.get.call_args[1]
        assert call_kwargs["timeout"] == 30000  # Converted to ms

    def test_params(self, mock_scrappey):
        """Should append params to URL."""
        MockScrappey, mock_client = mock_scrappey
        
        with patch.dict(os.environ, {"SCRAPPEY_API_KEY": "test_key"}):
            requests.get("https://example.com", params={"key": "value"})
        
        call_kwargs = mock_client.get.call_args[1]
        assert "key=value" in call_kwargs["url"]

    def test_request_type_browser(self, mock_scrappey):
        """Should not pass requestType when not specified (defaults to browser)."""
        MockScrappey, mock_client = mock_scrappey
        
        with patch.dict(os.environ, {"SCRAPPEY_API_KEY": "test_key"}):
            requests.get("https://example.com")
        
        call_kwargs = mock_client.get.call_args[1]
        # requestType should not be set if not specified
        assert "requestType" not in call_kwargs

    def test_request_type_request(self, mock_scrappey):
        """Should pass requestType='request' to Scrappey."""
        MockScrappey, mock_client = mock_scrappey
        
        with patch.dict(os.environ, {"SCRAPPEY_API_KEY": "test_key"}):
            requests.get("https://example.com", request_type="request")
        
        call_kwargs = mock_client.get.call_args[1]
        assert call_kwargs["requestType"] == "request"

    def test_request_type_post(self, mock_scrappey):
        """Should pass requestType for POST requests."""
        MockScrappey, mock_client = mock_scrappey
        
        with patch.dict(os.environ, {"SCRAPPEY_API_KEY": "test_key"}):
            requests.post("https://example.com", json={"data": "test"}, request_type="request")
        
        call_kwargs = mock_client.post.call_args[1]
        assert call_kwargs["requestType"] == "request"


# =============================================================================
# Test Warnings for Unsupported Parameters
# =============================================================================


class TestUnsupportedParameterWarnings:
    """Test that unsupported parameters generate warnings."""

    @pytest.fixture
    def mock_scrappey(self):
        """Create a mock Scrappey client."""
        with patch("scrappey.requests.Scrappey") as MockScrappey:
            mock_client = MagicMock()
            mock_client.get.return_value = {
                "solution": {
                    "statusCode": 200,
                    "response": "",
                    "cookies": [],
                    "responseHeaders": {},
                },
                "data": "success",
            }
            MockScrappey.return_value = mock_client
            yield MockScrappey, mock_client

    def test_files_warning(self, mock_scrappey):
        """Should warn when files parameter is used."""
        with patch.dict(os.environ, {"SCRAPPEY_API_KEY": "test_key"}):
            with pytest.warns(UserWarning, match="files"):
                requests.get("https://example.com", files={"file": "content"})

    def test_auth_warning(self, mock_scrappey):
        """Should warn when auth parameter is used."""
        with patch.dict(os.environ, {"SCRAPPEY_API_KEY": "test_key"}):
            with pytest.warns(UserWarning, match="auth"):
                requests.get("https://example.com", auth=("user", "pass"))

    def test_stream_warning(self, mock_scrappey):
        """Should warn when stream parameter is used."""
        with patch.dict(os.environ, {"SCRAPPEY_API_KEY": "test_key"}):
            with pytest.warns(UserWarning, match="stream"):
                requests.get("https://example.com", stream=True)

    def test_verify_false_warning(self, mock_scrappey):
        """Should warn when verify=False is used."""
        with patch.dict(os.environ, {"SCRAPPEY_API_KEY": "test_key"}):
            with pytest.warns(UserWarning, match="verify"):
                requests.get("https://example.com", verify=False)

    def test_cert_warning(self, mock_scrappey):
        """Should warn when cert parameter is used."""
        with patch.dict(os.environ, {"SCRAPPEY_API_KEY": "test_key"}):
            with pytest.warns(UserWarning, match="cert"):
                requests.get("https://example.com", cert="/path/to/cert")


# =============================================================================
# Test API Compatibility (interface matching)
# =============================================================================


class TestAPICompatibility:
    """Test that the API matches the requests library interface."""

    def test_response_has_requests_attributes(self):
        """Response should have all common requests.Response attributes."""
        response = Response({
            "solution": {
                "statusCode": 200,
                "response": "test",
                "cookies": [],
                "responseHeaders": {},
            },
            "data": "success",
        })
        
        # Check all common attributes exist
        assert hasattr(response, "status_code")
        assert hasattr(response, "text")
        assert hasattr(response, "content")
        assert hasattr(response, "headers")
        assert hasattr(response, "cookies")
        assert hasattr(response, "url")
        assert hasattr(response, "ok")
        assert hasattr(response, "is_redirect")
        assert hasattr(response, "is_permanent_redirect")
        assert hasattr(response, "encoding")
        assert hasattr(response, "reason")
        assert hasattr(response, "elapsed")
        assert hasattr(response, "request")
        assert hasattr(response, "history")
        assert hasattr(response, "links")
        assert hasattr(response, "apparent_encoding")
        
        # Check methods exist
        assert callable(response.json)
        assert callable(response.raise_for_status)
        assert callable(response.iter_content)
        assert callable(response.iter_lines)
        assert callable(response.close)

    def test_session_has_requests_attributes(self):
        """Session should have all common requests.Session attributes."""
        session = Session(api_key="test_key")
        
        # Check attributes exist
        assert hasattr(session, "headers")
        assert hasattr(session, "cookies")
        assert hasattr(session, "proxies")
        assert hasattr(session, "auth")
        assert hasattr(session, "params")
        assert hasattr(session, "verify")
        assert hasattr(session, "cert")
        assert hasattr(session, "max_redirects")
        assert hasattr(session, "trust_env")
        
        # Check methods exist
        assert callable(session.get)
        assert callable(session.post)
        assert callable(session.put)
        assert callable(session.delete)
        assert callable(session.patch)
        assert callable(session.head)
        assert callable(session.options)
        assert callable(session.request)
        assert callable(session.close)

    def test_module_has_all_exports(self):
        """Module should export all expected names."""
        # Functions
        assert hasattr(requests, "get")
        assert hasattr(requests, "post")
        assert hasattr(requests, "put")
        assert hasattr(requests, "delete")
        assert hasattr(requests, "patch")
        assert hasattr(requests, "head")
        assert hasattr(requests, "options")
        assert hasattr(requests, "request")
        
        # Classes
        assert hasattr(requests, "Session")
        assert hasattr(requests, "Response")
        assert hasattr(requests, "PreparedRequest")
        assert hasattr(requests, "RequestsCookieJar")
        
        # Exceptions
        assert hasattr(requests, "HTTPError")
        assert hasattr(requests, "ConnectionError")
        assert hasattr(requests, "Timeout")
        assert hasattr(requests, "RequestException")
