"""
Asynchronous Scrappey API client.

This module provides the AsyncScrappey class for async applications.
For synchronous usage, see client.py.
"""

from typing import Any, Dict, List, Optional, Union

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
    SessionCreateResponse,
    SessionListResponse,
)


class AsyncScrappey:
    """
    Asynchronous client for the Scrappey web scraping API.
    
    This client is designed for async applications using asyncio.
    For synchronous usage, use the Scrappey class instead.
    
    Args:
        api_key: Your Scrappey API key from https://app.scrappey.com
        base_url: API base URL (default: https://publisher.scrappey.com/api/v1)
        timeout: Default request timeout in seconds (default: 300)
    
    Example:
        ```python
        import asyncio
        from scrappey import AsyncScrappey
        
        async def main():
            async with AsyncScrappey(api_key="your_api_key") as scrappey:
                # Simple GET request
                result = await scrappey.get(url="https://example.com")
                print(result["solution"]["response"])
                
                # Parallel requests
                urls = ["https://example1.com", "https://example2.com"]
                results = await asyncio.gather(*[
                    scrappey.get(url=url) for url in urls
                ])
        
        asyncio.run(main())
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
        self._client = httpx.AsyncClient(timeout=timeout)
    
    async def __aenter__(self) -> "AsyncScrappey":
        return self
    
    async def __aexit__(self, *args: Any) -> None:
        await self.close()
    
    async def close(self) -> None:
        """Close the HTTP client and release resources."""
        await self._client.aclose()
    
    async def _request(self, cmd: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
            response = await self._client.post(
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
    
    async def get(
        self,
        url: str,
        *,
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
            result = await scrappey.get(
                url="https://example.com",
                cloudflareBypass=True,
            )
            html = result["solution"]["response"]
            ```
        """
        data: Dict[str, Any] = {"url": url}
        
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
        
        data.update(kwargs)
        
        return await self._request("request.get", data)
    
    async def post(
        self,
        url: str,
        *,
        postData: Optional[Union[str, Dict[str, Any]]] = None,
        session: Optional[str] = None,
        customHeaders: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> ScrappeyResponse:
        """
        Perform a POST request to the specified URL.
        
        Args:
            url: The target URL
            postData: Data to send (string or dict for JSON)
            session: Session ID for cookie/state persistence
            customHeaders: Custom HTTP headers
            **kwargs: Additional API options
        
        Returns:
            API response containing the result
        """
        data: Dict[str, Any] = {"url": url}
        
        if postData is not None:
            data["postData"] = postData
        if session is not None:
            data["session"] = session
        if customHeaders is not None:
            data["customHeaders"] = customHeaders
        
        data.update(kwargs)
        
        return await self._request("request.post", data)
    
    async def put(
        self,
        url: str,
        *,
        postData: Optional[Union[str, Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> ScrappeyResponse:
        """
        Perform a PUT request to the specified URL.
        
        Args:
            url: The target URL
            postData: Data to send
            **kwargs: Additional API options
        
        Returns:
            API response containing the result
        """
        data: Dict[str, Any] = {"url": url}
        
        if postData is not None:
            data["postData"] = postData
        
        data.update(kwargs)
        
        return await self._request("request.put", data)
    
    async def delete(self, url: str, **kwargs: Any) -> ScrappeyResponse:
        """
        Perform a DELETE request to the specified URL.
        
        Args:
            url: The target URL
            **kwargs: Additional API options
        
        Returns:
            API response containing the result
        """
        data: Dict[str, Any] = {"url": url}
        data.update(kwargs)
        
        return await self._request("request.delete", data)
    
    async def patch(
        self,
        url: str,
        *,
        postData: Optional[Union[str, Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> ScrappeyResponse:
        """
        Perform a PATCH request to the specified URL.
        
        Args:
            url: The target URL
            postData: Data to send
            **kwargs: Additional API options
        
        Returns:
            API response containing the result
        """
        data: Dict[str, Any] = {"url": url}
        
        if postData is not None:
            data["postData"] = postData
        
        data.update(kwargs)
        
        return await self._request("request.patch", data)
    
    async def request(self, options: RequestOptions) -> ScrappeyResponse:
        """
        Perform a request with full options object.
        
        Args:
            options: Full request options including 'cmd' for the method
        
        Returns:
            API response containing the result
        """
        cmd = options.get("cmd", "request.get")
        data = {k: v for k, v in options.items() if k != "cmd"}
        return await self._request(cmd, data)
    
    # ========================================================================
    # Session Management
    # ========================================================================
    
    async def create_session(
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
        
        Args:
            session: Optional custom session ID
            proxy: Custom proxy for this session
            proxyCountry: Request proxy from specific country
            premiumProxy: Use premium proxy
            mobileProxy: Use mobile proxy
            **kwargs: Additional session options
        
        Returns:
            Session creation response containing the session ID
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
        
        return await self._request("sessions.create", data)
    
    async def destroy_session(self, session: str) -> ScrappeyResponse:
        """
        Destroy an existing session and release resources.
        
        Args:
            session: The session ID to destroy
        
        Returns:
            API response confirming destruction
        """
        return await self._request("sessions.destroy", {"session": session})
    
    async def list_sessions(self) -> SessionListResponse:
        """
        List all active sessions for your account.
        
        Returns:
            Response containing list of active sessions and limits
        """
        return await self._request("sessions.list", {})
    
    async def is_session_active(self, session: str) -> bool:
        """
        Check if a session is currently active.
        
        Args:
            session: The session ID to check
        
        Returns:
            True if the session is active, False otherwise
        """
        response: SessionActiveResponse = await self._request(
            "sessions.active", {"session": session}
        )
        return response.get("active", False)
    
    # ========================================================================
    # Browser Actions
    # ========================================================================
    
    async def browser_action(
        self,
        url: str,
        actions: List[BrowserAction],
        *,
        session: Optional[str] = None,
        **kwargs: Any,
    ) -> ScrappeyResponse:
        """
        Execute browser actions on a page.
        
        Args:
            url: The target URL
            actions: List of browser actions to execute
            session: Session ID for state persistence
            **kwargs: Additional API options
        
        Returns:
            API response with results after actions complete
        """
        return await self.get(
            url=url,
            session=session,
            browserActions=actions,
            **kwargs,
        )
    
    # ========================================================================
    # Screenshot
    # ========================================================================
    
    async def screenshot(
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
        
        return await self._request("request.get", data)
