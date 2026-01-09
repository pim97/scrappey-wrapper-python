#!/bin/bash
#
# Scrappey - cURL Examples
#
# This script demonstrates how to use the Scrappey API with cURL
# for web scraping with Cloudflare bypass and browser automation.
#
# Prerequisites:
#   - cURL
#   - jq (optional, for pretty JSON output)
#
# Usage:
#   chmod +x examples.sh
#   export SCRAPPEY_API_KEY="your_api_key"
#   ./examples.sh
#
# Get your API key at: https://app.scrappey.com

API_KEY="${SCRAPPEY_API_KEY:-YOUR_API_KEY}"
API_URL="https://publisher.scrappey.com/api/v1"

echo "Scrappey cURL Examples"
echo "=================================================="

# =============================================================================
# Basic GET Request
# =============================================================================
echo ""
echo "=== Basic GET Request ==="
echo ""

curl -s -X POST "${API_URL}?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.get",
    "url": "https://httpbin.org/get"
  }' | jq -r '.data, .solution.statusCode'

# =============================================================================
# POST Request with Form Data
# =============================================================================
echo ""
echo "=== POST Request with Form Data ==="
echo ""

curl -s -X POST "${API_URL}?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.post",
    "url": "https://httpbin.org/post",
    "postData": "username=test&password=test123"
  }' | jq -r '.data, .solution.statusCode'

# =============================================================================
# POST Request with JSON Data
# =============================================================================
echo ""
echo "=== POST Request with JSON Data ==="
echo ""

curl -s -X POST "${API_URL}?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.post",
    "url": "https://httpbin.org/post",
    "postData": "{\"key\": \"value\", \"number\": 42}",
    "customHeaders": {
      "Content-Type": "application/json"
    }
  }' | jq -r '.data, .solution.statusCode'

# =============================================================================
# Create Session
# =============================================================================
echo ""
echo "=== Create Session ==="
echo ""

SESSION_RESPONSE=$(curl -s -X POST "${API_URL}?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "sessions.create",
    "proxyCountry": "UnitedStates",
    "premiumProxy": true
  }')

SESSION_ID=$(echo "$SESSION_RESPONSE" | jq -r '.session')
echo "Created session: $SESSION_ID"

# =============================================================================
# Request with Session
# =============================================================================
echo ""
echo "=== Request with Session ==="
echo ""

curl -s -X POST "${API_URL}?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"cmd\": \"request.get\",
    \"url\": \"https://httpbin.org/get\",
    \"session\": \"${SESSION_ID}\"
  }" | jq -r '.data, .solution.statusCode'

# =============================================================================
# Destroy Session
# =============================================================================
echo ""
echo "=== Destroy Session ==="
echo ""

curl -s -X POST "${API_URL}?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{
    \"cmd\": \"sessions.destroy\",
    \"session\": \"${SESSION_ID}\"
  }" | jq -r '.data'

echo "Destroyed session: $SESSION_ID"

# =============================================================================
# Cloudflare Bypass
# =============================================================================
echo ""
echo "=== Cloudflare Bypass Example ==="
echo ""

curl -s -X POST "${API_URL}?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.get",
    "url": "https://example.com",
    "cloudflareBypass": true,
    "premiumProxy": true,
    "proxyCountry": "UnitedStates"
  }' | jq -r '.data, .solution.statusCode'

# =============================================================================
# Browser Actions
# =============================================================================
echo ""
echo "=== Browser Actions Example ==="
echo ""

curl -s -X POST "${API_URL}?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.get",
    "url": "https://example.com",
    "browserActions": [
      {"type": "wait_for_selector", "cssSelector": "body"},
      {"type": "execute_js", "code": "document.title"},
      {"type": "wait", "wait": 1000}
    ]
  }' | jq -r '.data, .solution.javascriptReturn'

# =============================================================================
# Screenshot
# =============================================================================
echo ""
echo "=== Screenshot Example ==="
echo ""

SCREENSHOT_RESPONSE=$(curl -s -X POST "${API_URL}?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.get",
    "url": "https://example.com",
    "screenshot": true,
    "screenshotWidth": 1920,
    "screenshotHeight": 1080
  }')

# Check if screenshot was captured
if echo "$SCREENSHOT_RESPONSE" | jq -e '.solution.screenshot' > /dev/null 2>&1; then
  echo "$SCREENSHOT_RESPONSE" | jq -r '.solution.screenshot' | base64 -d > screenshot.png
  echo "Screenshot saved to screenshot.png"
else
  echo "No screenshot in response"
fi

# =============================================================================
# Captcha Solving
# =============================================================================
echo ""
echo "=== Captcha Solving Example ==="
echo ""

curl -s -X POST "${API_URL}?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.get",
    "url": "https://example.com",
    "automaticallySolveCaptchas": true,
    "alwaysLoad": ["recaptcha", "hcaptcha", "turnstile"]
  }' | jq -r '.data, .solution.captchaSolveResult'

# =============================================================================
# List Sessions
# =============================================================================
echo ""
echo "=== List Sessions ==="
echo ""

curl -s -X POST "${API_URL}?key=${API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "sessions.list"
  }' | jq -r '.open, .limit'

echo ""
echo "✓ All examples completed!"
echo ""
