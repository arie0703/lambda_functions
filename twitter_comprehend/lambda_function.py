import tweepy
import boto3
import os
import datetime as dt
import json
import requests

TWITTER_API_KEY = os.environ["TWITTER_API_KEY"]
TWITTER_API_SECRET = os.environ["TWITTER_API_SECRET"]
TWITTER_BEARER_TOKEN = os.environ["TWITTER_BEARER_TOKEN"]
TWITTER_ACCESS_TOKEN = os.environ["TWITTER_ACCESS_TOKEN"]
TWITTER_ACCESS_SECRET = os.environ["TWITTER_ACCESS_SECRET"]
NEWRELIC_KEY = os.environ["NEWRELIC_KEY"]
NEWRELIC_ENDPOINT = os.environ["NEWRELIC_ENDPOINT"]

client = tweepy.Client(bearer_token=TWITTER_BEARER_TOKEN,
                        consumer_key=TWITTER_API_KEY,
                        consumer_secret=TWITTER_API_SECRET,
                        access_token=TWITTER_ACCESS_TOKEN,
                        access_token_secret=TWITTER_ACCESS_SECRET
                    )

comprehend = boto3.client('comprehend')

def get_formatted_datetime(fmt, now):
    return dt.datetime.strftime(now, fmt)

def get_sentiment_score(target):
    sentiment = comprehend.detect_sentiment(Text=target, LanguageCode='ja')
    return sentiment.get('SentimentScore')

def post_newrelic(data):
    headers = {"X-Insert-Key": NEWRELIC_KEY}
    res = requests.post(NEWRELIC_ENDPOINT, headers=headers, json=data)
    return res

def lambda_handler(event,context):

    # twitterのcreated_atはUTCになってる。JSTで時刻を合わせてやる
    fmt = "%Y-%m-%dT15:00:00Z"
    JST = dt.timezone(dt.timedelta(hours=9), 'JST')
    now = dt.datetime.now(JST)
    start_today = get_formatted_datetime(fmt, now - dt.timedelta(days=1))
    now_formatted = get_formatted_datetime("%Y-%m-%dT%H:%M:%SZ",now)


    user = client.get_me()
    tweets = client.get_users_tweets(id = user.data.id,
                                    exclude=("replies"),
                                    start_time=start_today,
                                    end_time=now_formatted
                                    )
    tweets_data = tweets.data


    print(tweets_data, start_today, now_formatted)

    data = []
    if tweets_data != None:
        for i, tweet in enumerate(tweets_data):
            result = get_sentiment_score(tweet.text)
            # print (result)

            result.pop('Mixed') # Mixedは数値が不安定なので取り除く
            score = result['Positive'] - result['Negative']
            label = max(result, key=result.get)

            if label == 'Positive':
                label = 'ポジティブ'
            elif label == 'Negative':
                label = 'ネガティブ'
            else:
                label = 'ニュートラル'

            d = {}
            d["eventType"] = "test_twitter"
            d["positive_score"] = result['Positive']
            d["negative_score"] = result['Negative']
            d["score"] = score
            d["label"] = label
            d["tweet"] = tweet.text
            data.append(d)  

            print(d)

    # dryrunするときはコメントアウトしとく
    print(post_newrelic(data))

    return 200