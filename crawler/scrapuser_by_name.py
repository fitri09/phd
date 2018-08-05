#!/usr/bin/env python
# encoding: utf-8


import tweepy   # https://github.com/tweepy/tweepy
import csv
import os
import logging
import json
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
    outtweets = [[
            tweet.id_str,
            tweet.created_at,
            tweet.text.encode("utf-8"),
            tweet.user.screen_name
        ]
        for tweet in alltweets
    ]

    return outtweets


def search_users(query, page=1):
    users = api.search_users(query, per_page=20, page=page)
    return users

def get_screen_name_from_search(query, page=1):

    users = search_users(query, page)
    result = []

    for i in range(0, len(users)):
        user = users[i]._json
        screen_name = user["screen_name"]
        verified = bool(user["verified"])

        if verified:
            return [screen_name]

        if i < 3:
            result.append(screen_name)

    if not result:
        logging.error("'{}' not found".format(query))
        return [""]

    return result


if __name__ == '__main__':
    # pass in the username of the account you want to download
    # get_all_tweets("temanahok")
    # get_all_tweets("Panji Muhammad")

    screen_names = []

    current_path = os.path.abspath(os.path.dirname(__file__))
    dataset_path = "/../dataset/kenya_influencer.csv"
    f = open(current_path + dataset_path)
    content = f.readlines()
    for line in content:
        name = line.strip()
        temp_screen_name = get_screen_name_from_search(query=name)
        screen_names = screen_names + temp_screen_name

    with open('crawler-result/kenya_influencer_tweets.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["tweet_id", "created_at", "text", "screen_name"])

        for name in screen_names:
            outtweets = get_all_tweets(name)
            writer.writerows(outtweets)


    # users = search_users("Robert Alai")
    # for user in users:
    #     user_dict = user._json
    #     name = user_dict["name"]
    #     screen_name = user_dict["screen_name"]
    #     print("name     : {}\nusername : {}\n".format(name, screen_name))
