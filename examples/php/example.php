<?php
/**
 * Scrappey - PHP Example
 *
 * This example demonstrates how to use the Scrappey API from PHP
 * for web scraping with Cloudflare bypass and browser automation.
 *
 * Prerequisites:
 *   PHP 8.0+ with curl extension
 *
 * Run:
 *   php example.php
 *
 * Get your API key at: https://app.scrappey.com
 */

$API_KEY = getenv('SCRAPPEY_API_KEY') ?: 'YOUR_API_KEY';
$API_URL = 'https://publisher.scrappey.com/api/v1';

/**
 * Send a request to the Scrappey API
 */
function scrappeyRequest(string $cmd, array $data = []): array {
    global $API_KEY, $API_URL;

    $payload = array_merge(['cmd' => $cmd], $data);

    $ch = curl_init();
    curl_setopt_array($ch, [
        CURLOPT_URL => $API_URL . '?key=' . $API_KEY,
        CURLOPT_POST => true,
        CURLOPT_POSTFIELDS => json_encode($payload),
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_TIMEOUT => 300,
    ]);

    $response = curl_exec($ch);
    $error = curl_error($ch);
    curl_close($ch);

    if ($error) {
        throw new Exception("cURL error: $error");
    }

    return json_decode($response, true) ?? throw new Exception("Failed to parse response");
}

/**
 * Basic example: Simple GET request
 */
function basicExample(): void {
    echo "\n=== Basic Example ===\n\n";

    $result = scrappeyRequest('request.get', [
        'url' => 'https://httpbin.org/get',
    ]);

    if ($result['data'] === 'success') {
        echo "Status: {$result['solution']['statusCode']}\n";
        $preview = substr($result['solution']['response'], 0, 200) . '...';
        echo "Response: $preview\n";
    } else {
        echo "Error: {$result['error']}\n";
    }
}

/**
 * Session example: Maintain cookies across requests
 */
function sessionExample(): void {
    echo "\n=== Session Example ===\n\n";

    // Create session
    $sessionResult = scrappeyRequest('sessions.create', [
        'proxyCountry' => 'UnitedStates',
        'premiumProxy' => true,
    ]);

    $sessionId = $sessionResult['session'];
    echo "Created session: $sessionId\n";

    try {
        // Set cookie
        scrappeyRequest('request.get', [
            'url' => 'https://httpbin.org/cookies/set/test/value123',
            'session' => $sessionId,
        ]);

        // Verify cookie persists
        $result = scrappeyRequest('request.get', [
            'url' => 'https://httpbin.org/cookies',
            'session' => $sessionId,
        ]);
        echo "Cookies: {$result['solution']['response']}\n";

    } finally {
        // Destroy session
        scrappeyRequest('sessions.destroy', [
            'session' => $sessionId,
        ]);
        echo "Destroyed session: $sessionId\n";
    }
}

/**
 * Browser actions example
 */
function browserActionsExample(): void {
    echo "\n=== Browser Actions Example ===\n\n";

    $result = scrappeyRequest('request.get', [
        'url' => 'https://example.com',
        'browserActions' => [
            ['type' => 'wait_for_selector', 'cssSelector' => 'body'],
            ['type' => 'execute_js', 'code' => 'document.title'],
            ['type' => 'scroll', 'cssSelector' => 'footer'],
        ],
    ]);

    if ($result['data'] === 'success') {
        echo "Page loaded, status: {$result['solution']['statusCode']}\n";
        if (isset($result['solution']['javascriptReturn'])) {
            echo "JS Return: " . json_encode($result['solution']['javascriptReturn']) . "\n";
        }
    } else {
        echo "Error: {$result['error']}\n";
    }
}

/**
 * POST request example
 */
function postExample(): void {
    echo "\n=== POST Example ===\n\n";

    // Form data
    $result = scrappeyRequest('request.post', [
        'url' => 'https://httpbin.org/post',
        'postData' => 'username=test&password=test123',
    ]);
    echo "Form POST status: {$result['solution']['statusCode']}\n";

    // JSON data
    $result = scrappeyRequest('request.post', [
        'url' => 'https://httpbin.org/post',
        'postData' => json_encode(['key' => 'value', 'number' => 42]),
        'customHeaders' => ['Content-Type' => 'application/json'],
    ]);
    echo "JSON POST status: {$result['solution']['statusCode']}\n";
}

/**
 * Cloudflare bypass example
 */
function cloudflareExample(): void {
    echo "\n=== Cloudflare Bypass Example ===\n\n";

    $result = scrappeyRequest('request.get', [
        'url' => 'https://example-protected-site.com',
        'cloudflareBypass' => true,
        'premiumProxy' => true,
        'proxyCountry' => 'UnitedStates',
    ]);

    if ($result['data'] === 'success') {
        echo "Successfully bypassed! Status: {$result['solution']['statusCode']}\n";
    } else {
        echo "Error: {$result['error']}\n";
    }
}

/**
 * Screenshot example
 */
function screenshotExample(): void {
    echo "\n=== Screenshot Example ===\n\n";

    $result = scrappeyRequest('request.get', [
        'url' => 'https://example.com',
        'screenshot' => true,
        'screenshotWidth' => 1920,
        'screenshotHeight' => 1080,
    ]);

    if ($result['data'] === 'success' && !empty($result['solution']['screenshot'])) {
        $imageData = base64_decode($result['solution']['screenshot']);
        file_put_contents('screenshot.png', $imageData);
        echo "Screenshot saved to screenshot.png\n";
    } else {
        echo "Error: " . ($result['error'] ?? 'No screenshot returned') . "\n";
    }
}

/**
 * Captcha solving example
 */
function captchaSolvingExample(): void {
    echo "\n=== Captcha Solving Example ===\n\n";

    $result = scrappeyRequest('request.get', [
        'url' => 'https://example.com/protected',
        'automaticallySolveCaptchas' => true,
        'alwaysLoad' => ['recaptcha', 'hcaptcha', 'turnstile'],
    ]);

    if ($result['data'] === 'success') {
        echo "Captcha result: " . json_encode($result['solution']['captchaSolveResult'] ?? null) . "\n";
        echo "Response length: " . strlen($result['solution']['response']) . "\n";
    } else {
        echo "Error: {$result['error']}\n";
    }
}

// Main execution
echo "Scrappey PHP Examples\n";
echo str_repeat('=', 50) . "\n";

try {
    basicExample();
    sessionExample();
    postExample();
    // Uncomment to run additional examples:
    // browserActionsExample();
    // cloudflareExample();
    // screenshotExample();
    // captchaSolvingExample();

    echo "\n✓ All examples completed!\n\n";

} catch (Exception $e) {
    echo "Error: " . $e->getMessage() . "\n";
    exit(1);
}
