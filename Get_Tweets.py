from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
import time
import pandas as pd
from textblob import TextBlob
from reference import consumer_key, consumer_key_secret, access_token, access_token_secret

auth = tweepy.OAuthHandler(consumer_key, consumer_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

search_words = "gillette OR @Gillette OR to:Gillette -stadium -filter:retweets -from:Gillette -#sponsored"
date_since = "2018-06-16"


# Additional paramaters per https://github.com/KTakatsuji/Twitter-Sentiment-Naive-Bayes/blob/master/NaiveBayes/part1.py

count = 0
start = 0
errorCount=0

#here we tell the program how fast to search 
waitquery = 100      #this is the number of searches it will do before resting
waittime = 2.0          # this is the length of time we tell our program to rest
total_number = 130     #this is the total number of queries we want
justincase = 1         #this is the number of minutes to wait just in case twitter throttles us
results = []

users =tweepy.Cursor(api.search,
              q=search_words,
              lang="en",
              since=date_since).items()

# functions that allow waiting
text = [0] * total_number
secondcount = 0
idvalues = [1] * total_number
 #1 is happy; 2 is sad; 3 is angry; 4 is fearful
#Below is where the magic happens and the queries are being made according to our desires above
while secondcount < total_number:
    try:
        user = next(users)
        count += 1
        
        #We say that after every 100 searches wait 5 seconds
        if (count%waitquery == 0):
            time.sleep(waittime)
            #break

    except tweepy.TweepError:
        #catches TweepError when rate limiting occurs, sleeps, then restarts.
        #nominally 15 minnutes, make a bit longer to avoid attention.
        print("sleeping....")
        time.sleep(60*justincase)
        user = next(users)

        if StopIteration:
            print ("Stop Iteration envoked")
            break

    # except StopIteration:
    #     break
    
    try:
        results.append(user.text)
        secondcount = secondcount + 1
        print("current saved is:"+str(secondcount))

    except UnicodeEncodeError:
        errorCount += 1
        print("UnicodeEncodeError,errorCount ="+str(errorCount))


all_tweet_data = pd.DataFrame()

for tweet in results:
    analysis = TextBlob(tweet)
    polarity = analysis.polarity
    if analysis.sentiment[0]>0:
       tone = "positive"
    elif analysis.sentiment[0]<0:
       tone = "negative"
    else:
       tone = "neutral"
    all_tweet_data = all_tweet_data.append({'Text': tweet, 'Sentiment': tone, 'Polarity': polarity}, ignore_index=True)
    
all_tweet_data

# train_data = pd.DataFrame()

# counter = 1

# for index, i in all_tweet_data.iterrows():
#     if counter % 2 == 0:
#         train_data = train_data.append({'Text': i[1], 'Score': i[0]}, ignore_index=True)
#     else:
#         test_data = test_data.append({'Text': i[1], 'Score': i[0]}, ignore_index=True)
#     counter += 1

all_tweet_data.to_csv("Data/TwitterAnalysis.csv")
