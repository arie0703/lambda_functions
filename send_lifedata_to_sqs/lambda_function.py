
import json
import os
from urllib.parse import parse_qs
import requests
import boto3

NEWRELIC_KEY = os.environ["NEWRELIC_KEY"]
NEWRELIC_ENDPOINT = os.environ["NEWRELIC_ENDPOINT"]

def send_queue(data):

    queue_url = os.environ["QUEUE_URL"]
    sqs = boto3.client("sqs")
    body = f'{data[0]} {data[1]} {data[2]} {data[3]} {data[4]}'
    print(body)

    sqs.send_message(
        QueueUrl=queue_url, 
        MessageBody=body,
        MessageGroupId="slack_post"
    )

    result = ' 投稿完了！  ``` 摂取カロリー: {}kcal \n 消費カロリー: {}kcal \n 睡眠時間: {}hours \n コーヒー: {}cup \n 体重: {}kg ``` '.format(data[0], data[1], data[2], data[3], data[4])
    return result


def lambda_handler(event, context):
    params = event['text']
    command = event['command'] + ' ' + params
    data = [e for e in params.split(' ')]

    print("Command executed: " + command)

    if len(data) != 5:
        message = f"Please specify *five* parameters.\nYou typed: {command}"

    else:
        message = send_queue(data)

    return {
        "response_type": "ephemeral",
        "text": message
    }