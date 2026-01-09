/**
 * Scrappey - Node.js Example
 *
 * This example demonstrates how to use the Scrappey API from Node.js
 * for web scraping with Cloudflare bypass and browser automation.
 *
 * Prerequisites:
 *   npm install
 *
 * Get your API key at: https://app.scrappey.com
 */

const API_KEY = process.env.SCRAPPEY_API_KEY || 'YOUR_API_KEY';
const API_URL = 'https://publisher.scrappey.com/api/v1';

/**
 * Send a request to the Scrappey API
 */
async function scrappeyRequest(cmd, data = {}) {
    const response = await fetch(`${API_URL}?key=${API_KEY}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cmd, ...data }),
    });

    if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
    }

    return response.json();
}

/**
 * Basic example: Simple GET request
 */
async function basicExample() {
    console.log('\n=== Basic Example ===\n');

    const result = await scrappeyRequest('request.get', {
        url: 'https://httpbin.org/get',
    });

    if (result.data === 'success') {
        console.log(`Status: ${result.solution.statusCode}`);
        console.log(`Response: ${result.solution.response.substring(0, 200)}...`);
    } else {
        console.log(`Error: ${result.error}`);
    }
}

/**
 * Session example: Maintain cookies across requests
 */
async function sessionExample() {
    console.log('\n=== Session Example ===\n');

    // Create session
    const sessionData = await scrappeyRequest('sessions.create', {
        proxyCountry: 'UnitedStates',
    });
    const sessionId = sessionData.session;
    console.log(`Created session: ${sessionId}`);

    try {
        // Set a cookie
        await scrappeyRequest('request.get', {
            url: 'https://httpbin.org/cookies/set/test/value123',
            session: sessionId,
        });

        // Verify cookie persists
        const result = await scrappeyRequest('request.get', {
            url: 'https://httpbin.org/cookies',
            session: sessionId,
        });
        console.log(`Cookies: ${result.solution.response}`);

    } finally {
        // Clean up
        await scrappeyRequest('sessions.destroy', { session: sessionId });
        console.log(`Destroyed session: ${sessionId}`);
    }
}

/**
 * Cloudflare bypass example
 */
async function cloudflareExample() {
    console.log('\n=== Cloudflare Bypass Example ===\n');

    const result = await scrappeyRequest('request.get', {
        url: 'https://example-protected-site.com',
        cloudflareBypass: true,
        premiumProxy: true,
        proxyCountry: 'UnitedStates',
    });

    if (result.data === 'success') {
        console.log(`Successfully bypassed! Status: ${result.solution.statusCode}`);
        console.log(`Detected providers: ${JSON.stringify(result.solution.detectedAntibotProviders)}`);
    } else {
        console.log(`Error: ${result.error}`);
    }
}

/**
 * Browser automation example
 */
async function browserActionsExample() {
    console.log('\n=== Browser Actions Example ===\n');

    const result = await scrappeyRequest('request.get', {
        url: 'https://example.com/login',
        browserActions: [
            { type: 'wait_for_selector', cssSelector: '#login-form' },
            { type: 'type', cssSelector: '#email', text: 'user@example.com' },
            { type: 'type', cssSelector: '#password', text: 'password123' },
            { type: 'click', cssSelector: '#submit-btn', waitForSelector: '.dashboard' },
            { type: 'execute_js', code: 'document.querySelector(".user-name").innerText' },
        ],
    });

    if (result.data === 'success') {
        console.log('Login successful!');
        console.log(`JavaScript return: ${result.solution.javascriptReturn}`);
    } else {
        console.log(`Error: ${result.error}`);
    }
}

/**
 * Screenshot example
 */
async function screenshotExample() {
    console.log('\n=== Screenshot Example ===\n');

    const result = await scrappeyRequest('request.get', {
        url: 'https://example.com',
        screenshot: true,
        screenshotWidth: 1920,
        screenshotHeight: 1080,
    });

    if (result.data === 'success' && result.solution.screenshot) {
        const fs = await import('fs');
        const buffer = Buffer.from(result.solution.screenshot, 'base64');
        fs.writeFileSync('screenshot.png', buffer);
        console.log('Screenshot saved to screenshot.png');
    } else {
        console.log(`Error: ${result.error}`);
    }
}

/**
 * Captcha solving example
 */
async function captchaSolvingExample() {
    console.log('\n=== Captcha Solving Example ===\n');

    const result = await scrappeyRequest('request.get', {
        url: 'https://example.com/protected',
        automaticallySolveCaptchas: true,
        alwaysLoad: ['recaptcha', 'hcaptcha', 'turnstile'],
    });

    if (result.data === 'success') {
        console.log(`Captcha solve result: ${JSON.stringify(result.solution.captchaSolveResult)}`);
        console.log(`Page content length: ${result.solution.response.length}`);
    } else {
        console.log(`Error: ${result.error}`);
    }
}

/**
 * POST request example
 */
async function postExample() {
    console.log('\n=== POST Request Example ===\n');

    // Form data
    const formResult = await scrappeyRequest('request.post', {
        url: 'https://httpbin.org/post',
        postData: 'username=test&password=test123',
    });
    console.log(`Form POST status: ${formResult.solution?.statusCode}`);

    // JSON data
    const jsonResult = await scrappeyRequest('request.post', {
        url: 'https://httpbin.org/post',
        postData: JSON.stringify({ key: 'value', number: 42 }),
        customHeaders: { 'Content-Type': 'application/json' },
    });
    console.log(`JSON POST status: ${jsonResult.solution?.statusCode}`);
}

// Main execution
async function main() {
    console.log('Scrappey Node.js Examples');
    console.log('='.repeat(50));

    try {
        await basicExample();
        await sessionExample();
        await postExample();
        // Uncomment to run additional examples:
        // await cloudflareExample();
        // await browserActionsExample();
        // await screenshotExample();
        // await captchaSolvingExample();

        console.log('\n✓ All examples completed!\n');

    } catch (error) {
        console.error(`Error: ${error.message}`);
        process.exit(1);
    }
}

main();
