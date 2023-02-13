import json
from typing import List
import configparser
import requests


def generator_for_samples(path_to_data: str = './sample.json') -> List[str]:
    with open(path_to_data, 'r', encoding='utf8') as json_file:
        for line in json_file:
            yield json.loads(line)  # returns 1 dictionary containing segments list


generator_json = generator_for_samples()
# segments_list.append(" ".join(test1['segments'][0])).
# document['segments'][index = 0] returns list of lists instead of signle value
list_of_segments = []
for document in generator_json:
    segments_list = []  # for each document we need to get from list of list one list of segments.
    for segment in range(len(document['segments'])):
        segments_list.append(" ".join(document['segments'][segment]))  # segment replaces index
    list_of_segments += segments_list  # return type of document[segments] is a list

# changing dictionaries key name first_json['content'] = first_json.pop('segments')
tagging_dataset = [{"id": k, "content": v} for k, v in enumerate(list_of_segments)]  # 637 segments as full dataset.
basic_tags = [
    {
        "name": "אנשים",
        "description": "שמות של בני אדם"
    },
    {
        "name": "מיקום",
        "description": "מקום גיאוגרפי"
    },
    {
        "name": "ארגון",
        "description": "שם של ארגון לדוגמה גוגל"
    },
    {
        "name": "תאריך",
        "description": "תאריכים עבריים ולועזיים"
    }
]

legal_tags = [

    {
        "name": "צדדים",
        "description": "צדדים בתיק, נאשם, תובע, נתבע וכדומה"
    },
    {
        "name": "שופטים",
        "description": "שמות של שופטות ושופטים"
    },
    {
        "name": "בית משפט",
        "description": "בית משפט - עליון, שלום, מחוזי"
    },
    {
        "name": "מספר תיק",
        "description": "תיק משפטי - מספר תיק"
    },

    {
        "name": "עורכי דין מייצגים",
        "description": "Representing lawyers - עורכי דין מייצגים"
    },
    {
        "name": "עדים",
        "description": "עדים במשפט"
    },
    {
        "name": "הוצאות משפטיות",
        "description": "הוצאות משפטיות"
    },
    {
        "name": "קנס",
        "description": "קנס"
    }
]


config = configparser.ConfigParser()
config.read('conf.ini')

LIGHTTAG_DOMAIN = config['Credentials']['LIGHTTAG_DOMAIN']
SERVER = 'https://{domain}.lighttag.io/api/'.format(domain=LIGHTTAG_DOMAIN)
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
# session.get(API_BASE+'projects/').json()
legal_ds = {
    "name": "Legal Dataset",
    "content_field": "content",  # content is the field in the JSON we will be annotating
    "examples": tagging_dataset  # Set the list of examples that are part of this dataset
}

resp = session.post(API_BASE+'projects/default/datasets/bulk/', json=legal_ds)
assert resp.status_code == 201
# datasets = session.get(API_BASE+'projects/default/datasets/').json()  # Get all of the datasets in our project
basic_ner_schema = {
    "name": "Regular NER Schema",
    "tags": basic_tags
}
legal_ner_schema = {
    "name": "Legal NER Schema",
    "tags": legal_tags
}
# uploading schemas(regular NER and legal NER)
resp = session.post(API_BASE+'projects/default/schemas/bulk/', json=basic_ner_schema)
assert resp.status_code == 201
resp = session.post(API_BASE+'projects/default/schemas/bulk/', json=legal_ner_schema)
assert resp.status_code == 201

# slug for both NER tasks - "legal-dataset"

teams = session.get(API_BASE+'projects/default/teams/').json()
teamIds = [x['id'] for x in teams]  # this is everyone and reviewer teams

# defining the Task/Job to be created on lighttag
basic_ner_task = {
    "name": "Regular NER tagging",
    "dataset_slug": "legal-dataset",
    "schema_slug": "regular-ner-schema",
    "annotators_per_example": 3,
    "allow_suggestions": False,  # I don't want my annotators to see what others annotated.
    "teams": [teamIds[0]],
    "models": []
}

legal_ner_task = {
    "name": "Legal NER tagging",
    "dataset_slug": "legal-dataset",
    "schema_slug": "legal-ner-schema",
    "annotators_per_example": 3,
    "allow_suggestions": False,  # I don't want my annotators to see what others annotated.
    "teams": [teamIds[0]],
    "models": []
}
resp = session.post(API_BASE+'projects/default/task_definitions/', json=basic_ner_task)  # you run this line once
assert resp.status_code == 201, basic_ner_task
resp = session.post(API_BASE+'projects/default/task_definitions/', json=legal_ner_task)  # you run this line once
assert resp.status_code == 201, legal_ner_task
