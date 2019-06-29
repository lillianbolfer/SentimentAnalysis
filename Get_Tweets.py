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
total_number = 20     #this is the total number of queries we want
justincase = 1         #this is the number of minutes to wait just in case twitter throttles us
results = pd.DataFrame()

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
        results = results.append({"Text": user.text, "Date": user.created_at}, ignore_index=True)
        secondcount = secondcount + 1
        print("current saved is:"+str(secondcount))

    except UnicodeEncodeError:
        errorCount += 1
        print("UnicodeEncodeError,errorCount ="+str(errorCount))


all_tweet_data = pd.DataFrame()

for index, row in results.iterrows():
    analysis = TextBlob(row[1])
    polarity = analysis.polarity
    subjectivity = analysis.subjectivity
    no_tagged = row[1].count('@')
    word_count = row[1].count(' ')+1
    char_count = len(row[1])
    if analysis.sentiment[0]>0:
       tone = "positive"
    elif analysis.sentiment[0]<0:
       tone = "negative"
    else:
       tone = "neutral"
    all_tweet_data = all_tweet_data.append({'Date': row[0], 'Text': row[1], 'Sentiment': tone, 'Polarity': polarity, 'Subjectivity': subjectivity, 'Number Tagged': no_tagged, 'Word Count': word_count, 'Character Count': char_count}, ignore_index=True)
    
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

# Dataframe with word frequency
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 

join_str = ' '.join(all_tweet_data.Text)
stop_list = set(stopwords.words('english')) 

print("***CHECK ONE***")
print(stop_list)

wordcount = pd.Series(' '.join(all_tweet_data.Text).split()).str.lower().value_counts()
print("***CHECK TWO***")
print(wordcount.head())

# for index, row in wordcount.iteritems():
#     if row in stop_list:
#         #IGNORED wordcount = wordcount.drop(index, inplace=True)
#         #IGNORED wordcount = np.delete(wordcount, row)


print("***CHECK THREE***")
print(wordcount.head())

wordcount_df = pd.DataFrame({'Word': wordcount.index, 'Count': wordcount.values})
#IGNORED wordcount_df = pd.DataFrame({'Word': wordcount.index})
#IGNORED wordcount_df[~wordcount_df['Word'].isin(stop_list)]

wordcount_df.sort_values(by="Count",ascending=False, inplace=True)
print("***CHECK FOUR***")
print(wordcount_df.head())

wordcount_df.to_csv("Data/WordCount.csv")

# wordcount_df = pd.DataFrame({'a':list('abssbab')})
# df.groupby('a').count()
