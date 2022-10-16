import json
import os
from urllib.parse import parse_qs
import requests
import boto3

NEWRELIC_KEY = os.environ["NEWRELIC_KEY"]
NEWRELIC_ENDPOINT = os.environ["NEWRELIC_ENDPOINT"]

def lambda_handler(event, context):

    headers = {"X-Insert-Key": NEWRELIC_KEY}
    d = {}
    d["eventType"] = "health"
    d["count_coffee"] = 1
    res = requests.post(NEWRELIC_ENDPOINT, headers=headers, json=d)
    print(res)

    message = '記録完了！ \n コーヒーの飲み過ぎはほどほどに。'

    return {
        "response_type": "ephemeral",
        "text": message
    }