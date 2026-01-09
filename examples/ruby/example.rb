# Scrappey - Ruby Example
#
# This example demonstrates how to use the Scrappey API from Ruby
# for web scraping with Cloudflare bypass and browser automation.
#
# Prerequisites:
#   Ruby 3.0+
#   gem install json net-http
#
# Run:
#   ruby example.rb
#
# Get your API key at: https://app.scrappey.com

require 'net/http'
require 'json'
require 'uri'
require 'base64'

API_KEY = ENV['SCRAPPEY_API_KEY'] || 'YOUR_API_KEY'
API_URL = 'https://publisher.scrappey.com/api/v1'

# Send a request to the Scrappey API
def scrappey_request(cmd, data = {})
  uri = URI("#{API_URL}?key=#{API_KEY}")
  
  payload = { cmd: cmd }.merge(data)
  
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = true
  http.read_timeout = 300
  
  request = Net::HTTP::Post.new(uri)
  request['Content-Type'] = 'application/json'
  request.body = payload.to_json
  
  response = http.request(request)
  
  JSON.parse(response.body)
rescue StandardError => e
  raise "Request failed: #{e.message}"
end

# Basic example: Simple GET request
def basic_example
  puts "\n=== Basic Example ===\n\n"

  result = scrappey_request('request.get', url: 'https://httpbin.org/get')

  if result['data'] == 'success'
    puts "Status: #{result['solution']['statusCode']}"
    preview = result['solution']['response'][0, 200] + '...'
    puts "Response: #{preview}"
  else
    puts "Error: #{result['error']}"
  end
end

# Session example: Maintain cookies across requests
def session_example
  puts "\n=== Session Example ===\n\n"

  # Create session
  session_result = scrappey_request('sessions.create',
    proxyCountry: 'UnitedStates',
    premiumProxy: true
  )

  session_id = session_result['session']
  puts "Created session: #{session_id}"

  begin
    # Set cookie
    scrappey_request('request.get',
      url: 'https://httpbin.org/cookies/set/test/value123',
      session: session_id
    )

    # Verify cookie persists
    result = scrappey_request('request.get',
      url: 'https://httpbin.org/cookies',
      session: session_id
    )
    puts "Cookies: #{result['solution']['response']}"

  ensure
    # Destroy session
    scrappey_request('sessions.destroy', session: session_id)
    puts "Destroyed session: #{session_id}"
  end
end

# Browser actions example
def browser_actions_example
  puts "\n=== Browser Actions Example ===\n\n"

  result = scrappey_request('request.get',
    url: 'https://example.com',
    browserActions: [
      { type: 'wait_for_selector', cssSelector: 'body' },
      { type: 'execute_js', code: 'document.title' },
      { type: 'scroll', cssSelector: 'footer' }
    ]
  )

  if result['data'] == 'success'
    puts "Page loaded, status: #{result['solution']['statusCode']}"
    if result['solution']['javascriptReturn']
      puts "JS Return: #{result['solution']['javascriptReturn']}"
    end
  else
    puts "Error: #{result['error']}"
  end
end

# POST request example
def post_example
  puts "\n=== POST Example ===\n\n"

  # Form data
  result = scrappey_request('request.post',
    url: 'https://httpbin.org/post',
    postData: 'username=test&password=test123'
  )
  puts "Form POST status: #{result['solution']['statusCode']}"

  # JSON data
  result = scrappey_request('request.post',
    url: 'https://httpbin.org/post',
    postData: { key: 'value', number: 42 }.to_json,
    customHeaders: { 'Content-Type' => 'application/json' }
  )
  puts "JSON POST status: #{result['solution']['statusCode']}"
end

# Cloudflare bypass example
def cloudflare_example
  puts "\n=== Cloudflare Bypass Example ===\n\n"

  result = scrappey_request('request.get',
    url: 'https://example-protected-site.com',
    cloudflareBypass: true,
    premiumProxy: true,
    proxyCountry: 'UnitedStates'
  )

  if result['data'] == 'success'
    puts "Successfully bypassed! Status: #{result['solution']['statusCode']}"
  else
    puts "Error: #{result['error']}"
  end
end

# Screenshot example
def screenshot_example
  puts "\n=== Screenshot Example ===\n\n"

  result = scrappey_request('request.get',
    url: 'https://example.com',
    screenshot: true,
    screenshotWidth: 1920,
    screenshotHeight: 1080
  )

  if result['data'] == 'success' && result['solution']['screenshot']
    image_data = Base64.decode64(result['solution']['screenshot'])
    File.write('screenshot.png', image_data, mode: 'wb')
    puts 'Screenshot saved to screenshot.png'
  else
    puts "Error: #{result['error'] || 'No screenshot returned'}"
  end
end

# Captcha solving example
def captcha_solving_example
  puts "\n=== Captcha Solving Example ===\n\n"

  result = scrappey_request('request.get',
    url: 'https://example.com/protected',
    automaticallySolveCaptchas: true,
    alwaysLoad: %w[recaptcha hcaptcha turnstile]
  )

  if result['data'] == 'success'
    puts "Captcha result: #{result['solution']['captchaSolveResult']}"
    puts "Response length: #{result['solution']['response'].length}"
  else
    puts "Error: #{result['error']}"
  end
end

# Main execution
puts 'Scrappey Ruby Examples'
puts '=' * 50

begin
  basic_example
  session_example
  post_example
  # Uncomment to run additional examples:
  # browser_actions_example
  # cloudflare_example
  # screenshot_example
  # captcha_solving_example

  puts "\n✓ All examples completed!\n\n"

rescue StandardError => e
  puts "Error: #{e.message}"
  exit 1
end
