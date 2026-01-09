"""
Type definitions for Scrappey API.

This module provides TypedDict definitions for all API request and response types,
making the API self-documenting and compatible with static type checkers.
"""

from typing import Any, Dict, List, Literal, Optional, TypedDict, Union


# ============================================================================
# Browser Action Types
# ============================================================================

class ClickAction(TypedDict, total=False):
    """Click on an element using CSS selector."""
    type: Literal["click"]
    cssSelector: str
    wait: int
    waitForSelector: str
    direct: bool
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool
    timeout: int


class TypeAction(TypedDict, total=False):
    """Type text into an input field."""
    type: Literal["type"]
    cssSelector: str
    text: str
    wait: int
    direct: bool
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool
    timeout: int


class GotoAction(TypedDict, total=False):
    """Navigate to a URL."""
    type: Literal["goto"]
    url: str
    wait: int
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool
    timeout: int


class WaitAction(TypedDict, total=False):
    """Wait for a specified time."""
    type: Literal["wait"]
    wait: int
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool
    timeout: int


class WaitForSelectorAction(TypedDict, total=False):
    """Wait for an element to appear."""
    type: Literal["wait_for_selector"]
    cssSelector: str
    timeout: int
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool


class WaitForFunctionAction(TypedDict, total=False):
    """Wait until a JavaScript expression returns truthy."""
    type: Literal["wait_for_function"]
    code: str
    timeout: int
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool


class WaitForLoadStateAction(TypedDict, total=False):
    """Wait for a specific page load state."""
    type: Literal["wait_for_load_state"]
    waitForLoadState: Literal["domcontentloaded", "networkidle", "load"]
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool
    timeout: int


class WaitForCookieAction(TypedDict, total=False):
    """Wait for a specific cookie to be set."""
    type: Literal["wait_for_cookie"]
    cookieName: str
    cookieValue: str
    cookieDomain: str
    pollIntervalMs: int
    timeout: int
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool


class ExecuteJsAction(TypedDict, total=False):
    """Execute JavaScript code on the page."""
    type: Literal["execute_js"]
    code: str
    dontReturnValue: bool
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool
    timeout: int


class ScrollAction(TypedDict, total=False):
    """Scroll to an element or the bottom of the page."""
    type: Literal["scroll"]
    cssSelector: str
    repeat: int
    delayMs: int
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool
    timeout: int


class HoverAction(TypedDict, total=False):
    """Hover the mouse over an element."""
    type: Literal["hover"]
    cssSelector: str
    timeout: int
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool


class KeyboardAction(TypedDict, total=False):
    """Simulate keyboard key presses."""
    type: Literal["keyboard"]
    value: Literal[
        "tab", "enter", "space", "arrowdown", "arrowup",
        "arrowleft", "arrowright", "backspace", "clear"
    ]
    cssSelector: str
    wait: int
    waitForSelector: str
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool
    timeout: int


class DropdownAction(TypedDict, total=False):
    """Select an option from a dropdown."""
    type: Literal["dropdown"]
    cssSelector: str
    index: int
    value: str
    wait: int
    waitForSelector: str
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool
    timeout: int


class SwitchIframeAction(TypedDict, total=False):
    """Switch context to an iframe."""
    type: Literal["switch_iframe"]
    cssSelector: str
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool
    timeout: int


class SetViewportAction(TypedDict, total=False):
    """Change the browser viewport size."""
    type: Literal["set_viewport"]
    width: int
    height: int
    wait: int
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool
    timeout: int


class IfAction(TypedDict, total=False):
    """Execute actions conditionally."""
    type: Literal["if"]
    condition: str
    then: List["BrowserAction"]
    or_: List["BrowserAction"]  # 'or' is reserved in Python
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool
    timeout: int


class WhileAction(TypedDict, total=False):
    """Loop actions while a condition is true."""
    type: Literal["while"]
    condition: str
    then: List["BrowserAction"]
    maxAttempts: int
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool
    timeout: int


class CaptchaData(TypedDict, total=False):
    """Additional captcha data."""
    sitekey: str
    action: str
    pageAction: str
    invisible: bool
    base64Image: str
    cssSelector: str
    reset: bool
    fast: bool


