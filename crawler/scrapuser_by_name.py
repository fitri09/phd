#!/usr/bin/env python
# encoding: utf-8


import tweepy   # https://github.com/tweepy/tweepy
import csv
import os
import logging
from dotenv import load_dotenv

# Load env variable
project_folder = os.path.expanduser('~/Documents/fitri-phd-project')
load_dotenv(os.path.join(project_folder, '.env'))

# Twitter API credentials
consumer_key = os.getenv("TWITTER_CONSUMER_KEY")
consumer_secret = os.getenv("TWITTER_CONSUMER_SECRET")
access_key = os.getenv("TWITTER_ACCESS_KEY")
access_secret = os.getenv("TWITTER_ACCESS_SECRET")

# authorize twitter, initialize tweepy
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth)


def get_all_tweets(screen_name):
    # Twitter only allows access to a users
    # most recent 3240 tweets with this method
    # initialize a list to hold all the tweepy Tweets
    alltweets = []

    # make initial request for
    # most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name=screen_name, count=200)

    # save most recent Tweets
    alltweets.extend(new_tweets)

    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    # oldest = 826569136390144000 - 1
    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:
        print("getting tweets before %s" % (oldest))

        # all subsiquent requests use the max_id param to prevent duplicates
        new_tweets = api.user_timeline(
            screen_name=screen_name,
            count=200, max_id=oldest
        )

        # save most recent tweets
        alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1

        print("...%s tweets downloaded so far" % (len(alltweets)))

    # transform the tweepy tweets into a 2D array that will populate the csv
    outtweets = [
        [tweet.id_str, tweet.created_at, tweet.text.encode("utf-8")]
        for tweet in alltweets
    ]

    # write the csv
    with open('crawler-result/%s_tweets.csv' % screen_name, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["id", "created_at", "text"])
        writer.writerows(outtweets)


if __name__ == '__main__':
    # pass in the username of the account you want to download
    get_all_tweets("temanahok")
    # get_all_tweets("Panji Muhammad")

    current_path = os.path.abspath(os.path.dirname(__file__))
    dataset_path = "/../dataset/kenya_influencer.csv"
    f = open(current_path + dataset_path)
    content = f.readlines()
    for line in content:
        screen_name = line.strip()
        print("Scrapping user " + screen_name)
        get_all_tweets(screen_name)
