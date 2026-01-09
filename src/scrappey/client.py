"""
Synchronous Scrappey API client.

This module provides the main Scrappey class for interacting with the Scrappey
web scraping API. For async support, see async_client.py.
"""

from typing import Any, Dict, List, Literal, Optional, Union

import httpx

from .exceptions import (
    ScrappeyAuthenticationError,
    ScrappeyConnectionError,
    ScrappeyError,
    ScrappeyTimeoutError,
)
from .types import (
    BrowserAction,
    RequestOptions,
    ScrappeyResponse,
    SessionActiveResponse,
    SessionCreateOptions,
    SessionCreateResponse,
    SessionListResponse,
)


class Scrappey:
    """
    Synchronous client for the Scrappey web scraping API.
    
    Scrappey provides web scraping with automatic Cloudflare bypass, antibot
    solving, captcha solving, and browser automation capabilities.
    
    Args:
        api_key: Your Scrappey API key from https://app.scrappey.com
        base_url: API base URL (default: https://publisher.scrappey.com/api/v1)
        timeout: Default request timeout in seconds (default: 300)
    
    Example:
        ```python
        from scrappey import Scrappey
        
        # Initialize client
        scrappey = Scrappey(api_key="your_api_key")
        
        # Simple GET request
        result = scrappey.get(url="https://example.com")
        print(result["solution"]["response"])
        
        # With session for cookie persistence
        session = scrappey.create_session()
        result = scrappey.get(
            url="https://example.com",
            session=session["session"]
        )
        scrappey.destroy_session(session["session"])
        ```
    
    See Also:
        - Documentation: https://wiki.scrappey.com/getting-started
        - Request Builder: https://app.scrappey.com/#/builder
    """
    
    DEFAULT_BASE_URL = "https://publisher.scrappey.com/api/v1"
    DEFAULT_TIMEOUT = 300  # 5 minutes
    
    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        if not api_key:
            raise ScrappeyAuthenticationError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)
    
    def __enter__(self) -> "Scrappey":
        return self
    
    def __exit__(self, *args: Any) -> None:
        self.close()
    
    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self._client.close()
    
    def _request(self, cmd: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Send a request to the Scrappey API.
        
        Args:
            cmd: The API command (e.g., "request.get", "sessions.create")
            data: Additional request parameters
        
        Returns:
            The API response as a dictionary
        
        Raises:
            ScrappeyConnectionError: If unable to connect to the API
            ScrappeyTimeoutError: If the request times out
            ScrappeyAuthenticationError: If the API key is invalid
            ScrappeyError: For other API errors
        """
        url = f"{self.base_url}?key={self.api_key}"
        
        payload: Dict[str, Any] = {"cmd": cmd}
        if data:
            payload.update(data)
        
        try:
            response = self._client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
        except httpx.ConnectError as e:
            raise ScrappeyConnectionError(
                f"Failed to connect to Scrappey API: {e}"
            ) from e
        except httpx.TimeoutException as e:
            raise ScrappeyTimeoutError(
                f"Request timed out: {e}"
            ) from e
        except httpx.HTTPError as e:
            raise ScrappeyError(f"HTTP error: {e}") from e
        
        # Check for authentication errors
        if response.status_code == 401:
            raise ScrappeyAuthenticationError(
                "Invalid API key",
                status_code=401,
            )
        
        # Parse response
        try:
            return response.json()
        except Exception as e:
            raise ScrappeyError(
                f"Failed to parse API response: {e}",
                status_code=response.status_code,
            ) from e
    
    # ========================================================================
    # HTTP Request Methods
    # ========================================================================
    
    def get(
        self,
        url: str,
        *,
        requestType: Optional[Literal["browser", "request"]] = None,
        session: Optional[str] = None,
        proxy: Optional[str] = None,
        proxyCountry: Optional[str] = None,
        premiumProxy: Optional[bool] = None,
        mobileProxy: Optional[bool] = None,
        browserActions: Optional[List[BrowserAction]] = None,
        automaticallySolveCaptchas: Optional[bool] = None,
        cloudflareBypass: Optional[bool] = None,
        datadomeBypass: Optional[bool] = None,
        kasadaBypass: Optional[bool] = None,
        screenshot: Optional[bool] = None,
        video: Optional[bool] = None,
        cssSelector: Optional[str] = None,
        innerText: Optional[bool] = None,
        **kwargs: Any,
    ) -> ScrappeyResponse:
        """
        Perform a GET request to the specified URL.
        
        Args:
            url: The target URL to scrape
            requestType: Request mode - "browser" (default, headless browser, 1 balance)
                        or "request" (HTTP library with TLS, faster, 0.2 balance)
            session: Session ID for cookie/state persistence
            proxy: Custom proxy (format: http://user:pass@ip:port)
            proxyCountry: Request proxy from specific country (e.g., "UnitedStates")
            premiumProxy: Use premium residential-like proxies
            mobileProxy: Use mobile carrier proxies
            browserActions: List of browser actions to execute
            automaticallySolveCaptchas: Auto-solve detected captchas
            cloudflareBypass: Enable Cloudflare-specific bypass
            datadomeBypass: Enable Datadome bypass
            kasadaBypass: Enable Kasada bypass
            screenshot: Capture page screenshot
            video: Record browser session as video
            cssSelector: Extract content matching CSS selector
            innerText: Include inner text of elements
            **kwargs: Additional API options (see RequestOptions type)
        
        Returns:
            API response containing the scraped data
        
        Example:
            ```python
            # Simple request (browser mode, default)
            result = scrappey.get(url="https://example.com")
            html = result["solution"]["response"]
            
            # Fast request mode (cheaper, faster)
            result = scrappey.get(
                url="https://example.com",
                requestType="request",
            )
            
            # With Cloudflare bypass and screenshot
            result = scrappey.get(
                url="https://protected-site.com",
                cloudflareBypass=True,
                screenshot=True,
                premiumProxy=True,
            )
            ```
        """
        data: Dict[str, Any] = {"url": url}
        
        if requestType is not None:
            data["requestType"] = requestType
        
        # Add optional parameters
        if session is not None:
            data["session"] = session
        if proxy is not None:
            data["proxy"] = proxy
        if proxyCountry is not None:
            data["proxyCountry"] = proxyCountry
        if premiumProxy is not None:
            data["premiumProxy"] = premiumProxy
        if mobileProxy is not None:
            data["mobileProxy"] = mobileProxy
        if browserActions is not None:
            data["browserActions"] = browserActions
        if automaticallySolveCaptchas is not None:
            data["automaticallySolveCaptchas"] = automaticallySolveCaptchas
        if cloudflareBypass is not None:
            data["cloudflareBypass"] = cloudflareBypass
        if datadomeBypass is not None:
            data["datadomeBypass"] = datadomeBypass
        if kasadaBypass is not None:
            data["kasadaBypass"] = kasadaBypass
        if screenshot is not None:
            data["screenshot"] = screenshot
        if video is not None:
            data["video"] = video
        if cssSelector is not None:
            data["cssSelector"] = cssSelector
        if innerText is not None:
            data["innerText"] = innerText
        
        # Add any additional kwargs
        data.update(kwargs)
        
        return self._request("request.get", data)
    
    def post(
        self,
        url: str,
        *,
        postData: Optional[Union[str, Dict[str, Any]]] = None,
        requestType: Optional[Literal["browser", "request"]] = None,
        session: Optional[str] = None,
        customHeaders: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> ScrappeyResponse:
        """
        Perform a POST request to the specified URL.
        
        Args:
            url: The target URL
            postData: Data to send (string or dict for JSON)
            requestType: Request mode - "browser" (default) or "request" (faster, cheaper)
            session: Session ID for cookie/state persistence
            customHeaders: Custom HTTP headers (e.g., {"content-type": "application/json"})
            **kwargs: Additional API options
        
        Returns:
            API response containing the result
        
        Example:
            ```python
            # Form data
            result = scrappey.post(
                url="https://example.com/login",
                postData="username=user&password=pass",
            )
            
            # JSON data with request mode (faster)
            result = scrappey.post(
                url="https://api.example.com/data",
                postData={"key": "value"},
                customHeaders={"content-type": "application/json"},
                requestType="request",
            )
            ```
        """
        data: Dict[str, Any] = {"url": url}
        
        if postData is not None:
            data["postData"] = postData
        if requestType is not None:
            data["requestType"] = requestType
        if session is not None:
            data["session"] = session
        if customHeaders is not None:
            data["customHeaders"] = customHeaders
        
        data.update(kwargs)
        
        return self._request("request.post", data)
    
    def put(
        self,
        url: str,
        *,
        postData: Optional[Union[str, Dict[str, Any]]] = None,
        requestType: Optional[Literal["browser", "request"]] = None,
        **kwargs: Any,
    ) -> ScrappeyResponse:
        """
        Perform a PUT request to the specified URL.
        
        Args:
            url: The target URL
            postData: Data to send
            requestType: Request mode - "browser" (default) or "request" (faster, cheaper)
            **kwargs: Additional API options
        
        Returns:
            API response containing the result
        """
        data: Dict[str, Any] = {"url": url}
        
        if postData is not None:
            data["postData"] = postData
        if requestType is not None:
            data["requestType"] = requestType
        
        data.update(kwargs)
        
        return self._request("request.put", data)
    
    def delete(
        self,
        url: str,
        *,
        requestType: Optional[Literal["browser", "request"]] = None,
        **kwargs: Any,
    ) -> ScrappeyResponse:
        """
        Perform a DELETE request to the specified URL.
        
        Args:
            url: The target URL
            requestType: Request mode - "browser" (default) or "request" (faster, cheaper)
            **kwargs: Additional API options
        
        Returns:
            API response containing the result
        """
        data: Dict[str, Any] = {"url": url}
        if requestType is not None:
            data["requestType"] = requestType
        data.update(kwargs)
        
        return self._request("request.delete", data)
    
    def patch(
        self,
        url: str,
        *,
        postData: Optional[Union[str, Dict[str, Any]]] = None,
        requestType: Optional[Literal["browser", "request"]] = None,
        **kwargs: Any,
    ) -> ScrappeyResponse:
        """
        Perform a PATCH request to the specified URL.
        
        Args:
            url: The target URL
            postData: Data to send
            requestType: Request mode - "browser" (default) or "request" (faster, cheaper)
            **kwargs: Additional API options
        
        Returns:
            API response containing the result
        """
        data: Dict[str, Any] = {"url": url}
        
        if postData is not None:
            data["postData"] = postData
        if requestType is not None:
            data["requestType"] = requestType
        
        data.update(kwargs)
        
        return self._request("request.patch", data)
    
    def request(self, options: RequestOptions) -> ScrappeyResponse:
        """
        Perform a request with full options object.
        
        This method allows passing a complete RequestOptions dictionary,
        which is useful when building requests programmatically or when
        using the request builder output directly.
        
        Args:
            options: Full request options including 'cmd' for the method
        
        Returns:
            API response containing the result
        
        Example:
            ```python
            # Use output from request builder
            result = scrappey.request({
                "cmd": "request.get",
                "url": "https://example.com",
                "browserActions": [
                    {"type": "wait", "wait": 2000}
                ]
            })
            ```
        """
        cmd = options.get("cmd", "request.get")
        data = {k: v for k, v in options.items() if k != "cmd"}
        return self._request(cmd, data)
    
    # ========================================================================
    # Session Management
    # ========================================================================
    
    def create_session(
        self,
        session: Optional[str] = None,
        proxy: Optional[str] = None,
        proxyCountry: Optional[str] = None,
        premiumProxy: Optional[bool] = None,
        mobileProxy: Optional[bool] = None,
        **kwargs: Any,
    ) -> SessionCreateResponse:
        """
        Create a new browser session.
        
        Sessions persist browser state (cookies, localStorage) across requests.
        Use the returned session ID in subsequent requests for state persistence.
        
        Args:
            session: Optional custom session ID (auto-generated if not provided)
            proxy: Custom proxy for this session
            proxyCountry: Request proxy from specific country
            premiumProxy: Use premium proxy
            mobileProxy: Use mobile proxy
            **kwargs: Additional session options
        
        Returns:
            Session creation response containing the session ID
        
        Example:
            ```python
            # Create session
            session_data = scrappey.create_session(
                proxyCountry="UnitedStates",
                premiumProxy=True,
            )
            session_id = session_data["session"]
            
            # Use session for requests
            result = scrappey.get(
                url="https://example.com",
                session=session_id,
            )
            
            # Clean up
            scrappey.destroy_session(session_id)
            ```
        """
        data: Dict[str, Any] = {}
        
        if session is not None:
            data["session"] = session
        if proxy is not None:
            data["proxy"] = proxy
        if proxyCountry is not None:
            data["proxyCountry"] = proxyCountry
        if premiumProxy is not None:
            data["premiumProxy"] = premiumProxy
        if mobileProxy is not None:
            data["mobileProxy"] = mobileProxy
        
        data.update(kwargs)
        
        return self._request("sessions.create", data)
    
    def destroy_session(self, session: str) -> ScrappeyResponse:
        """
        Destroy an existing session and release resources.
        
        Always destroy sessions when done to free server resources.
        
        Args:
            session: The session ID to destroy
        
        Returns:
            API response confirming destruction
        
        Example:
            ```python
            scrappey.destroy_session(session_id)
            ```
        """
        return self._request("sessions.destroy", {"session": session})
    
    def list_sessions(self) -> SessionListResponse:
        """
        List all active sessions for your account.
        
        Returns:
            Response containing list of active sessions and limits
        
        Example:
            ```python
            sessions = scrappey.list_sessions()
            print(f"Open sessions: {sessions['open']}/{sessions['limit']}")
            for s in sessions["sessions"]:
                print(f"  - {s['session']}")
            ```
        """
        return self._request("sessions.list", {})
    
    def is_session_active(self, session: str) -> bool:
        """
        Check if a session is currently active.
        
        Args:
            session: The session ID to check
        
        Returns:
            True if the session is active, False otherwise
        
        Example:
            ```python
            if scrappey.is_session_active(session_id):
                result = scrappey.get(url="...", session=session_id)
            else:
                session_id = scrappey.create_session()["session"]
            ```
        """
        response: SessionActiveResponse = self._request(
            "sessions.active", {"session": session}
        )
        return response.get("active", False)
    
    # ========================================================================
    # Browser Actions
    # ========================================================================
    
    def browser_action(
        self,
        url: str,
        actions: List[BrowserAction],
        *,
        session: Optional[str] = None,
        **kwargs: Any,
    ) -> ScrappeyResponse:
        """
        Execute browser actions on a page.
        
        This is a convenience method for performing browser automation.
        Actions are executed sequentially after page load.
        
        Args:
            url: The target URL
            actions: List of browser actions to execute
            session: Session ID for state persistence
            **kwargs: Additional API options
        
        Returns:
            API response with results after actions complete
        
        Example:
            ```python
            result = scrappey.browser_action(
                url="https://example.com/login",
                actions=[
                    {"type": "type", "cssSelector": "#email", "text": "user@example.com"},
                    {"type": "type", "cssSelector": "#password", "text": "password123"},
                    {"type": "click", "cssSelector": "#submit"},
                    {"type": "wait_for_selector", "cssSelector": ".dashboard"},
                ],
            )
            ```
        """
        return self.get(
            url=url,
            session=session,
            browserActions=actions,
            **kwargs,
        )
    
    # ========================================================================
    # Screenshot
    # ========================================================================
    
    def screenshot(
        self,
        url: str,
        *,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fullPage: bool = False,
        session: Optional[str] = None,
        browserActions: Optional[List[BrowserAction]] = None,
        **kwargs: Any,
    ) -> ScrappeyResponse:
        """
        Capture a screenshot of a webpage.
        
        Args:
            url: The target URL
            width: Screenshot width in pixels
            height: Screenshot height in pixels
            fullPage: Capture full page instead of viewport
            session: Session ID for state persistence
            browserActions: Actions to execute before screenshot
            **kwargs: Additional API options
        
        Returns:
            API response with screenshot in solution.screenshot (base64)
            or solution.screenshotUrl (if screenshotUpload=True)
        
        Example:
            ```python
            result = scrappey.screenshot(
                url="https://example.com",
                width=1920,
                height=1080,
            )
            screenshot_base64 = result["solution"]["screenshot"]
            ```
        """
        data: Dict[str, Any] = {
            "url": url,
            "screenshot": True,
        }
        
        if width is not None:
            data["screenshotWidth"] = width
        if height is not None:
            data["screenshotHeight"] = height
        if session is not None:
            data["session"] = session
        if browserActions is not None:
            data["browserActions"] = browserActions
        
        data.update(kwargs)
        
        return self._request("request.get", data)
