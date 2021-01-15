# Vader Sentiments created on DASH python

It is a sentiment analyzer dashboard based on VADER Sentiments and created in python with Dash framework. 

The output of the dash has below three features:

- Stock ticker's cummulative returns based on the dynamic data extracted from Yahoo Finance
- Sentiment Analysis based on the keyword entered. In output it gives the trend of Sentiments between positive and negative for last 7 days as per the allowed twitter API limitation.
- Wordcloud is created based on the total tweets fetched

# The Dash - Dashboard

![](assets/sentiment_analysis.gif)

# Things to ADD:

Please configure twitter developer account and add following keys for it to run:

- ``consumer_key``
- ``consumer_secret``
- ``access_token``
- ``access_token_secret``