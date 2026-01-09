// Scrappey - Go Example
//
// This example demonstrates how to use the Scrappey API from Go
// for web scraping with Cloudflare bypass and browser automation.
//
// Prerequisites:
//   go mod init scrappey-example
//   go run example.go
//
// Get your API key at: https://app.scrappey.com

package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
)

var (
	apiKey = getEnv("SCRAPPEY_API_KEY", "YOUR_API_KEY")
	apiURL = "https://publisher.scrappey.com/api/v1"
)

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

// Cookie represents a browser cookie
type Cookie struct {
	Key    string `json:"key"`
	Value  string `json:"value"`
	Domain string `json:"domain"`
	Path   string `json:"path"`
}

// Solution contains the scraped data
type Solution struct {
	Verified      bool     `json:"verified"`
	Response      string   `json:"response"`
	StatusCode    int      `json:"statusCode"`
	CurrentURL    string   `json:"currentUrl"`
	UserAgent     string   `json:"userAgent"`
	Cookies       []Cookie `json:"cookies"`
	CookieString  string   `json:"cookieString"`
	Screenshot    string   `json:"screenshot,omitempty"`
	ScreenshotURL string   `json:"screenshotUrl,omitempty"`
}

// ScrappeyResponse is the API response structure
type ScrappeyResponse struct {
	Solution    Solution `json:"solution"`
	TimeElapsed int      `json:"timeElapsed"`
	Data        string   `json:"data"`
	Session     string   `json:"session"`
	Error       string   `json:"error,omitempty"`
}

// SessionListResponse contains session list data
type SessionListResponse struct {
	Sessions []struct {
		Session      string `json:"session"`
		LastAccessed int64  `json:"lastAccessed"`
	} `json:"sessions"`
	Open  int `json:"open"`
	Limit int `json:"limit"`
}

// BrowserAction defines a browser automation action
type BrowserAction struct {
	Type            string `json:"type"`
	CSSSelector     string `json:"cssSelector,omitempty"`
	Text            string `json:"text,omitempty"`
	URL             string `json:"url,omitempty"`
	Wait            int    `json:"wait,omitempty"`
	WaitForSelector string `json:"waitForSelector,omitempty"`
	Code            string `json:"code,omitempty"`
}

// RequestOptions contains all request parameters
type RequestOptions struct {
	Cmd                        string                 `json:"cmd"`
	URL                        string                 `json:"url,omitempty"`
	Session                    string                 `json:"session,omitempty"`
	Proxy                      string                 `json:"proxy,omitempty"`
	ProxyCountry               string                 `json:"proxyCountry,omitempty"`
	PremiumProxy               bool                   `json:"premiumProxy,omitempty"`
	MobileProxy                bool                   `json:"mobileProxy,omitempty"`
	BrowserActions             []BrowserAction        `json:"browserActions,omitempty"`
	AutomaticallySolveCaptchas bool                   `json:"automaticallySolveCaptchas,omitempty"`
	CloudflareBypass           bool                   `json:"cloudflareBypass,omitempty"`
	DatadomeBypass             bool                   `json:"datadomeBypass,omitempty"`
	KasadaBypass               bool                   `json:"kasadaBypass,omitempty"`
	Screenshot                 bool                   `json:"screenshot,omitempty"`
	ScreenshotWidth            int                    `json:"screenshotWidth,omitempty"`
	ScreenshotHeight           int                    `json:"screenshotHeight,omitempty"`
	PostData                   interface{}            `json:"postData,omitempty"`
	CustomHeaders              map[string]string      `json:"customHeaders,omitempty"`
}

// scrappeyRequest sends a request to the Scrappey API
func scrappeyRequest(options RequestOptions) (*ScrappeyResponse, error) {
	body, err := json.Marshal(options)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	url := fmt.Sprintf("%s?key=%s", apiURL, apiKey)
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(body))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("request failed: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	var result ScrappeyResponse
	if err := json.Unmarshal(respBody, &result); err != nil {
		return nil, fmt.Errorf("failed to parse response: %w", err)
	}

	return &result, nil
}

