"""
Scrappey - Python Example

This example demonstrates how to use the Scrappey Python wrapper
for web scraping with Cloudflare bypass and browser automation.

Prerequisites:
    pip install scrappey

Get your API key at: https://app.scrappey.com
"""

import os

from scrappey import Scrappey

# Get API key from environment or replace with your key
API_KEY = os.getenv("SCRAPPEY_API_KEY", "YOUR_API_KEY")


def basic_example():
    """Basic example: Simple GET request."""
    print("\n=== Basic Example ===\n")

    scrappey = Scrappey(api_key=API_KEY)

    try:
        # Simple GET request
        result = scrappey.get(url="https://httpbin.org/get")

        if result.get("data") == "success":
            print(f"Status: {result['solution']['statusCode']}")
            print(f"Response: {result['solution']['response'][:200]}...")
        else:
            print(f"Error: {result.get('error')}")

    finally:
        scrappey.close()


def session_example():
    """Session example: Maintain cookies across requests."""
    print("\n=== Session Example ===\n")

    scrappey = Scrappey(api_key=API_KEY)

    try:
        # Create a session
        session_data = scrappey.create_session()
        session_id = session_data["session"]
        print(f"Created session: {session_id}")

        # Use session for requests (cookies persist)
        result = scrappey.get(
            url="https://httpbin.org/cookies/set/test/value123",
            session=session_id,
        )
        print(f"Set cookie, status: {result['solution']['statusCode']}")

        # Verify cookie persists
        result = scrappey.get(
            url="https://httpbin.org/cookies",
            session=session_id,
        )
        print(f"Cookies: {result['solution']['response']}")

        # Clean up session
        scrappey.destroy_session(session_id)
        print(f"Destroyed session: {session_id}")

    finally:
        scrappey.close()


def cloudflare_example():
    """Cloudflare bypass example."""
    print("\n=== Cloudflare Bypass Example ===\n")

    scrappey = Scrappey(api_key=API_KEY)

    try:
        result = scrappey.get(
            url="https://example-protected-site.com",
            cloudflareBypass=True,
            premiumProxy=True,
            proxyCountry="UnitedStates",
        )

        if result.get("data") == "success":
            print(f"Successfully bypassed! Status: {result['solution']['statusCode']}")
            print(f"Detected providers: {result['solution'].get('detectedAntibotProviders')}")
        else:
            print(f"Error: {result.get('error')}")

    finally:
        scrappey.close()


def browser_actions_example():
    """Browser automation example: Login flow."""
    print("\n=== Browser Actions Example ===\n")

    scrappey = Scrappey(api_key=API_KEY)

    try:
        result = scrappey.browser_action(
            url="https://example.com/login",
            actions=[
                # Wait for login form
                {"type": "wait_for_selector", "cssSelector": "#login-form"},
                # Type credentials
                {"type": "type", "cssSelector": "#email", "text": "user@example.com"},
                {"type": "type", "cssSelector": "#password", "text": "password123"},
                # Click submit
                {"type": "click", "cssSelector": "#submit-btn", "waitForSelector": ".dashboard"},
                # Extract data
                {"type": "execute_js", "code": "document.querySelector('.user-name').innerText"},
            ],
        )

        if result.get("data") == "success":
            print(f"Login successful!")
            print(f"JavaScript return: {result['solution'].get('javascriptReturn')}")
        else:
            print(f"Error: {result.get('error')}")

    finally:
        scrappey.close()


def screenshot_example():
    """Screenshot capture example."""
    print("\n=== Screenshot Example ===\n")

    scrappey = Scrappey(api_key=API_KEY)

    try:
        result = scrappey.screenshot(
            url="https://example.com",
            width=1920,
            height=1080,
        )

        if result.get("data") == "success":
            screenshot_base64 = result["solution"].get("screenshot")
            if screenshot_base64:
                # Save screenshot
                import base64
                with open("screenshot.png", "wb") as f:
                    f.write(base64.b64decode(screenshot_base64))
                print("Screenshot saved to screenshot.png")
        else:
            print(f"Error: {result.get('error')}")

    finally:
        scrappey.close()


def captcha_solving_example():
    """Automatic captcha solving example."""
    print("\n=== Captcha Solving Example ===\n")

    scrappey = Scrappey(api_key=API_KEY)

    try:
        result = scrappey.get(
            url="https://example.com/protected",
            automaticallySolveCaptchas=True,
            alwaysLoad=["recaptcha", "hcaptcha", "turnstile"],
        )

        if result.get("data") == "success":
            captcha_result = result["solution"].get("captchaSolveResult")
            print(f"Captcha solve result: {captcha_result}")
            print(f"Page content length: {len(result['solution']['response'])}")
        else:
            print(f"Error: {result.get('error')}")

    finally:
        scrappey.close()


def context_manager_example():
    """Using Scrappey as a context manager."""
    print("\n=== Context Manager Example ===\n")

    with Scrappey(api_key=API_KEY) as scrappey:
        result = scrappey.get(url="https://httpbin.org/get")
        print(f"Status: {result.get('data')}")
        # Client is automatically closed when exiting the context


def main():
    """Run all examples."""
    print("Scrappey Python Examples")
    print("=" * 50)

    try:
        basic_example()
        session_example()
        context_manager_example()
        # Uncomment to run additional examples:
        # cloudflare_example()
        # browser_actions_example()
        # screenshot_example()
        # captcha_solving_example()

        print("\n✓ All examples completed!\n")

    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    main()
