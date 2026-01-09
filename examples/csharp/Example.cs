/**
 * Scrappey - C# (.NET) Example
 *
 * This example demonstrates how to use the Scrappey API from C#
 * for web scraping with Cloudflare bypass and browser automation.
 *
 * Prerequisites:
 *   .NET 6.0+
 *   dotnet add package System.Text.Json
 *
 * Run:
 *   dotnet run
 *
 * Get your API key at: https://app.scrappey.com
 */

using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Text.Json.Serialization;
using System.Threading.Tasks;

class Program
{
    private static readonly string ApiKey = Environment.GetEnvironmentVariable("SCRAPPEY_API_KEY") 
        ?? "YOUR_API_KEY";
    private static readonly string ApiUrl = "https://publisher.scrappey.com/api/v1";
    private static readonly HttpClient httpClient = new HttpClient();

    // Response types
    public class Solution
    {
        [JsonPropertyName("verified")]
        public bool Verified { get; set; }

        [JsonPropertyName("response")]
        public string Response { get; set; } = "";

        [JsonPropertyName("statusCode")]
        public int StatusCode { get; set; }

        [JsonPropertyName("currentUrl")]
        public string CurrentUrl { get; set; } = "";

        [JsonPropertyName("userAgent")]
        public string UserAgent { get; set; } = "";

        [JsonPropertyName("cookieString")]
        public string CookieString { get; set; } = "";

        [JsonPropertyName("screenshot")]
        public string? Screenshot { get; set; }
    }

    public class ScrappeyResponse
    {
        [JsonPropertyName("solution")]
        public Solution Solution { get; set; } = new();

        [JsonPropertyName("timeElapsed")]
        public int TimeElapsed { get; set; }

        [JsonPropertyName("data")]
        public string Data { get; set; } = "";

        [JsonPropertyName("session")]
        public string Session { get; set; } = "";

        [JsonPropertyName("error")]
        public string? Error { get; set; }
    }

    /// <summary>
    /// Send a request to the Scrappey API
    /// </summary>
    static async Task<ScrappeyResponse> ScrappeyRequest(string cmd, Dictionary<string, object> data)
    {
        data["cmd"] = cmd;

        var json = JsonSerializer.Serialize(data, new JsonSerializerOptions
        {
            DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull
        });

        var content = new StringContent(json, Encoding.UTF8, "application/json");
        var response = await httpClient.PostAsync($"{ApiUrl}?key={ApiKey}", content);
        var responseBody = await response.Content.ReadAsStringAsync();

        return JsonSerializer.Deserialize<ScrappeyResponse>(responseBody) 
            ?? throw new Exception("Failed to parse response");
    }

    /// <summary>
    /// Basic example: Simple GET request
    /// </summary>
    static async Task BasicExample()
    {
        Console.WriteLine("\n=== Basic Example ===\n");

        var result = await ScrappeyRequest("request.get", new Dictionary<string, object>
        {
            ["url"] = "https://httpbin.org/get"
        });

        if (result.Data == "success")
        {
            Console.WriteLine($"Status: {result.Solution.StatusCode}");
            var preview = result.Solution.Response.Length > 200 
                ? result.Solution.Response[..200] + "..." 
                : result.Solution.Response;
            Console.WriteLine($"Response: {preview}");
        }
        else
        {
            Console.WriteLine($"Error: {result.Error}");
        }
    }

    /// <summary>
    /// Session example: Maintain cookies across requests
    /// </summary>
    static async Task SessionExample()
    {
        Console.WriteLine("\n=== Session Example ===\n");

        // Create session
        var sessionResult = await ScrappeyRequest("sessions.create", new Dictionary<string, object>
        {
            ["proxyCountry"] = "UnitedStates",
            ["premiumProxy"] = true
        });

        var sessionId = sessionResult.Session;
        Console.WriteLine($"Created session: {sessionId}");

        try
        {
            // Use session for request
            var result = await ScrappeyRequest("request.get", new Dictionary<string, object>
            {
                ["url"] = "https://httpbin.org/get",
                ["session"] = sessionId
            });

            Console.WriteLine($"Request status: {result.Solution.StatusCode}");
        }
        finally
        {
            // Destroy session
            await ScrappeyRequest("sessions.destroy", new Dictionary<string, object>
            {
                ["session"] = sessionId
            });
            Console.WriteLine($"Destroyed session: {sessionId}");
        }
    }

