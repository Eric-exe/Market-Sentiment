"""
This file processes the news data and returns the sentiment score for said company.
It also saves the data to a JSON file for later use.
"""

# API: https://www.marketaux.com/documentation

import os
import configparser
from datetime import datetime, timedelta
from dotenv import load_dotenv
import requests

import utils.dict_compress as dict_compress


class News:
    """The class for getting the news information and their sentiments."""

    def __init__(self, data):

        self.data = data

        load_dotenv()
        self.api_token = os.getenv("MARKETAUX_API_TOKEN")

        config = configparser.ConfigParser()
        config.read("config/config.ini")

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

    def get_news(self, ticker, database):
        """Return the news data for said company."""
        # build the request
        url = "https://api.marketaux.com/v1/news/all?" + \
              "symbols=" + ticker + \
              "&filter_entities=true" + \
              "&published_after=" + \
              (datetime.today() - timedelta(days=int(self.days_range))).strftime("%Y-%m-%d") + \
              "&sort=entity_match_score" + \
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

        labels = ["weak_positive", "moderate_positive", "strong_positive",
                  "weak_negative", "moderate_negative", "strong_negative"]

        article_counts = {}
        articles = {}

        # send the requests
        for i in range(len(urls)):
            response = requests.get(urls[i], timeout=60)

            if response.status_code != 200:
                print("Error: " + str(response.status_code))
                return False

            data = response.json()

            article_counts[labels[i]] = data["meta"]["found"]

            # news articles
            news_articles = data["data"]  # list of dictionaries
            articles[labels[i]] = []

            for article in news_articles:
                articles[labels[i]].append({
                    "title": article["title"],
                    "description": article["description"],
                    "url": article["url"],
                    "published_at": article["published_at"],
                })

            # marketaux has a 60 api request per minute limit
            # luckily, we only need to make 60 requests (10 companies * 6 sentiments)
            # if you want to add more companies, you need to add a delay here
            # sleep(some time)

        self.data.news[ticker] = articles
        self.data.news_count[ticker] = article_counts
        self.data.sentiment[ticker] = self.get_sentiment(article_counts)
        self.data.news_date_logged[ticker] = datetime.now()

        # save to firebase
        # we save it for each ticker so that we don't lost data if the program crashes
        ticker_data = {
            "news_date_logged": str(self.data.news_date_logged[ticker]),
            "news_count": self.data.news_count[ticker],
            "sentiment": self.data.sentiment[ticker],
            "news_compressed": dict_compress.compress_data(self.data.news[ticker])
        }
        database.add_news_data(ticker, ticker_data)

        return True

    def get_sentiment(self, sentiments):
        """Return a sentiment score given article counts."""
        data = sentiments
        # calculate the sentiment score
        # check if any article count < 0 (error)
        for key in data:
            if data[key] < 0:
                return 0

        sentiment_score = 0

        sentiment_score += data["weak_positive"] * \
            int(self.sentiment_weight[0])
        sentiment_score += data["moderate_positive"] * \
            int(self.sentiment_weight[1])
        sentiment_score += data["strong_positive"] * \
            int(self.sentiment_weight[2])

        sentiment_score -= data["weak_negative"] * \
            int(self.sentiment_weight[0])
        sentiment_score -= data["moderate_negative"] * \
            int(self.sentiment_weight[1])
        sentiment_score -= data["strong_negative"] * \
            int(self.sentiment_weight[2])

        # normalize the sentiment score and add the extra bayesian values
        sentiment_score /= ((data["weak_positive"] + data["weak_negative"]) * int(self.sentiment_weight[0]) +
                            (data["moderate_positive"] + data["moderate_negative"]) * int(self.sentiment_weight[1]) +
                            (data["strong_positive"] + data["strong_negative"]) * int(self.sentiment_weight[2]) +
                            int(self.bayesian_extra_values))

        return sentiment_score

    def save_news(self, database):
        """Update the news data for all companies."""

        # check if we already have the news data for today
        # check if the datetime is defined
        if (self.data.news_date_logged_all is not None and
                datetime.now() - self.data.news_date_logged_all <= timedelta(hours=24) and
                self.data.news_is_complete == True):
            return

        for ticker in self.data.tickers:
            # fetch from firebase first
            ticker_data = database.get_news_data_ticker(ticker)
            # check if the data is up to date
            if ticker_data is not None and ticker_data.get("news_date_logged") != None:

                date = datetime.strptime(ticker_data["news_date_logged"], "%Y-%m-%d %H:%M:%S.%f")

                if datetime.now() - date < timedelta(hours=24):
                    self.data.news[ticker] = dict_compress.decompress_data(ticker_data["news_compressed"])
                    self.data.news_count[ticker] = ticker_data["news_count"]
                    self.data.sentiment[ticker] = ticker_data["sentiment"]
                    self.data.news_date_logged[ticker] = ticker_data["news_date_logged"]
                    continue

            if not self.get_news(ticker, database):
                # ran into an error, stop processing
                return

        self.data.news_date_logged_all = datetime.now()
        self.data.news_is_complete = True

        # update meta in firebase
        meta = {
            "news_is_complete": str(self.data.news_is_complete),
            "news_date_logged_all": str(self.data.news_date_logged_all)
        }

        database.add_news_meta(meta)

    def get_news_data(self, request_time):
        """Return the news data for all companies as a dictionary."""
        response = {
            "meta": {},
            "data": {}
        }

        response["meta"]["request_time"] = request_time
        response["meta"]["news_is_complete"] = str(self.data.news_is_complete)
        response["meta"]["news_date_logged_all"] = str(self.data.news_date_logged_all)

        for ticker in self.data.tickers:
            response["data"][ticker] = {
                "news_count": self.data.news_count[ticker],
                "sentiment": self.data.sentiment[ticker],
                "news": self.data.news[ticker]
            }

        return response

    def load_news_data(self, database):
        """Load the news data from the database."""

        # first, check if the data we have is recent
        if (self.data.news_is_complete and
                datetime.now() - self.data.news_date_logged_all < timedelta(hours=24)):
            print("Using cached news data", flush=True)
            return True

        meta = database.get_news_meta()

        if meta is None:
            return False
        
        # check if the data is complete
        news_date_logged_all = meta.get("news_date_logged_all")
        if news_date_logged_all is None:
            return False
        
        news_is_complete = meta.get("news_is_complete")
        if news_is_complete is None:
            return False
        
        news_is_complete = bool(news_is_complete)
        if news_is_complete is False:
            return False

        # check if the data is recent
        news_date_logged_all = datetime.strptime(
            news_date_logged_all, "%Y-%m-%d %H:%M:%S.%f")

        if datetime.now() - news_date_logged_all > timedelta(hours=24):
            return False

        # the data is recent, load data from firebase
        data = database.get_news_data()

        for ticker in data:
            self.data.news_count[ticker] = data[ticker]["news_count"]
            self.data.sentiment[ticker] = data[ticker]["sentiment"]
            self.data.news[ticker] = dict_compress.decompress_data(data[ticker]["news_compressed"])
            self.data.news_date_logged[ticker] = data[ticker]["news_date_logged"]

        self.data.news_date_logged_all = news_date_logged_all
        self.data.news_is_complete = True

        return True
