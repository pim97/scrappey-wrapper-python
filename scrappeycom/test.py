from scrappey import Scrappey
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

        get_request_result = scrappey.request({
            "cmd":  "request.get",
            'session': session['session'],
            'url': 'https://httpbin.rs/get',
        })
        print('GET Request Result:', get_request_result)

        post_request_result = scrappey.request({
            "cmd": "request.post",
            "url": "https://httpbin.rs/post",
            "postData": "test=test&test2=test2"
        })
        print('POST Request Result:', post_request_result)

        # JSON request example
        post_request_result_json = scrappey.request({
            "cmd": "request.post",
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
