//! Scrappey - Rust Example
//!
//! This example demonstrates how to use the Scrappey API from Rust
//! for web scraping with Cloudflare bypass and browser automation.
//!
//! Prerequisites:
//!   cargo add reqwest tokio serde serde_json
//!
//! Run:
//!   cargo run
//!
//! Get your API key at: https://app.scrappey.com

use reqwest::Client;
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use std::env;

fn get_api_key() -> String {
    env::var("SCRAPPEY_API_KEY").unwrap_or_else(|_| "YOUR_API_KEY".to_string())
}

fn get_api_url() -> String {
    "https://publisher.scrappey.com/api/v1".to_string()
}

// Response types
#[derive(Debug, Deserialize)]
struct Solution {
    verified: Option<bool>,
    response: Option<String>,
    #[serde(rename = "statusCode")]
    status_code: Option<i32>,
    #[serde(rename = "currentUrl")]
    current_url: Option<String>,
    #[serde(rename = "userAgent")]
    user_agent: Option<String>,
    #[serde(rename = "cookieString")]
    cookie_string: Option<String>,
    screenshot: Option<String>,
    #[serde(rename = "javascriptReturn")]
    javascript_return: Option<Vec<Value>>,
}

#[derive(Debug, Deserialize)]
struct ScrappeyResponse {
    solution: Option<Solution>,
    #[serde(rename = "timeElapsed")]
    time_elapsed: Option<i32>,
    data: Option<String>,
    session: Option<String>,
    error: Option<String>,
}

/// Send a request to the Scrappey API
async fn scrappey_request(
    client: &Client,
    cmd: &str,
    data: Value,
) -> Result<ScrappeyResponse, Box<dyn std::error::Error>> {
    let api_url = get_api_url();
    let api_key = get_api_key();

    let mut payload = data.as_object().cloned().unwrap_or_default();
    payload.insert("cmd".to_string(), json!(cmd));

    let response = client
        .post(format!("{}?key={}", api_url, api_key))
        .header("Content-Type", "application/json")
        .json(&payload)
        .send()
        .await?;

    let result: ScrappeyResponse = response.json().await?;
    Ok(result)
}

/// Basic example: Simple GET request
async fn basic_example(client: &Client) -> Result<(), Box<dyn std::error::Error>> {
    println!("\n=== Basic Example ===\n");

    let result = scrappey_request(
        client,
        "request.get",
        json!({
            "url": "https://httpbin.org/get"
        }),
    )
    .await?;

    if result.data.as_deref() == Some("success") {
        if let Some(solution) = &result.solution {
            println!("Status: {:?}", solution.status_code);
            if let Some(response) = &solution.response {
                let preview = if response.len() > 200 {
                    format!("{}...", &response[..200])
                } else {
                    response.clone()
                };
                println!("Response: {}", preview);
            }
        }
    } else {
        println!("Error: {:?}", result.error);
    }

    Ok(())
}

/// Session example: Maintain cookies across requests
async fn session_example(client: &Client) -> Result<(), Box<dyn std::error::Error>> {
    println!("\n=== Session Example ===\n");

    // Create session
    let session_result = scrappey_request(
        client,
        "sessions.create",
        json!({
            "proxyCountry": "UnitedStates",
            "premiumProxy": true
        }),
    )
    .await?;

    let session_id = session_result
        .session
        .clone()
        .unwrap_or_default();
    println!("Created session: {}", session_id);

    // Use session for request
    let result = scrappey_request(
        client,
        "request.get",
        json!({
            "url": "https://httpbin.org/get",
            "session": &session_id
        }),
    )
    .await?;

    if let Some(solution) = &result.solution {
        println!("Request status: {:?}", solution.status_code);
    }

    // Destroy session
    scrappey_request(
        client,
        "sessions.destroy",
        json!({
            "session": &session_id
        }),
    )
    .await?;
    println!("Destroyed session: {}", session_id);

    Ok(())
}

/// POST request example
async fn post_example(client: &Client) -> Result<(), Box<dyn std::error::Error>> {
    println!("\n=== POST Example ===\n");

    let result = scrappey_request(
        client,
        "request.post",
        json!({
            "url": "https://httpbin.org/post",
            "postData": "username=test&password=test123"
        }),
    )
    .await?;

    if let Some(solution) = &result.solution {
        println!("POST status: {:?}", solution.status_code);
    }

    Ok(())
}

/// Browser actions example
async fn browser_actions_example(client: &Client) -> Result<(), Box<dyn std::error::Error>> {
    println!("\n=== Browser Actions Example ===\n");

    let result = scrappey_request(
        client,
        "request.get",
        json!({
            "url": "https://example.com",
            "browserActions": [
                {"type": "wait_for_selector", "cssSelector": "body"},
                {"type": "execute_js", "code": "document.title"},
                {"type": "scroll", "cssSelector": "footer"}
            ]
        }),
    )
    .await?;

    if result.data.as_deref() == Some("success") {
        if let Some(solution) = &result.solution {
            println!("Page loaded, status: {:?}", solution.status_code);
            if let Some(js_return) = &solution.javascript_return {
                println!("JS Return: {:?}", js_return);
            }
        }
    } else {
        println!("Error: {:?}", result.error);
    }

    Ok(())
}

/// Cloudflare bypass example
async fn cloudflare_example(client: &Client) -> Result<(), Box<dyn std::error::Error>> {
    println!("\n=== Cloudflare Bypass Example ===\n");

    let result = scrappey_request(
        client,
        "request.get",
        json!({
            "url": "https://example-protected-site.com",
            "cloudflareBypass": true,
            "premiumProxy": true,
            "proxyCountry": "UnitedStates"
        }),
    )
    .await?;

    if result.data.as_deref() == Some("success") {
        println!("Successfully bypassed!");
    } else {
        println!("Error: {:?}", result.error);
    }

    Ok(())
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("Scrappey Rust Examples");
    println!("{}", "=".repeat(50));

    let client = Client::builder()
        .timeout(std::time::Duration::from_secs(300))
        .build()?;

    basic_example(&client).await?;
    session_example(&client).await?;
    post_example(&client).await?;
    // Uncomment to run additional examples:
    // browser_actions_example(&client).await?;
    // cloudflare_example(&client).await?;

    println!("\n✓ All examples completed!\n");

    Ok(())
}
