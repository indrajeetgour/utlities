import json
from datetime import date
import datetime
from datetime import timedelta
import requests
from pprint import pprint

from requests import HTTPError

# todo: X-Rundeck-Auth-Token will come from ADO lib only
headers = {
    'X-Rundeck-Auth-Token': 'your_token',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}


def list_rundeck_tokens():
    token_list = {'to_be_cleaned_up': list(), 'to_be_regen': list(dict())}
    print(type(token_list['to_be_cleaned_up']))
    print(type(token_list['to_be_regen']))

    url = "https://rundeck_url:4443/api/40/tokens/igour"
    # Todo: check if the user igour will be replaced by some service account

    response = requests.request("GET", url, headers=headers, verify=False)
    all_tokens = response.json()

    for token in all_tokens:
        if token['expired']:  # token which is expired
            print("Token which has expired!!!")
            pprint(token['name'])
            token_id = token['id']
            pprint(token['id'])
            pprint(token['expired'])
            # clean up expired token
            # clean_expired_token(token_id)
            if token_list['to_be_cleaned_up']:  # token_list['to_be_cleaned_up'] is not empty
                token_list['to_be_cleaned_up'].append(token_id)
            else:  # token_list['to_be_cleaned_up'] is empty
                token_list['to_be_cleaned_up'] = [token_id]
        else:
            # print("Token which will about to expire in a week or less!!")
            curr_date = date.today()
            # print('curr_date', curr_date)
            token_expire_date = datetime.datetime.strptime(token['expiration'], "%Y-%m-%dT%H:%M:%SZ").date()
            # print('token_expire_date', token_expire_date)
            date_a_week_ahead = curr_date + timedelta(days=7)
            # put the right name for token
            if token['name'] == "testing-rundeck-regen" and date_a_week_ahead >= token_expire_date:
                print("Following token is about to expired...")
                print(
                    "==> Token name: {} with id: {} is about to expired with date: {} ".format(token['name'],
                                                                                               token['id'],
                                                                                               token_expire_date))
                token_info = {'token_name': token['name'], 'token_id': token['id']}
                if token_list['to_be_regen']:
                    token_list['to_be_regen'].append(token_info)
                    # token_list['to_be_regen']['token_id'] = token['id']
                else:
                    token_list['to_be_regen'] = [token_info]

    return token_list


def clean_expired_token(tokens_to_clean):
    for token_id in tokens_to_clean:
        url = "https://rundeck_url:4443/api/40/token/" + token_id
        response = requests.request("DELETE", url, headers=headers, verify=False)
        response_code = response.status_code
        print("response_code: ", str(response_code))
        print("response: ", str(response))
        print("response: ", str(response.text))

        if response_code == 204:
            print("Token is successfully deleted: ", str(token_id))
        else:
            print("Token is already deleted: " + str(token_id) + "!! Not Found!! ")


def generate_new_token(token_to_be_regen):
    if len(token_to_be_regen) > 1:
        # delete one token
        print(token_to_be_regen)
        # print(token_to_be_regen[1])

        url = "https://rundeck_url:4443/api/40/tokens/igour"

        payload = json.dumps({
            "roles": "ldap_role_group",
            "name": token_to_be_regen[0]['token_name']
        })
        try:
            response = requests.request("POST", url, headers=headers, data=payload, verify=False)
            response.raise_for_status()
            # access JSOn content
            post_call_response = response.json()
            print(post_call_response['user'])
            print(post_call_response['token'])
            print(post_call_response['id'])
            print(post_call_response['name'])
            # if response.status_code == 201:
            #     print(response.json())
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')

        # once the token is generated store it into ADO lib
        # store post_call_response['token'] into ADO lib


if __name__ == '__main__':
    # List all the token for user
    token_to_clean = list_rundeck_tokens()
    print(token_to_clean)

    # check if we have expired token currently
    if token_to_clean['to_be_cleaned_up']:
        print("Token expired, which need to be cleaned up: ", token_to_clean['to_be_cleaned_up'])
        clean_expired_token(token_to_clean['to_be_cleaned_up'])
    else:
        print("No token is expired, currently as of now: ", datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # regen token
    generate_new_token(token_to_clean['to_be_regen'])
