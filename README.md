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
