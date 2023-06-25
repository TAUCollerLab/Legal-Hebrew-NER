import configparser
import requests
import pandas as pd
from collections import defaultdict


def lighttag_connection() -> str:

    config = configparser.ConfigParser()
    config.read('conf.ini')

    LIGHTTAG_DOMAIN = config['Credentials']['LIGHTTAG_DOMAIN']
    SERVER = f'https://{LIGHTTAG_DOMAIN}.lighttag.io/api/'
    API_BASE = SERVER + 'v1/'
    MY_USER = config['Credentials']['User_name']
    MY_PWD = config['Credentials']['Password']

    response = requests.post(
        SERVER+'auth/token/login/', json={"username": MY_USER, "password": MY_PWD})

    assert response.status_code == 200, "Couldn't authenticate"
    auth_details = response.json()
    token = auth_details['key']
    assert auth_details['is_manager'] == 1, "Not a manager"  # Check you are a manager

    session = requests.session()
    session.headers.update({"Authorization": "Token {token}".format(token=token)})

    reg_task_url = config['Reg_task']['reg_url']
    json_data = session.get(reg_task_url+'download/').json()  # returns a list of jsons - sized by number of paragraphs
    json_data_examples = json_data['examples']

    return json_data_examples


def logging_annotators(file_name: str, update: bool = False) -> None:
    """"
    use file_name = participants_id_07_05.txt for example.
    change update to True only when logging Prolifics data.
    examples variable creates a dataframe out of LightTags json output.

    """
    examples = pd.DataFrame(lighttag_connection())
    list_comments = examples['comments'].to_list()
    def_dict = defaultdict(str)
    for comment in list_comments:
        for dict_comment in comment:
            def_dict[dict_comment['text']] = dict_comment['made_by_id']

    if update:
        with open(file_name, 'w') as file:
            for key in list(def_dict.keys()):
                file.write(key + "\n")


# import subprocess
# subprocess.run('pylint results_analysis.py > pylint_testing_20042023.txt', shell=True)