class SolveCaptchaAction(TypedDict, total=False):
    """Solve various captcha types."""
    type: Literal["solve_captcha"]
    captcha: Literal[
        "turnstile", "recaptcha", "recaptchav2", "recaptchav3",
        "hcaptcha", "hcaptcha_inside", "hcaptcha_enterprise_inside",
        "funcaptcha", "perimeterx", "mtcaptcha", "mtcaptchaisolated",
        "v4guard", "custom", "fingerprintjscom", "fingerprintjs_curseforge"
    ]
    captchaData: CaptchaData
    websiteUrl: str
    websiteKey: str
    cssSelector: str
    inputSelector: str
    clickSelector: str
    iframeSelector: str
    coreName: str
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool
    timeout: int


class DiscordLoginAction(TypedDict, total=False):
    """Log into Discord using a token."""
    type: Literal["discord_login"]
    token: str
    direct: bool
    wait: int
    timeout: int
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool


class RemoveIframesAction(TypedDict, total=False):
    """Remove all iframes from the page."""
    type: Literal["remove_iframes"]
    when: Literal["beforeload", "afterload"]
    ignoreErrors: bool
    timeout: int


# Union of all browser actions
BrowserAction = Union[
    ClickAction, TypeAction, GotoAction, WaitAction, WaitForSelectorAction,
    WaitForFunctionAction, WaitForLoadStateAction, WaitForCookieAction,
    ExecuteJsAction, ScrollAction, HoverAction, KeyboardAction, DropdownAction,
    SwitchIframeAction, SetViewportAction, IfAction, WhileAction,
    SolveCaptchaAction, DiscordLoginAction, RemoveIframesAction,
    Dict[str, Any]  # Allow arbitrary actions for forward compatibility
]


# ============================================================================
# Cookie Types
# ============================================================================

class Cookie(TypedDict, total=False):
    """Cookie object."""
    key: str
    value: str
    domain: str
    path: str
    expires: int
    httpOnly: bool
    secure: bool
    sameSite: Literal["Strict", "Lax", "None"]


class CookieJarItem(TypedDict, total=False):
    """Cookie jar item for setting cookies."""
    key: str
    value: str
    domain: str
    path: str


# ============================================================================
# Browser Configuration Types
# ============================================================================

class BrowserSpec(TypedDict, total=False):
    """Browser specification."""
    name: Literal["firefox", "chrome", "safari"]
    minVersion: int
    maxVersion: int


# ============================================================================
# Request Options
# ============================================================================

class RequestOptions(TypedDict, total=False):
    """
    Options for all Scrappey API requests.
    
    This is the main configuration object that can be passed to get(), post(),
    and other request methods. All fields are optional.
    """
    # Required
    url: str
    
    # Session
    session: str
    closeAfterUse: bool
    
    # Request settings
    referer: str
    postData: Union[str, Dict[str, Any]]
    requestType: Literal["browser", "request"]
    onlyStatusCode: bool
    method: str
    customHeaders: Dict[str, str]
    cookies: str
    cookiejar: List[CookieJarItem]
    localStorage: Dict[str, str]
    
    # Browser configuration
    browser: List[BrowserSpec]
    userAgent: str
    device: Dict[str, Any]
    operatingSystem: Dict[str, Any]
    locales: List[str]
    setLocale: bool
    headful: bool
    devTools: bool
    showBrowser: bool
    
    # Proxy settings
    proxy: str
    proxyCountry: str
    noProxy: bool
    premiumProxy: bool
    mobileProxy: bool
    dontChangeProxy: bool
    
    # Antibot bypass options
    cloudflareBypass: bool
    datadomeBypass: bool
    datadomeDebug: bool
    kasadaBypass: bool
    disableAntiBot: bool
    detectIncapsula: bool
    spsnspidChallenge: bool
    
    # Captcha solving
    automaticallySolveCaptchas: bool
    alwaysLoad: List[Literal["recaptcha", "hcaptcha", "turnstile"]]
    captchaAnswer: str
    captchaSuccessIntercept: str
    
    # Browser actions
    browserActions: List[BrowserAction]
    waitForSpecificActionOnSite: bool
    mouseMovements: bool
    forceMouseMovement: bool
    
    # Response data options
    cssSelector: str
    innerText: bool
    includeImages: bool
    includeLinks: bool
    regex: Union[str, List[str]]
    screenshot: bool
    screenshotUpload: bool
    screenshotWidth: int
    screenshotHeight: int
    video: bool
    base64: bool
    base64Response: bool
    binary: bool
    pdf: bool
    filter: List[str]
    
    # Request interception
    interceptFetchRequest: Union[str, List[str]]
    abortOnDetection: List[str]
    abortOnPostRequest: bool
    waitForAbortOnDetection: bool
    waitForAbortOnDetectionTimeout: int
    whitelistedDomains: List[str]
    blackListedDomains: List[str]
    neverCacheDomains: List[str]
    dontLoadMainSite: bool
    dontLoadFirstRequest: bool
    
    # Advanced options
    javascriptReturn: List[Any]
    autoparse: bool
    structure: Dict[str, Any]
    model: str
    api_key: str
    fullPageLoad: bool
    dontWaitOnPageLoad: bool
    waitForUrl: str
    listAllRedirects: bool
    removeIframes: bool
    blockCookieBanners: bool
    legacy: bool
    websocket: bool
    forceUniqueFingerprint: bool
    webrtcIpv4: str
    webrtcIpv6: str
    retries: int
    timeout: int