func basicExample() error {
	fmt.Println("\n=== Basic Example ===\n")

	result, err := scrappeyRequest(RequestOptions{
		Cmd: "request.get",
		URL: "https://httpbin.org/get",
	})
	if err != nil {
		return err
	}

	if result.Data == "success" {
		fmt.Printf("Status: %d\n", result.Solution.StatusCode)
		responsePreview := result.Solution.Response
		if len(responsePreview) > 200 {
			responsePreview = responsePreview[:200] + "..."
		}
		fmt.Printf("Response: %s\n", responsePreview)
	} else {
		fmt.Printf("Error: %s\n", result.Error)
	}

	return nil
}

func sessionExample() error {
	fmt.Println("\n=== Session Example ===\n")

	// Create session
	sessionResult, err := scrappeyRequest(RequestOptions{
		Cmd:          "sessions.create",
		ProxyCountry: "UnitedStates",
		PremiumProxy: true,
	})
	if err != nil {
		return err
	}

	sessionID := sessionResult.Session
	fmt.Printf("Created session: %s\n", sessionID)

	// Use session
	result, err := scrappeyRequest(RequestOptions{
		Cmd:     "request.get",
		URL:     "https://httpbin.org/get",
		Session: sessionID,
	})
	if err != nil {
		return err
	}
	fmt.Printf("Request status: %d\n", result.Solution.StatusCode)

	// Destroy session
	_, err = scrappeyRequest(RequestOptions{
		Cmd:     "sessions.destroy",
		Session: sessionID,
	})
	if err != nil {
		return err
	}
	fmt.Printf("Destroyed session: %s\n", sessionID)

	return nil
}

func browserActionsExample() error {
	fmt.Println("\n=== Browser Actions Example ===\n")

	result, err := scrappeyRequest(RequestOptions{
		Cmd: "request.get",
		URL: "https://example.com",
		BrowserActions: []BrowserAction{
			{Type: "wait_for_selector", CSSSelector: "body"},
			{Type: "execute_js", Code: "document.title"},
			{Type: "scroll", CSSSelector: "footer"},
		},
	})
	if err != nil {
		return err
	}

	if result.Data == "success" {
		fmt.Printf("Page loaded, status: %d\n", result.Solution.StatusCode)
	} else {
		fmt.Printf("Error: %s\n", result.Error)
	}

	return nil
}

func cloudflareExample() error {
	fmt.Println("\n=== Cloudflare Bypass Example ===\n")

	result, err := scrappeyRequest(RequestOptions{
		Cmd:              "request.get",
		URL:              "https://example-protected-site.com",
		CloudflareBypass: true,
		PremiumProxy:     true,
		ProxyCountry:     "UnitedStates",
	})
	if err != nil {
		return err
	}

	if result.Data == "success" {
		fmt.Printf("Successfully bypassed! Status: %d\n", result.Solution.StatusCode)
	} else {
		fmt.Printf("Error: %s\n", result.Error)
	}

	return nil
}

func postExample() error {
	fmt.Println("\n=== POST Example ===\n")

	result, err := scrappeyRequest(RequestOptions{
		Cmd:      "request.post",
		URL:      "https://httpbin.org/post",
		PostData: "username=test&password=test123",
	})
	if err != nil {
		return err
	}

	fmt.Printf("POST status: %d\n", result.Solution.StatusCode)
	return nil
}

func main() {
	fmt.Println("Scrappey Go Examples")
	fmt.Println("==================================================")

	if err := basicExample(); err != nil {
		fmt.Printf("Basic example error: %v\n", err)
	}

	if err := sessionExample(); err != nil {
		fmt.Printf("Session example error: %v\n", err)
	}

	if err := postExample(); err != nil {
		fmt.Printf("POST example error: %v\n", err)
	}

	// Uncomment to run additional examples:
	// cloudflareExample()
	// browserActionsExample()

	fmt.Println("\n✓ All examples completed!\n")
}
