/**
 * Scrappey - Kotlin Example
 *
 * This example demonstrates how to use the Scrappey API from Kotlin
 * for web scraping with Cloudflare bypass and browser automation.
 *
 * Prerequisites:
 *   - Kotlin 1.8+
 *   - Add kotlinx-serialization-json dependency
 *
 * Run:
 *   kotlinc Example.kt -include-runtime -d example.jar && java -jar example.jar
 *
 * Get your API key at: https://app.scrappey.com
 */

import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse

val API_KEY: String = System.getenv("SCRAPPEY_API_KEY") ?: "YOUR_API_KEY"
val API_URL: String = "https://publisher.scrappey.com/api/v1"
val httpClient: HttpClient = HttpClient.newHttpClient()

/**
 * Send a request to the Scrappey API
 */
fun scrappeyRequest(cmd: String, data: Map<String, Any?> = emptyMap()): String {
    val payload = mapOf("cmd" to cmd) + data
    val jsonPayload = mapToJson(payload)

    val request = HttpRequest.newBuilder()
        .uri(URI.create("$API_URL?key=$API_KEY"))
        .header("Content-Type", "application/json")
        .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
        .build()

    val response = httpClient.send(request, HttpResponse.BodyHandlers.ofString())
    return response.body()
}

/**
 * Convert map to JSON string (simple implementation)
 */
fun mapToJson(map: Map<String, Any?>): String {
    val entries = map.entries.joinToString(",") { (key, value) ->
        "\"$key\":${valueToJson(value)}"
    }
    return "{$entries}"
}

fun valueToJson(value: Any?): String = when (value) {
    null -> "null"
    is String -> "\"${value.replace("\\", "\\\\").replace("\"", "\\\"")}\""
    is Number, is Boolean -> value.toString()
    is Map<*, *> -> mapToJson(value as Map<String, Any?>)
    is List<*> -> "[${value.joinToString(",") { valueToJson(it) }}]"
    else -> "\"$value\""
}

/**
 * Extract a simple string value from JSON response
 */
fun extractJsonValue(json: String, key: String): String? {
    val pattern = "\"$key\":\"([^\"]*)\""
    val regex = Regex(pattern)
    return regex.find(json)?.groupValues?.getOrNull(1)
}

fun extractJsonNumber(json: String, key: String): Int? {
    val pattern = "\"$key\":(\\d+)"
    val regex = Regex(pattern)
    return regex.find(json)?.groupValues?.getOrNull(1)?.toIntOrNull()
}

/**
 * Basic example: Simple GET request
 */
fun basicExample() {
    println("\n=== Basic Example ===\n")

    val result = scrappeyRequest("request.get", mapOf(
        "url" to "https://httpbin.org/get"
    ))

    if (result.contains("\"data\":\"success\"")) {
        val statusCode = extractJsonNumber(result, "statusCode")
        println("Status: $statusCode")
        println("Response received successfully")
    } else {
        println("Error in response")
    }
}

/**
 * Session example: Maintain cookies across requests
 */
fun sessionExample() {
    println("\n=== Session Example ===\n")

    // Create session
    val sessionResult = scrappeyRequest("sessions.create", mapOf(
        "proxyCountry" to "UnitedStates",
        "premiumProxy" to true
    ))

    val sessionId = extractJsonValue(sessionResult, "session") ?: return
    println("Created session: $sessionId")

    try {
        // Use session for request
        val result = scrappeyRequest("request.get", mapOf(
            "url" to "https://httpbin.org/get",
            "session" to sessionId
        ))

        val statusCode = extractJsonNumber(result, "statusCode")
        println("Request status: $statusCode")

    } finally {
        // Destroy session
        scrappeyRequest("sessions.destroy", mapOf(
            "session" to sessionId
        ))
        println("Destroyed session: $sessionId")
    }
}

/**
 * Browser actions example
 */
fun browserActionsExample() {
    println("\n=== Browser Actions Example ===\n")

    val actions = listOf(
        mapOf("type" to "wait_for_selector", "cssSelector" to "body"),
        mapOf("type" to "execute_js", "code" to "document.title"),
        mapOf("type" to "wait", "wait" to 1000)
    )

    val result = scrappeyRequest("request.get", mapOf(
        "url" to "https://example.com",
        "browserActions" to actions
    ))

    if (result.contains("\"data\":\"success\"")) {
        println("Browser actions completed successfully!")
    } else {
        println("Error in browser actions")
    }
}

/**
 * POST request example
 */
fun postExample() {
    println("\n=== POST Example ===\n")

    // Form data
    val formResult = scrappeyRequest("request.post", mapOf(
        "url" to "https://httpbin.org/post",
        "postData" to "username=test&password=test123"
    ))

    val formStatus = extractJsonNumber(formResult, "statusCode")
    println("Form POST status: $formStatus")

    // JSON data
    val jsonResult = scrappeyRequest("request.post", mapOf(
        "url" to "https://httpbin.org/post",
        "postData" to """{"key": "value", "number": 42}""",
        "customHeaders" to mapOf("Content-Type" to "application/json")
    ))

    val jsonStatus = extractJsonNumber(jsonResult, "statusCode")
    println("JSON POST status: $jsonStatus")
}

/**
 * Cloudflare bypass example
 */
fun cloudflareExample() {
    println("\n=== Cloudflare Bypass Example ===\n")

    val result = scrappeyRequest("request.get", mapOf(
        "url" to "https://example-protected-site.com",
        "cloudflareBypass" to true,
        "premiumProxy" to true,
        "proxyCountry" to "UnitedStates"
    ))

    if (result.contains("\"data\":\"success\"")) {
        println("Successfully bypassed Cloudflare!")
    } else {
        println("Bypass failed or error occurred")
    }
}

fun main() {
    println("Scrappey Kotlin Examples")
    println("=".repeat(50))

    try {
        basicExample()
        sessionExample()
        postExample()
        // Uncomment to run additional examples:
        // browserActionsExample()
        // cloudflareExample()

        println("\n✓ All examples completed!\n")

    } catch (e: Exception) {
        println("Error: ${e.message}")
        e.printStackTrace()
    }
}
