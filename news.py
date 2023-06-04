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

        self.days_range = config["MISC"]["DAYS_RANGE"]
        self.bayesian_extra_values = config["MISC"]["BAYESIAN_EXTRA_VALUES"]

    def get_news(self, ticker):
        """Return the news data for said company."""
        # build the request
        url = "https://api.marketaux.com/v1/news/all?" + \
              "symbols=" + ticker + \
              "&filter_entities=true" + \
              "&published_after=" + \
              (datetime.today() - timedelta(days=self.days_range)).strftime("%Y-%m-%d") + \
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


    def get_sentiment(self, ticker):
        """Return a sentiment score for said company."""
        # load the news data
        data = self.load_news(ticker)

        # calculate the sentiment score
        sentiment_score = 0
        for i in range(3):
            sentiment_score += data[0][i] * int(self.sentiment_weight[i])

        for i in range(3):
            sentiment_score -= data[0][i + 3] * int(self.sentiment_weight[i])

        # normalize the sentiment score and add the extra bayesian values
        sentiment_score /= ((data[0][0] + data[0][3]) * int(self.sentiment_weight[0]) +
                            (data[0][1] + data[0][4]) * int(self.sentiment_weight[1]) +
                            (data[0][2] + data[0][5]) * int(self.sentiment_weight[2]) +
                            int(self.bayesian_extra_values))


        return [sentiment_score, sum(data[0])]


news = News()
print(news.get_sentiment("MSFT"))
