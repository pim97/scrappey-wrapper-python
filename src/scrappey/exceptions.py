"""
Exceptions for Scrappey API.

This module provides custom exception classes for handling Scrappey API errors.
Note: The Scrappey API handles most error conditions internally and returns
error information in the response. These exceptions are for client-side issues.
"""

from typing import Any, Dict, Optional


class ScrappeyError(Exception):
    """
    Base exception for Scrappey API errors.
    
    This exception is raised for client-side errors such as network issues
    or invalid configurations. API-level errors (like antibot blocks or
    captcha failures) are returned in the response and should be handled
    by checking the response's 'data' field.
    
    Attributes:
        message: Human-readable error message
        response: The raw API response, if available
        status_code: HTTP status code, if available
    
    Example:
        ```python
        try:
            result = scrappey.get(url="https://example.com")
        except ScrappeyError as e:
            print(f"Client error: {e.message}")
        ```
    """
    
    def __init__(
        self,
        message: str,
        response: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.response = response
        self.status_code = status_code
    
    def __str__(self) -> str:
        parts = [self.message]
        if self.status_code is not None:
            parts.append(f"(HTTP {self.status_code})")
        return " ".join(parts)
    
    def __repr__(self) -> str:
        return f"ScrappeyError(message={self.message!r}, status_code={self.status_code!r})"


class ScrappeyConnectionError(ScrappeyError):
    """
    Raised when unable to connect to the Scrappey API.
    
    This typically indicates network issues or that the API is unreachable.
    
    Example:
        ```python
        try:
            result = scrappey.get(url="https://example.com")
        except ScrappeyConnectionError as e:
            print("Cannot reach Scrappey API, check your internet connection")
        ```
    """
    pass


class ScrappeyTimeoutError(ScrappeyError):
    """
    Raised when a request to the Scrappey API times out.
    
    This can happen with complex browser actions or slow target websites.
    Consider increasing the timeout parameter.
    
    Example:
        ```python
        try:
            result = scrappey.get(url="https://slow-site.com", timeout=120000)
        except ScrappeyTimeoutError as e:
            print("Request timed out, try increasing timeout")
        ```
    """
    pass


class ScrappeyAuthenticationError(ScrappeyError):
    """
    Raised when the API key is invalid or missing.
    
    Verify your API key at https://app.scrappey.com
    
    Example:
        ```python
        try:
            scrappey = Scrappey(api_key="invalid_key")
            result = scrappey.get(url="https://example.com")
        except ScrappeyAuthenticationError as e:
            print("Invalid API key")
        ```
    """
    pass
