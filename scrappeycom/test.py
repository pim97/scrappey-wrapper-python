from scrappey import Scrappey

scrappey = Scrappey('YOUR_API_KEY')

def run_test():
    try:
        session = scrappey.create_session()
        print(session)

        get_request_result = scrappey.get_request('https://reqres.in/api/users', session['session'])
        print('GET Request Result:', get_request_result)

        post_data = {'username': 'user123', 'password': 'pass456'}
        post_request_result = scrappey.post_request('https://reqres.in/api/users', post_data, session['session'])
        print('POST Request Result:', post_request_result)

        scrappey.destroy_session(session['session'])
        print('Session destroyed.')
    except Exception as error:
        print(error)

run_test()
