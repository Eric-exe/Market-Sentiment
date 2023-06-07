"""
This file processes the news data and returns the sentiment score for said company.
It also saves the data to a JSON file for later use.
"""

# API: https://www.marketaux.com/documentation

import os
import time
import configparser
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests


class News:
    """The class for getting the news information and their sentiments."""

    def __init__(self, data):

        self.data = data
        self.data.news = {}
        self.data.sentiment = {}
        self.data.news_count = {}
        self.data.news_date_logged = {}

        load_dotenv()
        self.api_token = os.getenv("MARKETAUX_API_TOKEN")

        config = configparser.ConfigParser()
        config.read("api/config.ini")

        self.sentiment_range = [
            config["SENTIMENT_RANGE"]["WEAK_BEGIN"],
            config["SENTIMENT_RANGE"]["WEAK_END"],
            config["SENTIMENT_RANGE"]["MODERATE_BEGIN"],
            config["SENTIMENT_RANGE"]["MODERATE_END"],
            config["SENTIMENT_RANGE"]["STRONG_BEGIN"],
            config["SENTIMENT_RANGE"]["STRONG_END"]
        ]

        self.sentiment_weight = [
            config["SENTIMENT_WEIGHT"]["WEAK"],
            config["SENTIMENT_WEIGHT"]["MODERATE"],
            config["SENTIMENT_WEIGHT"]["STRONG"]
        ]

        self.days_range = config["MISC"]["DAYS_RANGE"]
        self.bayesian_extra_values = config["MISC"]["BAYESIAN_EXTRA_VALUES"]

    def get_news(self, ticker):
        """Return the news data for said company."""
        # build the request
        url = "https://api.marketaux.com/v1/news/all?" + \
              "symbols=" + ticker + \
              "&filter_entities=true" + \
              "&published_after=" + \
              (datetime.today() - timedelta(days=int(self.days_range))).strftime("%Y-%m-%d") + \
              "&sort=published_on" + \
              "&api_token=" + self.api_token

        urls = []
        # create the requests for all sentiment ranges
        for i in range(0, len(self.sentiment_range), 2):
            sentiment = "&sentiment_gte=" + self.sentiment_range[i] + \
                        "&sentiment_lte=" + self.sentiment_range[i + 1]
            url += sentiment
            urls.append(url)
            url = url[:-len(sentiment)]

        # negative sentiment
        for i in range(0, len(self.sentiment_range), 2):
            sentiment = "&sentiment_gte=-" + self.sentiment_range[i + 1] + \
                        "&sentiment_lte=-" + self.sentiment_range[i]
            url += sentiment
            urls.append(url)
            url = url[:-len(sentiment)]

        article_counts = []
        articles = []

        # send the requests
        for url in urls:
            response = requests.get(url, timeout=60)

            if response.status_code != 200:
                print("Error: " + str(response.status_code))
                article_counts.append(-1)
                articles.append([])
                continue

            data = response.json()

            article_counts.append(data["meta"]["found"])
            articles.append(data["data"])

            # wait for 1 second to avoid rate limit
            time.sleep(1)

        self.data.news[ticker] = articles
        self.data.news_count[ticker] = article_counts
        self.data.news_date_logged[ticker] = datetime.today().date()
        self.data.sentiment[ticker] = self.get_sentiment(article_counts)

    def load_news(self, ticker):
        """Load the news data for said company. Use this function instead of get_news()"""
        # check if the news data is already loaded
        if ticker in self.data.news_date_logged:
            # check if the news data is up to date
            if self.data.news_date_logged[ticker] == datetime.today().date():
                return [self.data.news_count[ticker], self.data.news[ticker]]

        self.get_news(ticker)
        return [self.data.sentiment[ticker], self.data.news[ticker]]

    def get_sentiment(self, sentiments):
        """Return a sentiment score given article counts."""
        data = sentiments
        # calculate the sentiment score
        sentiment_score = 0
        for i in range(3):
            sentiment_score += data[i] * int(self.sentiment_weight[i])

        for i in range(3):
            sentiment_score -= data[i + 3] * int(self.sentiment_weight[i])

        # normalize the sentiment score and add the extra bayesian values
        sentiment_score /= ((data[0] + data[3]) * int(self.sentiment_weight[0]) +
                            (data[1] + data[4]) * int(self.sentiment_weight[1]) +
                            (data[2] + data[5]) * int(self.sentiment_weight[2]) +
                            int(self.bayesian_extra_values))

        return sentiment_score

    def save_news(self):
        """Update the news data for all companies."""
        for ticker in self.data.tickers:
            if ticker in self.data.news_date_logged:
                continue
            self.load_news(ticker)
