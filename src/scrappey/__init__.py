"""
Scrappey - Official Python wrapper for Scrappey.com

Web scraping API with Cloudflare bypass, antibot solving, captcha solving,
and browser automation capabilities.

Example:
    ```python
    from scrappey import Scrappey

    # Initialize client
    scrappey = Scrappey(api_key="your_api_key")

    # Simple GET request
    result = scrappey.get(url="https://example.com")
    print(result["solution"]["response"])
    ```

For async usage:
    ```python
    import asyncio
    from scrappey import AsyncScrappey

    async def main():
        async with AsyncScrappey(api_key="your_api_key") as scrappey:
            result = await scrappey.get(url="https://example.com")
            print(result["solution"]["response"])

    asyncio.run(main())
    ```

Drop-in replacement for requests library:
    ```python
    # Instead of: import requests
    from scrappey import requests

    # Use exactly like the requests library
    response = requests.get("https://example.com")
    print(response.text)
    print(response.status_code)
    ```

Links:
    - Website: https://scrappey.com
    - Documentation: https://wiki.scrappey.com/getting-started
    - Request Builder: https://app.scrappey.com/#/builder
    - GitHub: https://github.com/pim97/scrappey-wrapper-python
"""

from . import requests
from .async_client import AsyncScrappey
from .client import Scrappey
from .exceptions import (
    ScrappeyAuthenticationError,
    ScrappeyConnectionError,
    ScrappeyError,
    ScrappeyTimeoutError,
)
from .types import (
    BrowserAction,
    CaptchaData,
    ClickAction,
    Cookie,
    CookieJarItem,
    DropdownAction,
    ExecuteJsAction,
    GotoAction,
    HoverAction,
    KeyboardAction,
    RequestOptions,
    ScrollAction,
    ScrappeyResponse,
    SessionActiveResponse,
    SessionCreateOptions,
    SessionCreateResponse,
    SessionInfo,
    SessionListResponse,
    SetViewportAction,
    Solution,
    SolveCaptchaAction,
    SwitchIframeAction,
    TypeAction,
    WaitAction,
    WaitForCookieAction,
    WaitForFunctionAction,
    WaitForLoadStateAction,
    WaitForSelectorAction,
    WhileAction,
)

__version__ = "1.0.3"

__all__ = [
    # Main clients
    "Scrappey",
    "AsyncScrappey",
    # Requests-compatible API
    "requests",
    # Exceptions
    "ScrappeyError",
    "ScrappeyConnectionError",
    "ScrappeyTimeoutError",
    "ScrappeyAuthenticationError",
    # Response types
    "ScrappeyResponse",
    "Solution",
    "SessionCreateResponse",
    "SessionListResponse",
    "SessionActiveResponse",
    "SessionInfo",
    # Request types
    "RequestOptions",
    "SessionCreateOptions",
    "Cookie",
    "CookieJarItem",
    # Browser action types
    "BrowserAction",
    "ClickAction",
    "TypeAction",
    "GotoAction",
    "WaitAction",
    "WaitForSelectorAction",
    "WaitForFunctionAction",
    "WaitForLoadStateAction",
    "WaitForCookieAction",
    "ExecuteJsAction",
    "ScrollAction",
    "HoverAction",
    "KeyboardAction",
    "DropdownAction",
    "SwitchIframeAction",
    "SetViewportAction",
    "WhileAction",
    "SolveCaptchaAction",
    "CaptchaData",
]
