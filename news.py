"""This file processes the news data and saves it to a JSON file."""

# API: https://www.marketaux.com/documentation

import os
import configparser
from datetime import datetime, timedelta
import json
import requests


class News:
    """The class for getting the news information and their sentiments."""

    def __init__(self):

        self.api_token = os.getenv("MARKETAUX_API_TOKEN")

        config = configparser.ConfigParser()
        config.read("config.ini")

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

    def get_news(self, ticker):
        """Return the news data for said company."""
        # build the request
        url = "https://api.marketaux.com/v1/news/all?" + \
              "symbols=" + ticker + \
              "&filter_entities=true" + \
              "&published_after=" + (datetime.today() - timedelta(days=14)).strftime("%Y-%m-%d") + \
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
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                print("Error: " + str(response.status_code))
                article_counts.append(-1)
                articles.append([])
                continue

            data = response.json()

            article_counts.append(data["meta"]["found"])
            articles.append(data["data"])

        # save the data to a JSON file

        # check if the directory exists
        if not os.path.exists("data/news"):
            os.mkdir("data/news")

        with open("data/news/" + ticker + ".json", "w", encoding="utf-8") as file:
            json.dump({
                "time": str(datetime.today().date()),
                "article_counts": article_counts,
                "articles": articles
            }, file, indent=4)

    def load_news(self, ticker):
        """Load the news data for said company."""

        # check if the directory exists
        if not os.path.exists("data/news"):
            os.mkdir("data/news")

        # check if the file exists
        if not os.path.exists("data/news/" + ticker + ".json"):
            self.get_news(ticker)

        with open("data/news/" + ticker + ".json", "r", encoding="utf-8") as file:
            data = json.load(file)
            if data["time"] != str(datetime.today().date()):
                print("Updating news data for " + ticker + "...")
                self.get_news(ticker)
                return self.load_news(ticker)

            return [data["article_counts"], data["articles"]]


news = News()
news.load_news("MSFT")
