"""
Scrappey requests-compatible API example.

This example shows how to use Scrappey as a drop-in replacement for the
popular `requests` library. Simply change your import and your existing
code will work with Scrappey's Cloudflare bypass and antibot capabilities!

Requirements:
    pip install scrappey

Environment:
    Set SCRAPPEY_API_KEY environment variable with your API key
"""

import os

# =============================================================================
# MIGRATION EXAMPLE
# =============================================================================
#
# Before (using requests):
#     import requests
#     response = requests.get("https://example.com")
#
# After (using Scrappey):
#     from scrappey import requests
#     response = requests.get("https://example.com")
#
# That's it! Your code now uses Scrappey for automatic Cloudflare bypass!
# =============================================================================

from scrappey import requests

# Ensure API key is set
if not os.environ.get("SCRAPPEY_API_KEY"):
    print("Please set SCRAPPEY_API_KEY environment variable")
    print("Example: export SCRAPPEY_API_KEY=your_api_key")
    exit(1)


def basic_get_example():
    """Basic GET request - works exactly like requests.get()"""
    print("\n=== Basic GET Request ===\n")

    response = requests.get("https://httpbin.org/get")

    print(f"Status Code: {response.status_code}")
    print(f"OK: {response.ok}")
    print(f"URL: {response.url}")
    print(f"Encoding: {response.encoding}")
    print(f"Elapsed: {response.elapsed}")
    print(f"Headers: {dict(list(response.headers.items())[:3])}...")  # First 3 headers

    # Access response body
    print(f"\nResponse text (first 200 chars):\n{response.text[:200]}...")


def get_with_params_example():
    """GET request with query parameters"""
    print("\n=== GET with Query Parameters ===\n")

    response = requests.get(
        "https://httpbin.org/get",
        params={"name": "scrappey", "version": "1.0"},
    )

    print(f"URL with params: {response.url}")
    data = response.json()
    print(f"Server received args: {data.get('args', {})}")


def post_form_example():
    """POST request with form data"""
    print("\n=== POST with Form Data ===\n")

    response = requests.post(
        "https://httpbin.org/post",
        data={"username": "testuser", "password": "testpass"},
    )

    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Server received form: {data.get('form', {})}")


def post_json_example():
    """POST request with JSON data"""
    print("\n=== POST with JSON Data ===\n")

    response = requests.post(
        "https://httpbin.org/post",
        json={"key": "value", "nested": {"data": [1, 2, 3]}},
    )

    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Server received JSON: {data.get('json', {})}")


def custom_headers_example():
    """Request with custom headers"""
    print("\n=== Custom Headers ===\n")

    response = requests.get(
        "https://httpbin.org/headers",
        headers={
            "X-Custom-Header": "my-value",
            "Accept": "application/json",
        },
    )

    print(f"Status Code: {response.status_code}")
    data = response.json()
    print(f"Server saw headers: {data.get('headers', {})}")


def session_example():
    """Using sessions for cookie persistence"""
    print("\n=== Session with Cookie Persistence ===\n")

    # Create a session - cookies persist across requests
    session = requests.Session()

    try:
        # Set a cookie via the server
        print("Setting cookie via /cookies/set...")
        session.get("https://httpbin.org/cookies/set/session_id/abc123")

        # Verify cookie is sent in subsequent request
        print("Verifying cookie in next request...")
        response = session.get("https://httpbin.org/cookies")

        data = response.json()
        print(f"Cookies in session: {data.get('cookies', {})}")

        # Session-level headers persist too
        session.headers.update({"X-Session-Header": "persistent"})
        response = session.get("https://httpbin.org/headers")
        data = response.json()
        print(f"Session header present: {'X-Session-Header' in str(data)}")

    finally:
        # Always close the session to clean up Scrappey resources
        session.close()
        print("Session closed")


def response_methods_example():
    """Demonstrate Response object methods"""
    print("\n=== Response Object Methods ===\n")

    response = requests.get("https://httpbin.org/json")

    # .json() method
    data = response.json()
    print(f"JSON data: {data}")

    # .raise_for_status() - doesn't raise for 200
    try:
        response.raise_for_status()
        print("No error raised for 200 status")
    except requests.HTTPError as e:
        print(f"Error: {e}")

    # Test with error status
    print("\nTesting 404 response...")
    error_response = requests.get("https://httpbin.org/status/404")
    print(f"Status: {error_response.status_code}")
    print(f"OK: {error_response.ok}")

    try:
        error_response.raise_for_status()
    except requests.HTTPError as e:
        print(f"HTTPError raised: {e}")


def cookies_example():
    """Sending cookies with request"""
    print("\n=== Cookies ===\n")

    response = requests.get(
        "https://httpbin.org/cookies",
        cookies={"my_cookie": "cookie_value", "another": "value2"},
    )

    data = response.json()
    print(f"Server received cookies: {data.get('cookies', {})}")

    # Cookies from response
    print(f"Response cookies: {response.cookies.get_dict()}")


def error_handling_example():
    """Error handling"""
    print("\n=== Error Handling ===\n")

    try:
        response = requests.get("https://httpbin.org/status/500")
        response.raise_for_status()
    except requests.HTTPError as e:
        print(f"HTTP Error: {e}")
        print(f"Response status: {e.response.status_code}")

    # Connection errors are also caught
    # try:
    #     response = requests.get("https://invalid-domain-that-does-not-exist.com")
    # except requests.ConnectionError as e:
    #     print(f"Connection Error: {e}")


def cloudflare_protected_site():
    """
    Example: Accessing a Cloudflare-protected site.

    This is where Scrappey shines! Sites protected by Cloudflare, Datadome,
    PerimeterX, etc. are automatically bypassed.
    """
    print("\n=== Cloudflare Protected Site ===\n")

    # This would fail with regular requests, but works with Scrappey!
    response = requests.get("https://nowsecure.nl/")  # Known CF-protected site

    print(f"Status Code: {response.status_code}")
    print(f"Successfully bypassed protection: {response.ok}")
    print(f"Response length: {len(response.text)} characters")


def main():
    """Run all examples."""
    print("=" * 60)
    print("Scrappey requests-compatible API Examples")
    print("=" * 60)

    # Basic examples
    basic_get_example()
    get_with_params_example()
    post_form_example()
    post_json_example()
    custom_headers_example()
    cookies_example()
    response_methods_example()
    error_handling_example()

    # Session example
    session_example()

    # Cloudflare bypass example
    cloudflare_protected_site()

    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
