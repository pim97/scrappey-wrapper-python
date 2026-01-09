"""
Drop-in replacement for the `requests` library using Scrappey.

This module provides a requests-compatible API that uses Scrappey behind the scenes,
enabling automatic Cloudflare bypass, antibot solving, and captcha solving.

Usage:
    # Instead of: import requests
    from scrappey import requests

    # Or: from scrappey.requests import get, post, Session

    # Then use exactly like the requests library:
    response = requests.get("https://example.com")
    print(response.text)
    print(response.status_code)

    # Sessions work too:
    session = requests.Session()
    session.get("https://example.com/login")
    session.post("https://example.com/login", data={"user": "test"})

Environment Variables:
    SCRAPPEY_API_KEY: Your Scrappey API key (required)

Note:
    Some requests parameters are not supported and will generate warnings:
    - verify (SSL verification not applicable)
    - cert (client certificates not supported)
    - stream (streaming not supported)
    - files (file uploads not directly supported)
    - auth (use headers instead)
"""

from __future__ import annotations

import json as json_module
import os
import warnings
from datetime import timedelta
from http.cookiejar import CookieJar
from typing import Any, Dict, Iterator, List, Mapping, Optional, Union
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from .client import Scrappey
from .exceptions import ScrappeyError


# Type aliases
HeadersType = Optional[Mapping[str, str]]
CookiesType = Optional[Union[Dict[str, str], "RequestsCookieJar"]]
ParamsType = Optional[Union[Dict[str, Any], List[tuple], bytes, str]]
DataType = Optional[Union[Dict[str, Any], List[tuple], bytes, str]]
JsonType = Optional[Any]
ProxiesType = Optional[Dict[str, str]]
TimeoutType = Optional[Union[float, tuple]]


