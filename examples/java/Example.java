/**
 * Scrappey - Java Example
 *
 * This example demonstrates how to use the Scrappey API from Java
 * for web scraping with Cloudflare bypass and browser automation.
 *
 * Prerequisites:
 *   Java 11+
 *   Add Gson dependency (or use the built-in JSON processing)
 *
 * Run:
 *   javac Example.java && java Example
 *
 * Get your API key at: https://app.scrappey.com
 */

import java.net.URI;
import java.net.http.*;
import java.util.*;

public class Example {

    private static final String API_KEY = System.getenv("SCRAPPEY_API_KEY") != null
        ? System.getenv("SCRAPPEY_API_KEY")
        : "YOUR_API_KEY";
    private static final String API_URL = "https://publisher.scrappey.com/api/v1";
    private static final HttpClient httpClient = HttpClient.newHttpClient();

    /**
     * Send a request to the Scrappey API
     */
    public static String scrappeyRequest(String cmd, Map<String, Object> data) throws Exception {
        Map<String, Object> payload = new HashMap<>(data);
        payload.put("cmd", cmd);

        String jsonPayload = mapToJson(payload);

        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(API_URL + "?key=" + API_KEY))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
            .build();

        HttpResponse<String> response = httpClient.send(request,
            HttpResponse.BodyHandlers.ofString());

        return response.body();
    }

    /**
     * Simple map to JSON converter (for basic types)
     */
    private static String mapToJson(Map<String, Object> map) {
        StringBuilder sb = new StringBuilder("{");
        boolean first = true;

        for (Map.Entry<String, Object> entry : map.entrySet()) {
            if (!first) sb.append(",");
            first = false;

            sb.append("\"").append(entry.getKey()).append("\":");

            Object value = entry.getValue();
            if (value instanceof String) {
                sb.append("\"").append(escapeJson((String) value)).append("\"");
            } else if (value instanceof Number || value instanceof Boolean) {
                sb.append(value);
            } else if (value instanceof Map) {
                sb.append(mapToJson((Map<String, Object>) value));
            } else if (value instanceof List) {
                sb.append(listToJson((List<?>) value));
            } else if (value == null) {
                sb.append("null");
            } else {
                sb.append("\"").append(escapeJson(value.toString())).append("\"");
            }
        }

        sb.append("}");
        return sb.toString();
    }

    private static String listToJson(List<?> list) {
        StringBuilder sb = new StringBuilder("[");
        boolean first = true;

        for (Object item : list) {
            if (!first) sb.append(",");
            first = false;

            if (item instanceof String) {
                sb.append("\"").append(escapeJson((String) item)).append("\"");
            } else if (item instanceof Map) {
                sb.append(mapToJson((Map<String, Object>) item));
            } else {
                sb.append(item);
            }
        }

        sb.append("]");
        return sb.toString();
    }

    private static String escapeJson(String str) {
        return str.replace("\\", "\\\\")
                  .replace("\"", "\\\"")
                  .replace("\n", "\\n")
                  .replace("\r", "\\r")
                  .replace("\t", "\\t");
    }

    /**
     * Basic example: Simple GET request
     */
    public static void basicExample() throws Exception {
        System.out.println("\n=== Basic Example ===\n");

        Map<String, Object> data = new HashMap<>();
        data.put("url", "https://httpbin.org/get");

        String result = scrappeyRequest("request.get", data);

        if (result.contains("\"data\":\"success\"")) {
            System.out.println("Request successful!");
            // In production, use a JSON library to parse the response
            int start = result.indexOf("\"statusCode\":") + 13;
            int end = result.indexOf(",", start);
            String statusCode = result.substring(start, end);
            System.out.println("Status Code: " + statusCode);
        } else {
            System.out.println("Error in response: " + result.substring(0, Math.min(200, result.length())));
        }
    }

    /**
     * Session example: Maintain cookies across requests
     */
    public static void sessionExample() throws Exception {
        System.out.println("\n=== Session Example ===\n");

        // Create session
        Map<String, Object> sessionData = new HashMap<>();
        sessionData.put("proxyCountry", "UnitedStates");

        String createResult = scrappeyRequest("sessions.create", sessionData);

        // Extract session ID (in production, use a JSON library)
        int sessionStart = createResult.indexOf("\"session\":\"") + 11;
        int sessionEnd = createResult.indexOf("\"", sessionStart);
        String sessionId = createResult.substring(sessionStart, sessionEnd);
        System.out.println("Created session: " + sessionId);

        try {
            // Use session
            Map<String, Object> requestData = new HashMap<>();
            requestData.put("url", "https://httpbin.org/get");
            requestData.put("session", sessionId);

            String result = scrappeyRequest("request.get", requestData);
            System.out.println("Request with session completed");

        } finally {
            // Destroy session
            Map<String, Object> destroyData = new HashMap<>();
            destroyData.put("session", sessionId);
            scrappeyRequest("sessions.destroy", destroyData);
            System.out.println("Destroyed session: " + sessionId);
        }
    }

    /**
     * Browser actions example
     */
    public static void browserActionsExample() throws Exception {
        System.out.println("\n=== Browser Actions Example ===\n");

        List<Map<String, Object>> actions = new ArrayList<>();

        Map<String, Object> waitAction = new HashMap<>();
        waitAction.put("type", "wait_for_selector");
        waitAction.put("cssSelector", "body");
        actions.add(waitAction);

        Map<String, Object> jsAction = new HashMap<>();
        jsAction.put("type", "execute_js");
        jsAction.put("code", "document.title");
        actions.add(jsAction);

        Map<String, Object> data = new HashMap<>();
        data.put("url", "https://example.com");
        data.put("browserActions", actions);

        String result = scrappeyRequest("request.get", data);

        if (result.contains("\"data\":\"success\"")) {
            System.out.println("Browser actions completed successfully!");
        } else {
            System.out.println("Error: " + result.substring(0, Math.min(200, result.length())));
        }
    }

    /**
     * POST request example
     */
    public static void postExample() throws Exception {
        System.out.println("\n=== POST Example ===\n");

        Map<String, Object> data = new HashMap<>();
        data.put("url", "https://httpbin.org/post");
        data.put("postData", "username=test&password=test123");

        String result = scrappeyRequest("request.post", data);

        if (result.contains("\"data\":\"success\"")) {
            System.out.println("POST request successful!");
        } else {
            System.out.println("Error in POST request");
        }
    }

    /**
     * Cloudflare bypass example
     */
    public static void cloudflareExample() throws Exception {
        System.out.println("\n=== Cloudflare Bypass Example ===\n");

        Map<String, Object> data = new HashMap<>();
        data.put("url", "https://example-protected-site.com");
        data.put("cloudflareBypass", true);
        data.put("premiumProxy", true);
        data.put("proxyCountry", "UnitedStates");

        String result = scrappeyRequest("request.get", data);

        if (result.contains("\"data\":\"success\"")) {
            System.out.println("Successfully bypassed Cloudflare!");
        } else {
            System.out.println("Bypass failed or error occurred");
        }
    }

    public static void main(String[] args) {
        System.out.println("Scrappey Java Examples");
        System.out.println("==================================================");

        try {
            basicExample();
            sessionExample();
            postExample();
            // Uncomment to run additional examples:
            // browserActionsExample();
            // cloudflareExample();

            System.out.println("\n✓ All examples completed!\n");

        } catch (Exception e) {
            System.err.println("Error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}
