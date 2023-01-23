import requests
import pandas as pd
import configparser
from pprint import pprint  # printing the json files prettier
import json

#  we will use configparser to work with our configuration ini file for requests and data location

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
session.get(API_BASE+'projects/').json()

all_data = json.load(open('./json_verdict_examples.json'))
# pprint(all_data[0])
# pprint("total of {num} examples".format(num=len(all_data)))

exploratory_dataset = {
    "name": "Verdicts Examples Dataset",
    "content_field": "content",  # content is the field in the JSON we will be annotating
    "examples": all_data  # Set the list of examples that are part of this dataset
}

resp = session.post(API_BASE+'projects/default/datasets/bulk/', json=exploratory_dataset)
assert resp.status_code == 201
datasets = session.get(API_BASE+'projects/default/datasets/').json()  # Get all of the datasets in our project
# datasets - run it in case you are running in condole or ipynb.

# defining tags:

tags = [
    {
        "name": "PAR",
        "description": "צדדים בתיק, נאשם, תובע, נתבע וכדומה"
    },
    {
        "name": "JUD",
        "description": "שופטים"
    },
    {
        "name": "COU",
        "description": "בית משפט - עליון, שלום, מחוזי"
    },
    {
        "name": "CASE",
        "description": "תיק משפטי - מספר תיק"
    },
    {
        "name": "RLAW",
        "description": "הפניה לחוק"
    },
    {
        "name": "RCAS",
        "description": "הפניה לפסק דין"
    },
    {
        "name": "AGL",
        "description": "Artificial legal entity - אישיות משפטית מלאכותית לדוגמה חברה בערבון מוגבל, עמותה, הקדש וכדומה"
    },
    {
        "name": "RELA",
        "description": "Representing lawyers - עורכי דין מייצגים"
    },
    {
        "name": "WIT",
        "description": "עדים"
    },
    {
        "name": "EXP",
        "description": "הוצאות משפטיות"
    },
    {
        "name": "PEN",
        "description": "קנס"
    },
    {
        "name": "PRSE",
        "description": "Prison Sentence - עונש מאסר"
    },
    {
        "name": "GA",
        "description": "Government authority - רשות שלטונית"
    },
    {
        "name": "TER",
        "description": "מונחים משפטיים כגון: מבחן מאזן הנוחות של הצדדים לתהליך"
    },
    {
        "name": "RES",
        "description": "תוצאה משפטית - דחייה, קבלה, דחייה חלקית וכולי"
    },
    {
        "name": "DATE",
        "description": "תאריך"
    },
    {
        "name": "LOC",
        "description": "מיקום"
    },
    {
        "name": "PER",
        "description": "אנשים - שמות של אינדיווידואלים"
    },
    {
        "name": "PHONE",
        "description": "מספר טלפון/פלאפון"
    },
    {
        "name": "URL",
        "description": "כתובת אינטרנט"
    },
    {
        "name": "EMAIL",
        "description": "כתובת דואר אלקטרוני"
    }
]
tags_only_schema = {
    "name": "Entity Tags only",
    "tags": tags
}

resp = session.post(API_BASE+'projects/default/schemas/bulk/', json=tags_only_schema)
assert resp.status_code == 201

# session.get(API_BASE+'projects/default/schemas/').json()
# annotators = session.get(API_BASE+'projects/default/annotators/').json()
# review = annotators[1:]
# ReviewTeam = {"name": "Review", "description": "defining a review team for myself-Tim", "members": review}
# session.post(API_BASE+'projects/default/teams/', json=ReviewTeam)
teams = session.get(API_BASE+'projects/default/teams/').json()
teamIds = [x['id'] for x in teams]

tags_only_task = {
    "name": "Verdicts examples task NER",
    "dataset_slug": "verdicts-examples-dataset",
    "schema_slug": "entity-tags-only",
    "annotators_per_example": 3,
    "allow_suggestions": False,  # I don't want my annotators to see what others annotated.
    "teams": [teamIds[0]],
    "models": []
}

resp = session.post(API_BASE+'projects/default/task_definitions/', json=tags_only_task)
assert resp.status_code == 201, tags_only_task

add_annotator = {
    'id': 3,
    'username': 'atalia121098@gmail.com',
    'is_active': True,
    'email': 'atalia121098@gmail.com',
    'is_manager': 0,
    'is_reviewer': 0,
    'teams': ['e6542695-64f5-4525-8274-d3119240cf62'],
    'name': 'atalia121098@gmail.com'
}
session.post(API_BASE+'projects/default/annotators/', json=add_annotator)
