"""This file gets the stock information from the API yfinance and saves it to a CSV file."""

from datetime import datetime, timedelta
from yahooquery import Ticker


class Stock:
    """The class for getting the stock information."""

    def __init__(self, data):
        """Initialize the Stock class."""
        self.data = data
        self.get_companies()

    def get_companies(self):
        """Update the company data."""
        # read the company data from the CSV file
        with open('api/data/companies.csv', 'r', encoding="utf-8") as file:
            data = file.read().split("\n")
            data.pop(0)  # remove header
            for company in data:
                company_info = company.split(",")
                name = company_info[0]
                ticker = company_info[1]
                # create a two-way dictionary
                self.data.companies[name] = ticker
                self.data.companies[ticker] = name

                self.data.tickers.append(ticker)

        self.data.closings = {}
        self.data.current_prices = {}

    def save_closings_prices(self):
        """Save the previous closing prices of the companies."""

        # check if we already have logged the previous closing prices
        # update every 60 minutes
        if (self.data.closings_date_logged is None or
                datetime.today().now() - self.data.closings_date_logged >=
                timedelta(minutes=60)):

            # process the closing prices
            for ticker in self.data.tickers:
                self.data.closings[ticker] = []
                # get the closing prices for the last 14 days
                history = Ticker(ticker).history(period="15d")
                closing_prices = history.reset_index(
                )[["date", "close"]].values.tolist()
                # convert the date to string
                closing_prices = [[str(date), price]
                                  for date, price in closing_prices]
                # pop the last closing price, which is today's closing price
                closing_prices.pop()

                self.data.closings[ticker] = closing_prices

                # update the previous closing price
                # use singular ticker instead of batch because it is faster
                self.data.previous_closing[ticker] = Ticker(ticker).price["regularMarketPreviousClose"]

            # update the time we logged the previous closing prices
            self.data.closings_date_logged = datetime.today().now()

    def save_current_prices(self):
        """Save the current prices of the companies. Should update every 30 seconds."""

        if (self.data.current_prices_date_logged is None or
                datetime.today().now() - self.data.current_prices_date_logged >=
                timedelta(seconds=30)):

            # switching to singular ticker instead of batch because it is faster
            for ticker in self.data.tickers:
                data = Ticker(ticker)
                self.data.current_prices[ticker] = data.price[ticker]["regularMarketPrice"]

            self.data.current_prices_date_logged = datetime.today().now()

    def get_stock_change(self, ticker):
        """Return the stock change percentage."""
        current_price = self.data.current_prices[ticker]
        previous_closing = self.data.previous_closing[ticker]
        return (current_price - previous_closing) / previous_closing * 100

    def get_stock_data(self, request_time):
        """Return the stock data in a dictionary."""

        response = {
            "meta": {},
            "data": {}
        }

        response["meta"]["request_time"] = request_time
        response["meta"]["current_prices_date_logged"] = str(
            self.data.current_prices_date_logged)
        response["meta"]["closings_date_logged"] = str(
            self.data.closings_date_logged)

        for ticker in self.data.tickers:
            response["data"][ticker] = {
                "company": self.data.companies[ticker],
                "current_price": self.data.current_prices[ticker],
                "previous_closing_price": self.data.previous_closing[ticker],
                "change": self.get_stock_change(ticker),
                "closings_prices": {}
            }

            for closing in self.data.closings[ticker]:
                response["data"][ticker]["closings_prices"][closing[0]] = closing[1]

        return response

    def load_stock_data(self, database):
        """Loads the stock data from firebase"""
        # check if the stock data in firebase is recent
        meta = database.get_stock_meta()
        if meta is None:
            return

        current_prices_date_logged = meta.get("current_prices_date_logged")
        closings_date_logged = meta.get("closings_date_logged")

        if (current_prices_date_logged is None or closings_date_logged is None):
            return

        current_prices_date_logged = datetime.strptime(current_prices_date_logged, "%Y-%m-%d %H:%M:%S.%f")
        closings_date_logged = datetime.strptime(closings_date_logged, "%Y-%m-%d %H:%M:%S.%f")

        # if at least one of the data is recent, load the data
        if (datetime.today().now() - current_prices_date_logged > timedelta(seconds=30) and
                datetime.today().now() - closings_date_logged > timedelta(minutes=60)):
            return

        data = database.get_stock_data()
        # the keys are the tickers
        for ticker in data.keys():
            self.data.tickers.append(ticker)

            self.data.companies[ticker] = data[ticker]["company"]
            self.data.companies[data[ticker]["company"]] = ticker

            self.data.current_prices[ticker] = data[ticker]["current_price"]

            self.data.previous_closing[ticker] = data[ticker]["previous_closing_price"]

            self.data.closings[ticker] = []
            for date, price in data[ticker]["closings_prices"].items():
                self.data.closings[ticker].append([date, price])

            self.data.closings_date_logged = closings_date_logged
            self.data.current_prices_date_logged = current_prices_date_logged
