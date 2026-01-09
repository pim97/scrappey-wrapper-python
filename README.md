# Scrappey - Official Python Wrapper

[![PyPI version](https://badge.fury.io/py/scrappey.svg)](https://badge.fury.io/py/scrappey)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python wrapper for [Scrappey.com](https://scrappey.com) - Web scraping API with automatic Cloudflare bypass, antibot solving, captcha solving, and browser automation.

## Features

- **Cloudflare Bypass** - Automatically bypass Cloudflare protection
- **Antibot Solving** - Handle Datadome, PerimeterX, Kasada, Akamai, and more
- **Captcha Solving** - Automatic solving for reCAPTCHA, hCaptcha, Turnstile
- **Browser Automation** - Full browser control with actions like click, type, scroll
- **Session Management** - Maintain cookies and state across requests
- **Proxy Support** - Built-in proxy rotation with country selection
- **Async Support** - Both sync and async clients included
- **Type Hints** - Full type annotations for IDE support and AI assistants
- **Drop-in Replacement** - Use as a replacement for the `requests` library

## Installation

```bash
pip install scrappey
```

## Quick Start

```python
from scrappey import Scrappey

# Initialize with your API key
scrappey = Scrappey(api_key="YOUR_API_KEY")

# Simple GET request
result = scrappey.get(url="https://example.com")
print(result["solution"]["response"])

# Don't forget to close the client when done
scrappey.close()
```

Or use as a context manager:

```python
from scrappey import Scrappey

with Scrappey(api_key="YOUR_API_KEY") as scrappey:
    result = scrappey.get(url="https://example.com")
    print(result["solution"]["statusCode"])
```

## Request Types

Scrappey supports two request modes with different trade-offs:

| Mode | Description | Cost | Speed |
|------|-------------|------|-------|
| `browser` | Headless browser (default) | 1 balance | Slower, more powerful |
| `request` | HTTP library with TLS | 0.2 balance | Faster, cheaper |

### Browser Mode (Default)

Uses a real headless browser. Best for:
- Sites with JavaScript rendering
- Cloudflare, Datadome, and other antibot protection
- Browser actions and screenshots

```python
# Browser mode is the default
result = scrappey.get(url="https://protected-site.com")
```

### Request Mode

Uses an HTTP library with TLS fingerprinting. Best for:
- Simple API calls
- High-volume scraping
- When you need speed and low cost

```python
# Request mode - 5x cheaper and faster
result = scrappey.get(url="https://api.example.com", requestType="request")

# Works with all HTTP methods
result = scrappey.post(
    url="https://api.example.com/data",
    postData={"key": "value"},
    requestType="request",
)
```

## Async Usage

```python
import asyncio
from scrappey import AsyncScrappey

async def main():
    async with AsyncScrappey(api_key="YOUR_API_KEY") as scrappey:
        # Parallel requests
        urls = ["https://example1.com", "https://example2.com"]
        results = await asyncio.gather(*[
            scrappey.get(url=url) for url in urls
        ])
        for result in results:
            print(result["solution"]["statusCode"])

asyncio.run(main())
```

## Drop-in Replacement for `requests`

Scrappey provides a **drop-in replacement** for the popular `requests` library. Simply change your import and your existing code will work with Scrappey's Cloudflare bypass and antibot capabilities!

### Migration

```python
# Before (using requests)
import requests

response = requests.get("https://example.com")
print(response.text)

# After (using Scrappey) - just change the import!
from scrappey import requests

response = requests.get("https://example.com")
print(response.text)
```

That's it! Your code now uses Scrappey for automatic Cloudflare bypass.

> **Note**: Set the `SCRAPPEY_API_KEY` environment variable with your API key.

### Response Object

The Response object works exactly like `requests.Response`:

```python
from scrappey import requests

response = requests.get("https://httpbin.org/get")

# All standard attributes
print(response.status_code)    # 200
print(response.ok)             # True
print(response.text)           # Response body as text
print(response.content)        # Response body as bytes
print(response.headers)        # Response headers
print(response.cookies)        # Response cookies
print(response.url)            # Final URL
print(response.elapsed)        # Time elapsed

# Methods
data = response.json()         # Parse JSON
response.raise_for_status()    # Raise on 4xx/5xx
```

### Sessions

Sessions maintain cookies and headers across requests:

```python
from scrappey import requests

session = requests.Session()

try:
    # Login
    session.post("https://example.com/login", data={"user": "test"})

    # Subsequent requests include cookies from login
    response = session.get("https://example.com/dashboard")

    # Session-level headers
    session.headers.update({"Authorization": "Bearer token"})
finally:
    session.close()  # Clean up Scrappey session
```

Or use as a context manager:

```python
from scrappey import requests

with requests.Session() as session:
    session.get("https://example.com")
    # Session automatically closed when exiting
```

### Supported Parameters

| Parameter | Supported | Notes |
|-----------|-----------|-------|
| `params` | Yes | Query parameters |
| `data` | Yes | Form data |
| `json` | Yes | JSON data |
| `headers` | Yes | Custom headers |
| `cookies` | Yes | Request cookies |
| `timeout` | Yes | Request timeout |
| `proxies` | Yes | Proxy configuration |
| `request_type` | Yes | "browser" (default) or "request" (faster) |
| `allow_redirects` | Warn | Handled by browser |
| `verify` | Warn | SSL handled by service |
| `stream` | Warn | Not supported |
| `files` | Warn | Not supported |
| `auth` | Warn | Use headers instead |

### Why Use This?

Sites protected by Cloudflare, Datadome, PerimeterX, and other antibots will **just work**:

```python
from scrappey import requests

# This would fail with regular requests, but works with Scrappey!
response = requests.get("https://nowsecure.nl/")  # CF-protected
print(response.status_code)  # 200
```

## Examples

### Cloudflare Bypass

```python
result = scrappey.get(
    url="https://protected-site.com"
)

if result["data"] == "success":
    print("Successfully bypassed Cloudflare!")
    print(result["solution"]["response"])
```

### Session Management

Sessions persist cookies and browser state across requests:

```python
# Create a session
session = scrappey.create_session(proxyCountry="UnitedStates")
session_id = session["session"]

try:
    # All requests with this session share cookies
    scrappey.get(url="https://example.com/login", session=session_id)
    scrappey.get(url="https://example.com/dashboard", session=session_id)
finally:
    # Clean up when done
    scrappey.destroy_session(session_id)
```

### Browser Automation

```python
result = scrappey.browser_action(
    url="https://example.com/login",
    actions=[
        {"type": "wait_for_selector", "cssSelector": "#login-form"},
        {"type": "type", "cssSelector": "#email", "text": "user@example.com"},
        {"type": "type", "cssSelector": "#password", "text": "password123"},
        {"type": "click", "cssSelector": "#submit-btn", "waitForSelector": ".dashboard"},
        {"type": "execute_js", "code": "document.querySelector('.user-name').innerText"},
    ],
)

# Get JavaScript return values
print(result["solution"]["javascriptReturn"])
```

### POST Requests

```python
# Form data
result = scrappey.post(
    url="https://httpbin.org/post",
    postData="username=user&password=pass",
)

# JSON data
result = scrappey.post(
    url="https://api.example.com/data",
    postData={"key": "value"},
    customHeaders={"Content-Type": "application/json"},
)
```

### Automatic Captcha Solving

```python
result = scrappey.get(
    url="https://site-with-captcha.com",
    automaticallySolveCaptchas=True
)
```

### Screenshot Capture

```python
result = scrappey.screenshot(
    url="https://example.com",
    width=1920,
    height=1080,
)

# Save screenshot
import base64
with open("screenshot.png", "wb") as f:
    f.write(base64.b64decode(result["solution"]["screenshot"]))
```

### Using Request Builder Output

Copy directly from the [Request Builder](https://app.scrappey.com/#/builder):

```python
result = scrappey.request({
    "cmd": "request.get",
    "url": "https://example.com",
    "browserActions": [
        {"type": "wait", "wait": 2000},
        {"type": "scroll", "cssSelector": "footer"}
    ],
    "screenshot": True
})
```

## API Reference

### Scrappey Client

```python
Scrappey(
    api_key: str,                    # Your API key (required)
    base_url: str = "...",           # API URL (optional)
    timeout: float = 300,            # Request timeout in seconds
)
```

### Methods

| Method | Description |
|--------|-------------|
| `get(url, **options)` | Perform GET request |
| `post(url, postData, **options)` | Perform POST request |
| `put(url, postData, **options)` | Perform PUT request |
| `delete(url, **options)` | Perform DELETE request |
| `patch(url, postData, **options)` | Perform PATCH request |
| `request(options)` | Send request with full options dict |
| `create_session(**options)` | Create a new session |
| `destroy_session(session)` | Destroy a session |
| `browser_action(url, actions, **options)` | Execute browser actions |
| `screenshot(url, **options)` | Capture screenshot |

### Common Options

| Option | Type | Description |
|--------|------|-------------|
| `requestType` | str | "browser" (default) or "request" (faster, cheaper) |
| `session` | str | Session ID for state persistence |
| `proxy` | str | Custom proxy (http://user:pass@ip:port) |
| `proxyCountry` | str | Proxy country (e.g., "UnitedStates") |
| `premiumProxy` | bool | Use premium residential proxies |
| `mobileProxy` | bool | Use mobile carrier proxies |
| `cloudflareBypass` | bool | Enable Cloudflare bypass |
| `datadomeBypass` | bool | Enable Datadome bypass |
| `kasadaBypass` | bool | Enable Kasada bypass |
| `automaticallySolveCaptchas` | bool | Auto-solve captchas |
| `browserActions` | list | Browser automation actions |
| `screenshot` | bool | Capture screenshot |
| `cssSelector` | str | Extract content by CSS selector |
| `customHeaders` | dict | Custom HTTP headers |

### Response Structure

```python
{
    "solution": {
        "verified": True,
        "response": "<html>...</html>",
        "statusCode": 200,
        "currentUrl": "https://example.com",
        "cookies": [...],
        "cookieString": "session=abc; token=xyz",
        "userAgent": "Mozilla/5.0...",
        "screenshot": "base64...",
        "javascriptReturn": [...],
    },
    "timeElapsed": 1234,
    "data": "success",  # or "error"
    "session": "session-id",
    "error": "error message if failed"
}
```

## Multi-Language Examples

Examples are provided for:

- **Python** - `examples/python/`
- **Node.js** - `examples/nodejs/`
- **TypeScript** - `examples/typescript/`
- **Go** - `examples/go/`
- **Java** - `examples/java/`
- **C#** - `examples/csharp/`
- **PHP** - `examples/php/`
- **Ruby** - `examples/ruby/`
- **Rust** - `examples/rust/`
- **Kotlin** - `examples/kotlin/`
- **cURL** - `examples/curl/`

## Error Handling

The API returns errors in the response body. Check the `data` field:

```python
result = scrappey.get(url="https://example.com")

if result["data"] == "success":
    html = result["solution"]["response"]
else:
    error = result.get("error", "Unknown error")
    print(f"Request failed: {error}")
```

Client-side errors raise exceptions:

```python
from scrappey import (
    ScrappeyError,
    ScrappeyConnectionError,
    ScrappeyTimeoutError,
    ScrappeyAuthenticationError,
)

try:
    result = scrappey.get(url="https://example.com")
except ScrappeyConnectionError:
    print("Could not connect to API")
except ScrappeyTimeoutError:
    print("Request timed out")
except ScrappeyAuthenticationError:
    print("Invalid API key")
except ScrappeyError as e:
    print(f"API error: {e}")
```

## Links

- **Website**: https://scrappey.com
- **Documentation**: https://wiki.scrappey.com/getting-started
- **Request Builder**: https://app.scrappey.com/#/builder
- **API Reference**: https://wiki.scrappey.com/api-reference
- **GitHub**: https://github.com/pim97/scrappey-wrapper-python

## License

MIT License - see [LICENSE](LICENSE) for details.

## Disclaimer

Please ensure that your web scraping activities comply with the website's terms of service and legal regulations. Scrappey is not responsible for any misuse or unethical use of the library. Use responsibly and respect website policies.