class RequestsCookieJar(CookieJar):
    """
    A CookieJar that mimics requests.cookies.RequestsCookieJar.
    """

    def __init__(self) -> None:
        super().__init__()
        self._cookies: Dict[str, str] = {}

    def set(self, name: str, value: str, **kwargs: Any) -> None:
        """Set a cookie."""
        self._cookies[name] = value

    def get(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get a cookie value."""
        return self._cookies.get(name, default)

    def items(self) -> Iterator[tuple]:
        """Iterate over cookie items."""
        return iter(self._cookies.items())

    def keys(self) -> Iterator[str]:
        """Iterate over cookie names."""
        return iter(self._cookies.keys())

    def values(self) -> Iterator[str]:
        """Iterate over cookie values."""
        return iter(self._cookies.values())

    def update(self, other: Union[Dict[str, str], "RequestsCookieJar", None] = None) -> None:
        """Update cookies from another dict or CookieJar."""
        if other is None:
            return
        if isinstance(other, RequestsCookieJar):
            self._cookies.update(other._cookies)
        elif isinstance(other, dict):
            self._cookies.update(other)

    def __iter__(self) -> Iterator[str]:
        return iter(self._cookies)

    def __len__(self) -> int:
        return len(self._cookies)

    def __getitem__(self, name: str) -> str:
        return self._cookies[name]

    def __setitem__(self, name: str, value: str) -> None:
        self._cookies[name] = value

    def __contains__(self, name: object) -> bool:
        return name in self._cookies

    def get_dict(self) -> Dict[str, str]:
        """Return cookies as a dict."""
        return self._cookies.copy()


class PreparedRequest:
    """A PreparedRequest object (minimal implementation for compatibility)."""

    def __init__(
        self,
        method: str = "",
        url: str = "",
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
    ) -> None:
        self.method = method
        self.url = url
        self.headers = headers or {}
        self.body = body
        self.path_url = urlparse(url).path or "/"


class Response:
    """
    A Response object that mimics requests.Response.

    This wraps a Scrappey API response and provides the same interface
    as the popular requests library's Response object.

    Attributes:
        status_code: HTTP status code (e.g., 200, 404)
        text: Response body as text
        content: Response body as bytes
        headers: Response headers as a dict
        cookies: Response cookies as RequestsCookieJar
        url: Final URL after redirects
        encoding: Response encoding
        reason: HTTP status reason phrase
        elapsed: Time elapsed for the request
        request: The PreparedRequest that was sent
        ok: True if status_code < 400
    """

    def __init__(
        self,
        scrappey_response: Dict[str, Any],
        request: Optional[PreparedRequest] = None,
    ) -> None:
        self._scrappey_response = scrappey_response
        self._json_cache: Optional[Any] = None

        solution = scrappey_response.get("solution", {})

        # Status code
        self.status_code: int = solution.get("statusCode", 0)

        # Response body
        self._text: str = solution.get("response", "")
        self._content: Optional[bytes] = None

        # Headers (case-insensitive)
        response_headers = solution.get("responseHeaders", {})
        self.headers: Dict[str, str] = {
            k.lower(): v for k, v in response_headers.items()
        }

        # Cookies
        self.cookies = RequestsCookieJar()
        for cookie in solution.get("cookies", []):
            if isinstance(cookie, dict):
                name = cookie.get("name", "")
                value = cookie.get("value", "")
                if name:
                    self.cookies.set(name, value)
            elif isinstance(cookie, str) and "=" in cookie:
                # Parse "name=value" format
                parts = cookie.split("=", 1)
                self.cookies.set(parts[0], parts[1] if len(parts) > 1 else "")

        # URL
        self.url: str = solution.get("currentUrl", "")

        # Encoding (detect from headers or default to utf-8)
        content_type = self.headers.get("content-type", "")
        self.encoding: str = "utf-8"
        if "charset=" in content_type:
            try:
                self.encoding = content_type.split("charset=")[1].split(";")[0].strip()
            except (IndexError, ValueError):
                pass

        # Reason phrase
        self.reason: str = self._get_reason_phrase(self.status_code)

        # Elapsed time
        time_elapsed_ms = scrappey_response.get("timeElapsed", 0)
        self.elapsed = timedelta(milliseconds=time_elapsed_ms)

        # Request object
        self.request = request or PreparedRequest()

        # History (redirects) - not tracked by Scrappey
        self.history: List[Response] = []

        # Connection (stub)
        self.connection = None

        # Raw response (stub for compatibility)
        self.raw = None

    @property
    def text(self) -> str:
        """Response body as text."""
        return self._text

    @property
    def content(self) -> bytes:
        """Response body as bytes."""
        if self._content is None:
            self._content = self._text.encode(self.encoding, errors="replace")
        return self._content

    @property
    def ok(self) -> bool:
        """True if status_code is less than 400."""
        return self.status_code < 400

    @property
    def is_redirect(self) -> bool:
        """True if response is a redirect."""
        return self.status_code in (301, 302, 303, 307, 308)

    @property
    def is_permanent_redirect(self) -> bool:
        """True if response is a permanent redirect."""
        return self.status_code in (301, 308)

    @property
    def apparent_encoding(self) -> str:
        """The apparent encoding, as detected by charset detection."""
        return self.encoding

    @property
    def links(self) -> Dict[str, Any]:
        """Returns the parsed header links of the response."""
        # Parse Link header if present
        link_header = self.headers.get("link", "")
        if not link_header:
            return {}
        # Basic Link header parsing
        links = {}
        for link in link_header.split(","):
            parts = link.strip().split(";")
            if len(parts) >= 2:
                url = parts[0].strip(" <>")
                for part in parts[1:]:
                    if "rel=" in part:
                        rel = part.split("=")[1].strip(' "')
                        links[rel] = {"url": url}
        return links

    def json(self, **kwargs: Any) -> Any:
        """
        Parse response body as JSON.

        Args:
            **kwargs: Arguments passed to json.loads()

        Returns:
            Parsed JSON data

        Raises:
            ValueError: If response is not valid JSON
        """
        if self._json_cache is None:
            try:
                self._json_cache = json_module.loads(self.text, **kwargs)
            except json_module.JSONDecodeError as e:
                raise ValueError(f"Response is not valid JSON: {e}") from e
        return self._json_cache

    def raise_for_status(self) -> None:
        """
        Raise an HTTPError if the status code indicates an error.

        Raises:
            HTTPError: If status_code >= 400
        """
        if 400 <= self.status_code < 600:
            raise HTTPError(
                f"{self.status_code} Error: {self.reason} for url: {self.url}",
                response=self,
            )

    def iter_content(self, chunk_size: int = 1, decode_unicode: bool = False) -> Iterator[bytes]:
        """
        Iterate over the response content in chunks.

        Note: Streaming is not supported by Scrappey, so this yields
        the entire content as a single chunk.
        """
        if decode_unicode:
            yield self.text.encode(self.encoding)
        else:
            yield self.content

    def iter_lines(
        self,
        chunk_size: int = 512,
        decode_unicode: bool = False,
        delimiter: Optional[str] = None,
    ) -> Iterator[str]:
        """
        Iterate over the response content line by line.
        """
        content = self.text if decode_unicode else self.content.decode(self.encoding)
        lines = content.splitlines()
        for line in lines:
            yield line

    def close(self) -> None:
        """Close the response (no-op for Scrappey)."""
        pass

    def _get_reason_phrase(self, status_code: int) -> str:
        """Get the HTTP reason phrase for a status code."""
        reasons = {
            200: "OK",
            201: "Created",
            202: "Accepted",
            204: "No Content",
            301: "Moved Permanently",
            302: "Found",
            303: "See Other",
            304: "Not Modified",
            307: "Temporary Redirect",
            308: "Permanent Redirect",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            405: "Method Not Allowed",
            408: "Request Timeout",
            429: "Too Many Requests",
            500: "Internal Server Error",
            502: "Bad Gateway",
            503: "Service Unavailable",
            504: "Gateway Timeout",
        }
        return reasons.get(status_code, "Unknown")

    def __repr__(self) -> str:
        return f"<Response [{self.status_code}]>"

    def __bool__(self) -> bool:
        return self.ok

    def __enter__(self) -> "Response":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


class HTTPError(Exception):
    """An HTTP error occurred."""

    def __init__(self, message: str, response: Optional[Response] = None) -> None:
        super().__init__(message)
        self.response = response


class ConnectionError(Exception):
    """A connection error occurred."""
    pass


class Timeout(Exception):
    """The request timed out."""
    pass


class RequestException(Exception):
    """Base exception for requests errors."""
    pass


class Session:
    """
    A Session object that mimics requests.Session.

    Sessions maintain cookies across requests and allow you to persist
    certain parameters across requests.

    Example:
        ```python
        from scrappey import requests

        session = requests.Session()
        session.headers.update({"User-Agent": "My App"})

        # Cookies are maintained across requests
        session.get("https://example.com/login")
        session.post("https://example.com/dashboard", data={"action": "view"})

        # Clean up
        session.close()
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        request_type: Optional[str] = None,
    ) -> None:
        """
        Initialize a Session.

        Args:
            api_key: Scrappey API key. If not provided, uses SCRAPPEY_API_KEY env var.
            request_type: Default request mode - "browser" (default) or "request" (faster, cheaper)
        """
        self._api_key = api_key or os.environ.get("SCRAPPEY_API_KEY", "")
        if not self._api_key:
            raise ValueError(
                "API key required. Set SCRAPPEY_API_KEY environment variable "
                "or pass api_key to Session()"
            )

        self._scrappey = Scrappey(api_key=self._api_key)
        self._session_id: Optional[str] = None
        self._request_type = request_type

        # Session-level settings
        self.headers: Dict[str, str] = {}
        self.cookies = RequestsCookieJar()
        self.proxies: Dict[str, str] = {}
        self.auth: Optional[tuple] = None
        self.params: Dict[str, Any] = {}
        self.verify: bool = True
        self.cert: Optional[str] = None
        self.max_redirects: int = 30
        self.trust_env: bool = True

    def _ensure_session(self) -> str:
        """Ensure a Scrappey session exists, creating one if needed."""
        if self._session_id is None:
            # Extract proxy from self.proxies if set
            proxy = None
            if self.proxies:
                proxy = self.proxies.get("https") or self.proxies.get("http")

            result = self._scrappey.create_session(proxy=proxy)
            self._session_id = result.get("session", "")
        return self._session_id

    def _merge_kwargs(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Merge session-level settings with request-level kwargs."""
        # Merge headers
        merged_headers = dict(self.headers)
        if "headers" in kwargs:
            merged_headers.update(kwargs["headers"])
        kwargs["headers"] = merged_headers

        # Merge cookies
        merged_cookies = self.cookies.get_dict()
        if "cookies" in kwargs:
            if isinstance(kwargs["cookies"], dict):
                merged_cookies.update(kwargs["cookies"])
            elif isinstance(kwargs["cookies"], RequestsCookieJar):
                merged_cookies.update(kwargs["cookies"].get_dict())
        kwargs["cookies"] = merged_cookies

        # Merge params
        merged_params = dict(self.params)
        if "params" in kwargs:
            if isinstance(kwargs["params"], dict):
                merged_params.update(kwargs["params"])
        kwargs["params"] = merged_params

        # Use session proxies if not overridden
        if "proxies" not in kwargs and self.proxies:
            kwargs["proxies"] = self.proxies

        # Use session request_type if not overridden
        if "request_type" not in kwargs and self._request_type:
            kwargs["request_type"] = self._request_type

        return kwargs

    def request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> Response:
        """
        Send a request.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to request
            **kwargs: Additional arguments (headers, data, json, etc.)

        Returns:
            Response object
        """
        # Ensure we have a session
        session_id = self._ensure_session()

        # Merge session-level settings
        kwargs = self._merge_kwargs(kwargs)

        # Build the request
        response = _request(
            method=method,
            url=url,
            scrappey_client=self._scrappey,
            session_id=session_id,
            **kwargs,
        )

        # Update session cookies from response
        self.cookies.update(response.cookies)

        return response

    def get(self, url: str, **kwargs: Any) -> Response:
        """Send a GET request."""
        return self.request("GET", url, **kwargs)

    def post(self, url: str, data: DataType = None, json: JsonType = None, **kwargs: Any) -> Response:
        """Send a POST request."""
        return self.request("POST", url, data=data, json=json, **kwargs)

    def put(self, url: str, data: DataType = None, json: JsonType = None, **kwargs: Any) -> Response:
        """Send a PUT request."""
        return self.request("PUT", url, data=data, json=json, **kwargs)

    def delete(self, url: str, **kwargs: Any) -> Response:
        """Send a DELETE request."""
        return self.request("DELETE", url, **kwargs)

    def patch(self, url: str, data: DataType = None, json: JsonType = None, **kwargs: Any) -> Response:
        """Send a PATCH request."""
        return self.request("PATCH", url, data=data, json=json, **kwargs)

    def head(self, url: str, **kwargs: Any) -> Response:
        """Send a HEAD request."""
        kwargs.setdefault("allow_redirects", False)
        return self.request("HEAD", url, **kwargs)

    def options(self, url: str, **kwargs: Any) -> Response:
        """Send an OPTIONS request."""
        return self.request("OPTIONS", url, **kwargs)

    def close(self) -> None:
        """Close the session and destroy the Scrappey session."""
        if self._session_id:
            try:
                self._scrappey.destroy_session(self._session_id)
            except ScrappeyError:
                pass  # Ignore errors during cleanup
            self._session_id = None
        self._scrappey.close()

    def __enter__(self) -> "Session":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"<scrappey.requests.Session [{self._session_id or 'not started'}]>"


def _build_url_with_params(url: str, params: ParamsType) -> str:
    """Build a URL with query parameters."""
    if not params:
        return url

    parsed = urlparse(url)
    existing_params = parse_qs(parsed.query)

    # Merge params
    if isinstance(params, dict):
        for key, value in params.items():
            existing_params[key] = [str(value)]
    elif isinstance(params, (list, tuple)):
        for key, value in params:
            existing_params[key] = [str(value)]
    elif isinstance(params, str):
        for key, value in parse_qs(params).items():
            existing_params[key] = value

    # Build new query string
    new_query = urlencode(existing_params, doseq=True)

    # Reconstruct URL
    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        new_query,
        parsed.fragment,
    ))


def _request(
    method: str,
    url: str,
    params: ParamsType = None,
    data: DataType = None,
    json: JsonType = None,
    headers: HeadersType = None,
    cookies: CookiesType = None,
    files: Any = None,
    auth: Optional[tuple] = None,
    timeout: TimeoutType = None,
    allow_redirects: bool = True,
    proxies: ProxiesType = None,
    hooks: Any = None,
    stream: bool = False,
    verify: bool = True,
    cert: Any = None,
    request_type: Optional[str] = None,
    scrappey_client: Optional[Scrappey] = None,
    session_id: Optional[str] = None,
    **kwargs: Any,
) -> Response:
    """
    Internal request function that maps requests parameters to Scrappey.
    
    Args:
        request_type: Request mode - "browser" (default) or "request" (faster, cheaper)
    """
    # Warn about unsupported parameters
    if files is not None:
        warnings.warn(
            "The 'files' parameter is not supported by Scrappey. File uploads are ignored.",
            UserWarning,
            stacklevel=3,
        )

    if auth is not None:
        warnings.warn(
            "The 'auth' parameter is not supported by Scrappey. "
            "Use headers={'Authorization': '...'} instead.",
            UserWarning,
            stacklevel=3,
        )

    if stream:
        warnings.warn(
            "The 'stream' parameter is not supported by Scrappey. "
            "Response content is returned in full.",
            UserWarning,
            stacklevel=3,
        )

    if not verify:
        warnings.warn(
            "The 'verify' parameter is ignored by Scrappey. "
            "SSL verification is handled by the service.",
            UserWarning,
            stacklevel=3,
        )

    if cert is not None:
        warnings.warn(
            "The 'cert' parameter is not supported by Scrappey. "
            "Client certificates cannot be used.",
            UserWarning,
            stacklevel=3,
        )

    if not allow_redirects:
        warnings.warn(
            "The 'allow_redirects=False' is not fully supported by Scrappey. "
            "Redirects are handled by the browser.",
            UserWarning,
            stacklevel=3,
        )

    if hooks is not None:
        warnings.warn(
            "The 'hooks' parameter is not supported by Scrappey.",
            UserWarning,
            stacklevel=3,
        )

    # Build URL with params
    full_url = _build_url_with_params(url, params)

    # Get or create Scrappey client
    own_client = False
    if scrappey_client is None:
        api_key = os.environ.get("SCRAPPEY_API_KEY", "")
        if not api_key:
            raise ValueError(
                "API key required. Set SCRAPPEY_API_KEY environment variable."
            )
        scrappey_client = Scrappey(api_key=api_key)
        own_client = True

    try:
        # Build Scrappey options
        scrappey_options: Dict[str, Any] = {
            "url": full_url,
        }

        # Add request type if specified
        if request_type:
            scrappey_options["requestType"] = request_type

        # Add session if provided
        if session_id:
            scrappey_options["session"] = session_id

        # Map headers
        if headers:
            scrappey_options["customHeaders"] = dict(headers)

        # Map cookies
        if cookies:
            if isinstance(cookies, dict):
                cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
            elif isinstance(cookies, RequestsCookieJar):
                cookie_str = "; ".join(f"{k}={v}" for k, v in cookies.items())
            else:
                cookie_str = str(cookies)
            scrappey_options["cookies"] = cookie_str

        # Map proxies
        if proxies:
            # Use https proxy if available, otherwise http
            proxy = proxies.get("https") or proxies.get("http")
            if proxy:
                scrappey_options["proxy"] = proxy

        # Map timeout
        if timeout is not None:
            if isinstance(timeout, tuple):
                # (connect_timeout, read_timeout) - use the larger one
                scrappey_options["timeout"] = int(max(timeout) * 1000)
            else:
                scrappey_options["timeout"] = int(timeout * 1000)

        # Map data/json for POST/PUT/PATCH
        if method.upper() in ("POST", "PUT", "PATCH"):
            if json is not None:
                scrappey_options["postData"] = json
            elif data is not None:
                if isinstance(data, dict):
                    # Form-encode the data
                    scrappey_options["postData"] = urlencode(data)
                elif isinstance(data, (list, tuple)):
                    scrappey_options["postData"] = urlencode(data)
                else:
                    scrappey_options["postData"] = str(data)

        # Create PreparedRequest for the response
        prepared = PreparedRequest(
            method=method.upper(),
            url=full_url,
            headers=dict(headers) if headers else {},
            body=scrappey_options.get("postData"),
        )

        # Make the request using the appropriate method
        method_upper = method.upper()
        if method_upper == "GET":
            result = scrappey_client.get(**scrappey_options)
        elif method_upper == "POST":
            result = scrappey_client.post(**scrappey_options)
        elif method_upper == "PUT":
            result = scrappey_client.put(**scrappey_options)
        elif method_upper == "DELETE":
            result = scrappey_client.delete(**scrappey_options)
        elif method_upper == "PATCH":
            result = scrappey_client.patch(**scrappey_options)
        elif method_upper in ("HEAD", "OPTIONS"):
            # Use GET for HEAD/OPTIONS as Scrappey may not support them directly
            result = scrappey_client.get(**scrappey_options)
        else:
            # Generic request
            scrappey_options["cmd"] = f"request.{method.lower()}"
            result = scrappey_client.request(scrappey_options)

        # Check for errors
        if result.get("data") == "error":
            error_msg = result.get("error", "Unknown error")
            raise RequestException(f"Scrappey error: {error_msg}")

        return Response(result, request=prepared)

    finally:
        if own_client:
            scrappey_client.close()


# Module-level convenience functions
def get(
    url: str,
    params: ParamsType = None,
    *,
    request_type: Optional[str] = None,
    **kwargs: Any,
) -> Response:
    """
    Send a GET request.

    Args:
        url: URL to request
        params: Query parameters
        request_type: Request mode - "browser" (default) or "request" (faster, cheaper)
        **kwargs: Additional arguments

    Returns:
        Response object

    Example:
        ```python
        from scrappey import requests

        # Browser mode (default) - better for protected sites
        response = requests.get("https://httpbin.org/get")
        
        # Request mode - faster and cheaper (0.2 balance vs 1 balance)
        response = requests.get("https://httpbin.org/get", request_type="request")
        ```
    """
    return _request("GET", url, params=params, request_type=request_type, **kwargs)


def post(
    url: str,
    data: DataType = None,
    json: JsonType = None,
    *,
    request_type: Optional[str] = None,
    **kwargs: Any,
) -> Response:
    """
    Send a POST request.

    Args:
        url: URL to request
        data: Form data to send
        json: JSON data to send
        request_type: Request mode - "browser" (default) or "request" (faster, cheaper)
        **kwargs: Additional arguments

    Returns:
        Response object

    Example:
        ```python
        from scrappey import requests

        # Form data
        response = requests.post("https://httpbin.org/post", data={"key": "value"})

        # JSON data with request mode (faster)
        response = requests.post(
            "https://httpbin.org/post",
            json={"key": "value"},
            request_type="request",
        )
        ```
    """
    return _request("POST", url, data=data, json=json, request_type=request_type, **kwargs)


def put(
    url: str,
    data: DataType = None,
    json: JsonType = None,
    **kwargs: Any,
) -> Response:
    """Send a PUT request."""
    return _request("PUT", url, data=data, json=json, **kwargs)


def delete(url: str, **kwargs: Any) -> Response:
    """Send a DELETE request."""
    return _request("DELETE", url, **kwargs)


def patch(
    url: str,
    data: DataType = None,
    json: JsonType = None,
    **kwargs: Any,
) -> Response:
    """Send a PATCH request."""
    return _request("PATCH", url, data=data, json=json, **kwargs)


def head(url: str, **kwargs: Any) -> Response:
    """Send a HEAD request."""
    kwargs.setdefault("allow_redirects", False)
    return _request("HEAD", url, **kwargs)


def options(url: str, **kwargs: Any) -> Response:
    """Send an OPTIONS request."""
    return _request("OPTIONS", url, **kwargs)


def request(method: str, url: str, **kwargs: Any) -> Response:
    """
    Send a request with the specified method.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        url: URL to request
        **kwargs: Additional arguments

    Returns:
        Response object
    """
    return _request(method, url, **kwargs)


# For "import scrappey.requests as requests" or "from scrappey import requests"
# We make this module act like the requests module
__all__ = [
    # Functions
    "get",
    "post",
    "put",
    "delete",
    "patch",
    "head",
    "options",
    "request",
    # Classes
    "Session",
    "Response",
    "PreparedRequest",
    "RequestsCookieJar",
    # Exceptions
    "HTTPError",
    "ConnectionError",
    "Timeout",
    "RequestException",
]
