import os
import json
import requests
from dotenv import load_dotenv
import requests


load_dotenv()


OLTSHUB_URL = os.getenv("OLTSHUB_URL")


def get_api(URL, token):
    '''
    Функция делает GET запрос на API OLTsHUB
    '''
    HEADERS = {
    "Authorization": f"{token}",
    }
    try:
        response = requests.get(OLTSHUB_URL+URL, headers=HEADERS, verify=False)
        result = json.loads(json.dumps(response.json(), indent=4))

        return result
    
    except requests.exceptions.ConnectionError:
        return {'result': 'error', 'message': 'Не удалось подключиться к OLTsHUB'}



def post_api_auth(URL, JSON):
    '''
    Функция делает POST запрос на аутентификацию пользователя API OLTsHUB
    '''
    try:
        response = requests.post(OLTSHUB_URL+URL, verify=False, json=JSON)
        result = json.loads(json.dumps(response.json(), indent=4))

        return result

    except requests.exceptions.ConnectionError:
        return {'result': 'error', 'message': 'Не удалось подключиться к OLTsHUB'}


def post_api(URL, token, JSON):
    '''
    Функция делает POST запрос на API OLTsHUB
    '''
    HEADERS = {
    "Authorization": f"{token}",
    }
    pass
    # try:
    #     response = requests.post(OLTSHUB_URL+URL, headers=HEADERS, verify=False, json=JSON)
    #     result = json.loads(json.dumps(response.json(), indent=4))

    #     return result

    # except requests.exceptions.ConnectionError:
    #     return {'result': 'error', 'message': 'Не удалось подключиться к OLTsHUB'}
