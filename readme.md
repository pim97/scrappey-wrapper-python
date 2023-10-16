# 🤖 Scrappey Wrapper - Data Extraction Made Easy - Now in 5 seconds!   
 
Introducing Scrappey, your comprehensive website scraping solution provided by Scrappey.com. With Scrappey's powerful and user-friendly API, you can effortlessly retrieve data from websites, including those protected by Cloudflare without using too much data using caching. Join Scrappey today and revolutionize your data extraction process. 🚀 Check out our https://app.scrappey.com/#/builder to create your first script!  

**Disclaimer: Please ensure that your web scraping activities comply with the website's terms of service and legal regulations. Scrappey is not responsible for any misuse or unethical use of the library. Use it responsibly and respect the website's policies.** :) 


Website: https://scrappey.com/

## Topics

- [Installation](#installation)
- [Usage](#usage)
- [Example](#example)
- [License](#license)

## Installation

Use pip to install the Scrappey library. 💻

```shell
pip install scrappeycom
```

## Usage

Import the Scrappey library in your code. 📦

```python
from scrappeycom.scrappey import Scrappey
```

Create an instance of Scrappey by providing your Scrappey API key. 🔑

```python
api_key = 'YOUR_API_KEY'
scrappey_instance = scrappey.Scrappey(api_key)
```

### Example

Here's an example of how to use Scrappey. 🚀

```python
from scrappeycom.scrappey import Scrappey
import uuid

scrappey = Scrappey('API_KEY')

def run_test():
    try:
        sessionData = {
            'session': str(uuid.uuid4()), #uuid is also optional, otherwise default uuid will be used
            #'proxy': 'http://username:password@ip:port' #proxy is optional, otherwise default proxy will be used
        }
        session = scrappey.create_session(sessionData)
        print('Session created:', session['session'])

        # View all the options here with the request builder
        # https://app.scrappey.com/#/builder
        # Just copy paste it below, example
        #
        #    {
        #       "cmd":  "request.get",
        #       "url":  "https://httpbin.rs/get"
        #    }

        get_request_result = scrappey.get({
            'session': session['session'],
            'url': 'https://httpbin.rs/get',
        })
        print('GET Request Result:', get_request_result)

        post_request_result = scrappey.post({
            "url": "https://httpbin.rs/post",
            "postData": "test=test&test2=test2"
        })
        print('POST Request Result:', post_request_result)

        # JSON request example
        post_request_result_json = scrappey.post({
            "url": "https://backend.scrappey.com/api/auth/login",
            "postData": "{\"email\":\"email\",\"password\":\"password\"}",
            "customHeaders": {
                "content-type": "application/json"
            }
        })
        print('POST Request Result:', post_request_result_json)

        sessionDestroyed = scrappey.destroy_session(sessionData)
        print('Session destroyed:', sessionDestroyed)
    except Exception as error:
        print(error)

run_test()


```
For more information, please visit the [official Scrappey documentation](https://wiki.scrappey.com/getting-started). 📚

Here are some other examples from the builder (https://app.scrappey.com/#/builder).

```json
{
  "cmd": "request.get",
  "url": "https://httpbin.rs/get",
  "customHeaders": {
    "auth": "test"
  },
  "cookiejar": [
    {
      "key": "cookiekey",
      "value": "cookievalue",
      "domain": "httpbin.rs",
      "path": "/"
    }
  ],
  "session": "86908d12-b225-446c-bb16-dc5c283e1d59",
  "autoparse": true,
  "properties": "parse using ai, product name",
  "proxy": "http://proxystring"
}

{
  "cmd": "request.post",
  "url": "https://httpbin.rs/post",
  "postData": "{\"happy\":\"true}",
  "customHeaders": {
    "content-type": "application/json",
    "auth": "test"
  },
  "cookiejar": [
    {
      "key": "cookiekey",
      "value": "cookievalue",
      "domain": "httpbin.rs",
      "path": "/"
    }
  ],
  "session": "86908d12-b225-446c-bb16-dc5c283e1d59",
  "autoparse": true,
  "properties": "parse using ai, product name",
  "proxy": "http://proxystring"
}

{
    "cmd": "request.get",
    "url": "https://app.scrappey.com/#/login",
    "browserActions": [
        {
            "type": "type",
            "text": "testtest@test.nl",
            "cssSelector": "input[name='login']"
        },
        {
            "type": "type",
            "text": "amazingpassword",
            "cssSelector": "input[name='password']"
        },
        {
            "type": "click",
            "cssSelector": "button[class='inline-flex cursor-pointer justify-center items-center whitespace-nowrap focus:outline-none transition-colors focus:ring duration-150 border rounded ring-blue-700 p-2 bg-blue-500 text-white border-blue-600 hover:bg-blue-600']"
        },
        {
            "type": "goto",
            "url": "https://app.scrappey.com/#/profilev2"
        },
        {
            "type": "goto",
            "url": "https://app.scrappey.com/#/builder"
        }
        
    ]
}

{
    "cmd": "request.get",
    "url": "https://discordbotlist.com/bots/dank-memer/upvote",
    "browserActions": [
        {
            "type": "discord_login",
            "token": "token_here",
            "when": "beforeload"
        },
        {
            "type": "click",
            "cssSelector": "a[class='btn btn-blurple']",
            "wait": 5
        },
        {
            "type": "goto",
            "url": "https://discordbotlist.com/bots/dank-memer/upvote"
        },
        {
            "type": "click",
            "cssSelector": "button[class='btn btn-blurple']"
        },
        {
            "type": "click",
            "cssSelector": "button[class='btn btn-blurple disabled']"
        }
    ]
}

```


## License

This project is licensed under the MIT License.

## Additional Tags

cloudflare anti bot bypass, cloudflare solver, scraper, scraping, cloudflare scraper, cloudflare turnstile solver, turnstile solver, data extraction, web scraping, website scraping, data scraping, scraping tool, API scraping, scraping solution, web data extraction, website data extraction, web scraping library, website scraping library, cloudflare bypass, scraping API, web scraping API, cloudflare protection, data scraping tool, scraping service, cloudflare challenge solver, web scraping solution, web scraping service, cloudflare scraping, cloudflare bot protection, scraping framework, scraping library, cloudflare bypass tool, cloudflare anti-bot, cloudflare protection bypass, cloudflare solver tool, web scraping tool, data extraction library, website scraping tool, cloudflare turnstile bypass, cloudflare anti-bot solver, turnstile solver tool, cloudflare scraping solution, website data scraper, cloudflare challenge bypass, web scraping framework, cloudflare challenge solver tool, web data scraping, data scraper, scraping data from websites, SEO, data mining,

data harvesting, data crawling, web scraping software, website scraping tool, web scraping framework, data extraction tool, web data scraper, data scraping service, scraping automation, scraping tutorial, scraping code, scraping techniques, scraping best practices, scraping scripts, scraping tutorial, scraping examples, scraping challenges, scraping tricks, scraping tips, scraping tricks, scraping strategies, scraping methods, cloudflare protection bypass, cloudflare security bypass, web scraping Python, web scraping JavaScript, web scraping PHP, web scraping Ruby, web scraping Java, web scraping C#, web scraping Node.js, web scraping BeautifulSoup, web scraping Selenium, web scraping Scrapy, web scraping Puppeteer, web scraping requests, web scraping headless browser, web scraping dynamic content, web scraping AJAX, web scraping pagination, web scraping authentication, web scraping cookies, web scraping session management, web scraping data parsing, web scraping data cleaning, web scraping data analysis, web scraping data visualization, web scraping legal issues, web scraping ethics, web scraping compliance, web scraping regulations, web scraping IP blocking, web scraping anti-scraping measures, web scraping proxy, web scraping CAPTCHA solving, web scraping IP rotation, web scraping rate limiting, web scraping data privacy, web scraping consent, web scraping terms of service, web scraping robots.txt, web scraping data storage, web scraping database integration, web scraping data integration, web scraping API integration, web scraping data export, web scraping data processing, web scraping data transformation, web scraping data enrichment, web scraping data validation, web scraping error handling, web scraping scalability, web scraping performance optimization, web scraping distributed scraping, web scraping cloud-based scraping, web scraping serverless scraping.
