import requests
import json

from tastypie.models import ApiKey

from pin.api.http import return_json_data, return_not_found


def authorization():
    status = True
    payload = {'client_id': '5731b82a-346c-4a37-8801-087d2e65ec48',
               'response_type': 'code', 'scope': 'write', 'access_type': 'offline',
               'redirect_uri': 'http://www.wisgoon.com/shop/hesabit/redirect'}

    url = 'https://www.hesabit.com/oauth2/authorize'
    request = requests.get(url, params=payload, headers={'Content-Type': 'application/json'})
    if int(request.status_code) != 200:
        status = False
    return status


def get_access_token(request):
    client_id = '5731b82a-346c-4a37-8801-087d2e65ec48'
    client_secret = '5731b82a-c364-48a7-8c87-087d2e65ec48'
    token_json = None
    request_token = None

    code = request.GET.get('code', False)
    if code:
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': 'http://www.wisgoon.com/shop/hesabit/redirect',
            'client_id': client_id,
            'client_secret': client_secret
        }

        request_token = requests.post('https://api.hesabit.com/oauth2/token', data=payload)
        token_json = json.loads(request_token.content)
    else:
        token_json = json.loads(request.body)

    try:
        api_key, created = ApiKey.objects.get_or_create(user_id=1680216)
    except:
        return return_not_found()

    api_key.key = token_json['access_token']
    api_key.save()

    return return_json_data({'token': token_json})


# def refresh_token():
#     client_id = '5731b82a-346c-4a37-8801-087d2e65ec48'
#     client_secret = '5731b82a-c364-48a7-8c87-087d2e65ec48'
#     token_json = None
#     request_token = None


#     payload = {
#         'grant_type': 'refresh_token',
#         'code': code,
#         'redirect_uri': 'http://www.wisgoon.com/shop/hesabit/redirect',
#         'client_id': client_id,
#         'client_secret': client_secret
#     }

#     request_token = requests.post('https://api.hesabit.com/oauth2/token', data=payload)
