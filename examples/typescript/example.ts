/**
 * Scrappey - TypeScript Example
 *
 * This example demonstrates how to use the Scrappey API from TypeScript
 * with full type definitions.
 *
 * Prerequisites:
 *   npm install
 *   npx ts-node example.ts
 *
 * Get your API key at: https://app.scrappey.com
 */

const API_KEY: string = process.env.SCRAPPEY_API_KEY || 'YOUR_API_KEY';
const API_URL: string = 'https://publisher.scrappey.com/api/v1';

// Type definitions
interface Cookie {
    key: string;
    value: string;
    domain: string;
    path: string;
}

interface Solution {
    verified: boolean;
    response: string;
    statusCode: number;
    currentUrl: string;
    userAgent: string;
    cookies: Cookie[];
    cookieString: string;
    screenshot?: string;
    screenshotUrl?: string;
    javascriptReturn?: any[];
    detectedAntibotProviders?: {
        providers: string[];
        primaryProvider: string;
    };
    captchaSolveResult?: {
        type: string;
        status: string;
        timeTaken: number;
    };
}

interface ScrappeyResponse {
    solution: Solution;
    timeElapsed: number;
    data: 'success' | 'error';
    session: string;
    error?: string;
}

interface SessionListResponse {
    sessions: { session: string; lastAccessed: number }[];
    open: number;
    limit: number;
}

interface BrowserAction {
    type: string;
    cssSelector?: string;
    text?: string;
    url?: string;
    wait?: number;
    waitForSelector?: string;
    code?: string;
    timeout?: number;
}

interface RequestOptions {
    url: string;
    session?: string;
    proxy?: string;
    proxyCountry?: string;
    premiumProxy?: boolean;
    mobileProxy?: boolean;
    browserActions?: BrowserAction[];
    automaticallySolveCaptchas?: boolean;
    cloudflareBypass?: boolean;
    datadomeBypass?: boolean;
    kasadaBypass?: boolean;
    screenshot?: boolean;
    screenshotWidth?: number;
    screenshotHeight?: number;
    cssSelector?: string;
    innerText?: boolean;
    postData?: string | Record<string, any>;
    customHeaders?: Record<string, string>;
}

/**
 * Send a request to the Scrappey API
 */
async function scrappeyRequest<T = ScrappeyResponse>(
    cmd: string,
    data: Record<string, any> = {}
): Promise<T> {
    const response = await fetch(`${API_URL}?key=${API_KEY}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cmd, ...data }),
    });

    if (!response.ok) {
        throw new Error(`HTTP error: ${response.status}`);
    }

    return response.json() as Promise<T>;
}

/**
 * Scrappey client class with typed methods
 */
class Scrappey {
    async get(options: RequestOptions): Promise<ScrappeyResponse> {
        return scrappeyRequest('request.get', options);
    }

    async post(options: RequestOptions): Promise<ScrappeyResponse> {
        return scrappeyRequest('request.post', options);
    }

    async createSession(options: Partial<RequestOptions> = {}): Promise<ScrappeyResponse> {
        return scrappeyRequest('sessions.create', options);
    }

    async destroySession(session: string): Promise<ScrappeyResponse> {
        return scrappeyRequest('sessions.destroy', { session });
    }

    async listSessions(): Promise<SessionListResponse> {
        return scrappeyRequest<SessionListResponse>('sessions.list', {});
    }
}

// Examples

async function basicExample(): Promise<void> {
    console.log('\n=== Basic Example ===\n');

    const scrappey = new Scrappey();
    const result = await scrappey.get({ url: 'https://httpbin.org/get' });

    if (result.data === 'success') {
        console.log(`Status: ${result.solution.statusCode}`);
        console.log(`User Agent: ${result.solution.userAgent}`);
        console.log(`Response length: ${result.solution.response.length}`);
    } else {
        console.log(`Error: ${result.error}`);
    }
}

async function sessionExample(): Promise<void> {
    console.log('\n=== Session Example ===\n');

    const scrappey = new Scrappey();

    // Create session with type safety
    const sessionData = await scrappey.createSession({
        proxyCountry: 'UnitedStates',
        premiumProxy: true,
    });
    const sessionId: string = sessionData.session;
    console.log(`Created session: ${sessionId}`);

    try {
        // Use session
        const result = await scrappey.get({
            url: 'https://httpbin.org/get',
            session: sessionId,
        });
        console.log(`Request status: ${result.solution.statusCode}`);

        // List sessions
        const sessions = await scrappey.listSessions();
        console.log(`Open sessions: ${sessions.open}/${sessions.limit}`);

    } finally {
        await scrappey.destroySession(sessionId);
        console.log(`Destroyed session: ${sessionId}`);
    }
}

async function browserActionsExample(): Promise<void> {
    console.log('\n=== Browser Actions Example ===\n');

    const scrappey = new Scrappey();

    const actions: BrowserAction[] = [
        { type: 'wait_for_selector', cssSelector: 'body' },
        { type: 'execute_js', code: 'document.title' },
        { type: 'scroll', cssSelector: 'footer' },
    ];

    const result = await scrappey.get({
        url: 'https://example.com',
        browserActions: actions,
    });

    if (result.data === 'success') {
        console.log(`Page title: ${result.solution.javascriptReturn?.[0]}`);
    }
}

async function typedResponseExample(): Promise<void> {
    console.log('\n=== Typed Response Example ===\n');

    const scrappey = new Scrappey();

    const result = await scrappey.get({
        url: 'https://httpbin.org/get',
        screenshot: true,
    });

    // TypeScript knows the shape of the response
    const { solution } = result;
    
    console.log(`Verified: ${solution.verified}`);
    console.log(`Status Code: ${solution.statusCode}`);
    console.log(`Current URL: ${solution.currentUrl}`);
    console.log(`Cookies count: ${solution.cookies.length}`);
    console.log(`Has screenshot: ${!!solution.screenshot}`);
}

// Main execution
async function main(): Promise<void> {
    console.log('Scrappey TypeScript Examples');
    console.log('='.repeat(50));

    try {
        await basicExample();
        await sessionExample();
        await typedResponseExample();
        // await browserActionsExample();

        console.log('\n✓ All examples completed!\n');

    } catch (error) {
        console.error(`Error: ${error instanceof Error ? error.message : error}`);
        process.exit(1);
    }
}

main();