# ============================================================================
# Session Types
# ============================================================================

class SessionCreateOptions(TypedDict, total=False):
    """Options for creating a session."""
    session: str
    proxy: str
    proxyCountry: str
    premiumProxy: bool
    mobileProxy: bool
    browser: List[BrowserSpec]
    userAgent: str
    locales: List[str]


class SessionInfo(TypedDict, total=False):
    """Session information from list response."""
    session: str
    lastAccessed: int


# ============================================================================
# Response Types
# ============================================================================

class IpInfo(TypedDict, total=False):
    """IP information and geolocation."""
    ip: str
    country: str
    city: str
    region: str
    timezone: str
    isp: str


class AntibotProviders(TypedDict, total=False):
    """Detected antibot providers."""
    providers: List[str]
    confidence: Dict[str, int]
    primaryProvider: str


class CaptchaSolveResult(TypedDict, total=False):
    """Captcha solving result."""
    type: str
    status: str
    timeTaken: int


class Solution(TypedDict, total=False):
    """
    Solution object returned by Scrappey API.
    
    This contains all the data extracted from the request.
    """
    verified: bool
    type: Literal["browser", "request"]
    response: str
    statusCode: int
    currentUrl: str
    userAgent: str
    cookies: List[Cookie]
    cookieString: str
    responseHeaders: Dict[str, str]
    requestHeaders: Dict[str, str]
    requestBody: str
    method: str
    ipInfo: IpInfo
    innerText: str
    localStorageData: Dict[str, str]
    screenshot: str
    screenshotUrl: str
    videoUrl: str
    interceptFetchRequestResponse: Union[Dict[str, Any], List[Dict[str, Any]]]
    javascriptReturn: List[Any]
    base64Response: str
    listAllRedirectsResponse: List[str]
    additionalCost: float
    wsEndpoint: str
    detectedAntibotProviders: AntibotProviders
    captchaSolveResult: CaptchaSolveResult
    autoparse: Dict[str, Any]
    abortOnDetectionResponse: List[Dict[str, Any]]


class ScrappeyResponse(TypedDict, total=False):
    """
    Standard response from Scrappey API.
    
    All API calls return this structure.
    """
    solution: Solution
    timeElapsed: int
    data: Literal["success", "error"]
    session: str
    error: str
    info: str


class SessionCreateResponse(TypedDict, total=False):
    """Response from session creation."""
    solution: Solution
    data: Literal["success", "error"]
    session: str
    fingerprint: Dict[str, Any]
    context: Dict[str, Any]
    error: str


class SessionListResponse(TypedDict, total=False):
    """Response from session list."""
    sessions: List[SessionInfo]
    open: int
    limit: int
    timeElapsed: int


class SessionActiveResponse(TypedDict, total=False):
    """Response from session active check."""
    active: bool


# ============================================================================
# Command Types
# ============================================================================

Command = Literal[
    "request.get",
    "request.post",
    "request.put",
    "request.delete",
    "request.patch",
    "request.publish",
    "sessions.create",
    "sessions.destroy",
    "sessions.list",
    "sessions.active",
    "websocket.create",
]
