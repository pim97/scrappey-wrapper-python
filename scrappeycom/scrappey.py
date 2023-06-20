import requests

class Scrappey:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://publisher.scrappey.com/api/v1'

    def send_request(self, endpoint, method, data=None):
        url = f'{self.base_url}?key={self.api_key}'

        headers = {
            'Content-Type': 'application/json'
        }

        payload = {
            'cmd': endpoint,
            **data
        }

        try:
            response = requests.request(method, url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            raise error

    def create_session(self, session_id=None, proxy=None):
        return self.send_request('sessions.create', 'POST', {'session': session_id, 'proxy': proxy})

    def destroy_session(self, session_id):
        if session_id is None:
            raise ValueError('sessionId parameter is required.')

        return self.send_request('sessions.destroy', 'POST', {'session': session_id})

    def get_request(self, url, session_id=None, cookiejar=None, proxy=None):
        if url is None:
            raise ValueError('url parameter is required.')

        if session_id is None and cookiejar is None and proxy is None:
            raise ValueError('At least one of sessionId, cookiejar, or proxy parameters must be provided.')

        return self.send_request('request.get', 'POST', {'url': url, 'session': session_id, 'cookiejar': cookiejar, 'proxy': proxy})

    def post_request(self, url, post_data, session_id=None, cookiejar=None, proxy=None):
        is_form_data = isinstance(post_data, str) and '=' in post_data

        if not is_form_data:
            try:
                request_data = requests.utils.quote(post_data)
            except ValueError:
                raise ValueError('Invalid postData format. It must be in application/x-www-form-urlencoded format.')
        else:
            request_data = post_data

        return self.send_request('request.post', 'POST', {'url': url, 'postData': request_data, 'session': session_id, 'cookiejar': cookiejar, 'proxy': proxy})
