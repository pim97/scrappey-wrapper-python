import requests
import urllib.parse

class Scrappey:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://publisher.scrappey.com/api/v1'

    def send_request(self, endpoint, data=None):
        url = f'{self.base_url}?key={self.api_key}'

        headers = {
            'Content-Type': 'application/json'
        }

        payload = {
            'cmd': endpoint,
            **data
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            raise error

    def create_session(self, data):
        return self.send_request(endpoint='sessions.create', data=data)

    def destroy_session(self, session):
        if session is None:
            raise ValueError('session parameter is required.')
        return self.send_request(endpoint='sessions.destroy', data={'session': session})

    def request(self, data):
        if data is None:
            raise ValueError('data parameter is required.')
        
        if data['cmd'] is None:
            raise ValueError('data.cmd parameter is required.')

        return self.send_request(endpoint=data['cmd'], data=data)