    /// <summary>
    /// Browser actions example
    /// </summary>
    static async Task BrowserActionsExample()
    {
        Console.WriteLine("\n=== Browser Actions Example ===\n");

        var actions = new List<Dictionary<string, object>>
        {
            new() { ["type"] = "wait_for_selector", ["cssSelector"] = "body" },
            new() { ["type"] = "execute_js", ["code"] = "document.title" },
            new() { ["type"] = "scroll", ["cssSelector"] = "footer" }
        };

        var result = await ScrappeyRequest("request.get", new Dictionary<string, object>
        {
            ["url"] = "https://example.com",
            ["browserActions"] = actions
        });

        if (result.Data == "success")
        {
            Console.WriteLine($"Page loaded, status: {result.Solution.StatusCode}");
        }
        else
        {
            Console.WriteLine($"Error: {result.Error}");
        }
    }

    /// <summary>
    /// POST request example
    /// </summary>
    static async Task PostExample()
    {
        Console.WriteLine("\n=== POST Example ===\n");

        var result = await ScrappeyRequest("request.post", new Dictionary<string, object>
        {
            ["url"] = "https://httpbin.org/post",
            ["postData"] = "username=test&password=test123"
        });

        Console.WriteLine($"POST status: {result.Solution.StatusCode}");
    }

    /// <summary>
    /// Cloudflare bypass example
    /// </summary>
    static async Task CloudflareExample()
    {
        Console.WriteLine("\n=== Cloudflare Bypass Example ===\n");

        var result = await ScrappeyRequest("request.get", new Dictionary<string, object>
        {
            ["url"] = "https://example-protected-site.com",
            ["cloudflareBypass"] = true,
            ["premiumProxy"] = true,
            ["proxyCountry"] = "UnitedStates"
        });

        if (result.Data == "success")
        {
            Console.WriteLine($"Successfully bypassed! Status: {result.Solution.StatusCode}");
        }
        else
        {
            Console.WriteLine($"Error: {result.Error}");
        }
    }

    /// <summary>
    /// Screenshot example
    /// </summary>
    static async Task ScreenshotExample()
    {
        Console.WriteLine("\n=== Screenshot Example ===\n");

        var result = await ScrappeyRequest("request.get", new Dictionary<string, object>
        {
            ["url"] = "https://example.com",
            ["screenshot"] = true,
            ["screenshotWidth"] = 1920,
            ["screenshotHeight"] = 1080
        });

        if (result.Data == "success" && !string.IsNullOrEmpty(result.Solution.Screenshot))
        {
            var bytes = Convert.FromBase64String(result.Solution.Screenshot);
            await System.IO.File.WriteAllBytesAsync("screenshot.png", bytes);
            Console.WriteLine("Screenshot saved to screenshot.png");
        }
        else
        {
            Console.WriteLine($"Error: {result.Error}");
        }
    }

    static async Task Main(string[] args)
    {
        Console.WriteLine("Scrappey C# Examples");
        Console.WriteLine(new string('=', 50));

        try
        {
            await BasicExample();
            await SessionExample();
            await PostExample();
            // Uncomment to run additional examples:
            // await BrowserActionsExample();
            // await CloudflareExample();
            // await ScreenshotExample();

            Console.WriteLine("\n✓ All examples completed!\n");
        }
        catch (Exception e)
        {
            Console.Error.WriteLine($"Error: {e.Message}");
        }
    }
}
