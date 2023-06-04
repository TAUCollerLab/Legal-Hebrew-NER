import configparser
import requests
import pandas as pd
from collections import defaultdict


def lighttag_connection() -> pd.DataFrame:

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

    # regular task id(priority 7 in LightTag) : 2b934f94-8d7c-4db9-8383-d412e772a481
    reg_task_url = config['Reg_task']['reg_url']
    json_data = session.get(reg_task_url+'download/').json()  # returns a list of jsons - sized by number of paragraphs
    json_data_examples = json_data['examples']

    return json_data_examples


def logging_annotators(file_name: str, update: bool = False) -> None:
    """"
    use for example file_name = participants_id_07_05.txt
    change update to True only when logging Prolifics data.
    examples convert Light Tag's output as json to DataFrame.

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


# examples = pd.DataFrame(lighttag_connection())  # convert downloaded task data to a dataframe
# examples = examples[examples['annotations'].str.len() > 0]  # stay only with annotated paragraphs
# examples['num_annotators'] = examples['seen_by'].apply(lambda row: len(row))
# examples = examples[examples['num_annotators'] > 2]


# for writing pylint in python script as shell script:
# import subprocess
# subprocess.run('pylint results_analysis.py > pylint_testing_20042023.txt', shell=True)
