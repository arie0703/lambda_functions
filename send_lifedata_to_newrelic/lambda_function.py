import json
import boto3
import os
from urllib.parse import parse_qs
import requests

# 特定時刻に最新のキューをNewRelicにポストする関数

NEWRELIC_KEY = os.environ["NEWRELIC_KEY"]
NEWRELIC_ENDPOINT = os.environ["NEWRELIC_ENDPOINT"]

def post_health_data(intake, consumption, sleep_time, count_coffee, weight):
    headers = {"X-Insert-Key": NEWRELIC_KEY}
    d = {}
    d["eventType"] = "health"
    d["intake"] = int(intake)
    d["consumption"] = int(consumption)
    d["sleep_time"] = float(sleep_time)
    d["count_coffee"] = int(count_coffee)
    d["weight"] = float(weight)

    # Test時はここをコメントアウト！
    res = requests.post(NEWRELIC_ENDPOINT, headers=headers, json=d)
    print(res)

    result = ' 投稿完了！  ``` 摂取カロリー: {}kcal \n 消費カロリー: {}kcal \n 睡眠時間: {}hours \n コーヒー: {}cup \n 体重: {}kg ``` '.format(intake, consumption, sleep_time, count_coffee, weight)
    return result

def lambda_handler(event, context):

    queue_url = os.environ["QUEUE_URL"]
    sqs = boto3.client("sqs")
    res = sqs.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1, VisibilityTimeout=30)

    print(res)

    data = res["Messages"][0]['Body'].split(' ')
    receipt_handle = res["Messages"][0]['ReceiptHandle']

    if len(data) != 5:
        message = f"Please specify *five* parameters.\nYou typed: {command}"

    else:
        message = post_health_data(
            data[0], data[1], data[2], data[3], data[4])

        # 取り出したキューは削除
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )

    return {
        "response_type": "ephemeral",
        "text": message
    }