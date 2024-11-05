import requests
from urllib.parse import urlparse, parse_qs
import hashlib
import time

headers = {
    'accept': 'application/json, text/plain, */*',
    'authorization': '',
    'x-requested-with': 'org.telegram.messenger',
}

def make_request(method, url, headers=None, params=None, data=None):
    attempt = 1
    delay = 2
    max_delay = 60

    while True:
        try:
            if method.lower() == 'get':
                response = requests.get(url, headers=headers, params=params)
            elif method.lower() == 'post':
                response = requests.post(url, headers=headers, data=data, params=params)
            if response.status_code == 200:
                return response.json()

        except (requests.ConnectionError, requests.Timeout):
            print(f"Network error. Retrying in {delay} seconds...")

        time.sleep(delay)
        delay = min(delay * 2, max_delay)
        attempt += 1

        if delay >= max_delay:
            print("Max retry limit reached. Cooling down for 1 hour...")
            time.sleep(3600)
            delay = 2

def compute_md5(amount, seq):
    prefix = str(amount) + str(seq) + "7be2a16a82054ee58398c5edb7ac4a5a"
    return hashlib.md5(prefix.encode()).hexdigest()

def auth(url: str) -> dict:
    parsed_url = urlparse(url)
    init = parse_qs(parsed_url.fragment).get('tgWebAppData', [None])[0]
    params = {'invitationCode': '', 'initData': init}
    data = {'invitationCode': '', 'initData': init}
    return make_request('post', 'https://api.freedogs.bot/miniapps/api/user/telegram_auth', headers=headers, params=params, data=data)

def do_click(init):
    headers['authorization'] = 'Bearer ' + auth(init)['data']['token']
    response = make_request('get', 'https://api.freedogs.bot/miniapps/api/user_game_level/GetGameInfo', headers=headers)
    seq = response['data']['collectSeqNo']
    params = {
        'collectAmount': '100000',
        'hashCode': compute_md5('100000', seq),
        'collectSeqNo': str(seq),
    }
    return make_request('post', 'https://api.freedogs.bot/miniapps/api/user_game/collectCoin', headers=headers, data=params)

def get_init_url():
    with open('session.txt', 'r') as file:
        return file.read().strip()

if __name__ == '__main__':
    init_url = get_init_url()
    attempt = 1
    while True:
        result = do_click(init_url)
        print(f"Attempt {attempt}: {result}")
        attempt += 1
        time.sleep(1)
