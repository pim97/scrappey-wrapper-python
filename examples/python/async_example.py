"""
Scrappey - Async Python Example

This example demonstrates how to use the AsyncScrappey client
for async/await web scraping workflows.

Prerequisites:
    pip install scrappey

Get your API key at: https://app.scrappey.com
"""

import asyncio
import os

from scrappey import AsyncScrappey

# Get API key from environment or replace with your key
API_KEY = os.getenv("SCRAPPEY_API_KEY", "YOUR_API_KEY")


async def basic_async_example():
    """Basic async example: Simple GET request."""
    print("\n=== Basic Async Example ===\n")

    async with AsyncScrappey(api_key=API_KEY) as scrappey:
        result = await scrappey.get(url="https://httpbin.org/get")

        if result.get("data") == "success":
            print(f"Status: {result['solution']['statusCode']}")
            print(f"Response: {result['solution']['response'][:200]}...")
        else:
            print(f"Error: {result.get('error')}")


async def parallel_requests_example():
    """Parallel requests example: Scrape multiple URLs concurrently."""
    print("\n=== Parallel Requests Example ===\n")

    urls = [
        "https://httpbin.org/get?id=1",
        "https://httpbin.org/get?id=2",
        "https://httpbin.org/get?id=3",
        "https://httpbin.org/get?id=4",
        "https://httpbin.org/get?id=5",
    ]

    async with AsyncScrappey(api_key=API_KEY) as scrappey:
        # Create session for all requests
        session_data = await scrappey.create_session()
        session_id = session_data["session"]

        try:
            # Run requests in parallel
            tasks = [
                scrappey.get(url=url, session=session_id)
                for url in urls
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for url, result in zip(urls, results):
                if isinstance(result, Exception):
                    print(f"  {url}: Error - {result}")
                elif result.get("data") == "success":
                    print(f"  {url}: Status {result['solution']['statusCode']}")
                else:
                    print(f"  {url}: API Error - {result.get('error')}")

        finally:
            # Clean up session
            await scrappey.destroy_session(session_id)
            print(f"\nSession destroyed: {session_id}")


async def session_management_example():
    """Async session management example."""
    print("\n=== Async Session Management Example ===\n")

    async with AsyncScrappey(api_key=API_KEY) as scrappey:
        # Create session
        session_data = await scrappey.create_session(
            proxyCountry="UnitedStates",
            premiumProxy=True,
        )
        session_id = session_data["session"]
        print(f"Created session: {session_id}")

        # Check if session is active
        is_active = await scrappey.is_session_active(session_id)
        print(f"Session active: {is_active}")

        # List all sessions
        sessions = await scrappey.list_sessions()
        print(f"Open sessions: {sessions.get('open')}/{sessions.get('limit')}")

        # Use session for login flow
        result = await scrappey.browser_action(
            url="https://example.com",
            session=session_id,
            actions=[
                {"type": "wait", "wait": 1000},
                {"type": "execute_js", "code": "document.title"},
            ],
        )

        if result.get("data") == "success":
            print(f"Page title: {result['solution'].get('javascriptReturn')}")

        # Destroy session
        await scrappey.destroy_session(session_id)
        print(f"Destroyed session: {session_id}")


async def rate_limited_scraping():
    """Rate-limited scraping with semaphore."""
    print("\n=== Rate Limited Scraping Example ===\n")

    urls = [f"https://httpbin.org/get?page={i}" for i in range(10)]
    max_concurrent = 3  # Maximum concurrent requests
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_limit(scrappey: AsyncScrappey, url: str, session: str):
        async with semaphore:
            print(f"Fetching: {url}")
            result = await scrappey.get(url=url, session=session)
            return url, result

    async with AsyncScrappey(api_key=API_KEY) as scrappey:
        session_data = await scrappey.create_session()
        session_id = session_data["session"]

        try:
            tasks = [fetch_with_limit(scrappey, url, session_id) for url in urls]
            results = await asyncio.gather(*tasks)

            success_count = sum(
                1 for _, r in results 
                if not isinstance(r, Exception) and r.get("data") == "success"
            )
            print(f"\nCompleted: {success_count}/{len(urls)} successful")

        finally:
            await scrappey.destroy_session(session_id)


async def main():
    """Run all async examples."""
    print("Scrappey Async Python Examples")
    print("=" * 50)

    try:
        await basic_async_example()
        await parallel_requests_example()
        await session_management_example()
        # Uncomment to run additional examples:
        # await rate_limited_scraping()

        print("\n✓ All async examples completed!\n")

    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
