import re
import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime, timedelta
import tweepy as tw
import pandas as pd
import collections
import re
from wordcloud import WordCloud, STOPWORDS


class tweet_sentiments(object):
    '''
    Generic tweets_sentiments Class for the App to get sentiments for last 7 days
    '''
    
    def __init__(self, query):
        
        # keys and tokens from the Twitter Dev Console
        consumer_key= ''
        consumer_secret= ''
        access_token= ''
        access_token_secret= ''
        
        
        try:
            self.auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
            self.auth.set_access_token(access_token, access_token_secret)
            self.api      = tweepy.API(self.auth, wait_on_rate_limit=True)
            self.query    = query
            self.analyzer = SentimentIntensityAnalyzer()
            self.no_days  = 8
            self.tweet_count_max = 20  # To prevent Rate Limiting
            self.word = []
        except:
            
            print("Error: Authentication Failed")
    
    
    def clean_text(self,txt):
        
        text = " ".join(re.sub("([^0-9A-Za-z \t])|(\w+:\/\/\S+)", "", txt).split())
        
        ign_words = re.sub('[^0-9a-zA-Z]','', self.query)
        STOPWORDS.add(ign_words)
        new_words = text.split(" ")
        new_words = [w for w in new_words if len(w) > 2]  # ignore a, an, be, ...
        new_words = [w.lower() for w in new_words]
        new_words = [w for w in new_words if w not in STOPWORDS]
        self.word.extend(new_words)
        return text


    def pred_sentiments(self,txt):
        
        text = self.clean_text(txt)
        pol  = self.analyzer.polarity_scores(text)
        
        if pol['compound'] >= 0.05:
            return 'positive'
        elif ((pol['compound'] > -0.05) and (pol['compound'] < 0.05)):
            return 'neutral'
        elif pol['compound'] <= -0.05:
            return 'negative'
        
        
    def get_tweet_sentiment(self):
        
        end_date   = datetime.today() 
        start_date = datetime.today() - timedelta(days=self.no_days)
        delta      = timedelta(days=1)

        df = pd.DataFrame(columns=['Date',
                                    'positive', 
                                        'negative', 
                                            'neutral'])
        try:
            while start_date <= end_date:
                date = start_date.strftime("%Y-%m-%d")
                date_since = start_date.strftime("%Y-%m-%d")
                start_date += delta
                date_until = start_date.strftime("%Y-%m-%d")
                tweets = tw.Cursor(self.api.search, 
                                        q=self.query + " -filter:retweets", 
                                            lang="en", 
                                                since=date_since, 
                                                    until=date_until).items(self.tweet_count_max)
                tweets_new = [self.pred_sentiments(tweet.text) for tweet in tweets]
                dict_tweet = dict(collections.Counter(tweets_new))
                dict_tweet['Date'] = date
                df = df.append(dict_tweet, ignore_index=True)
                
            return [df,self.word]
        
        except tweepy.TweepError as e:
            
            print("Error : " + str(e))
        
