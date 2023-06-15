"""This file gets the stock information from the API yfinance and saves it to a CSV file."""

from datetime import datetime, timedelta
from yahooquery import Ticker

# TODO: Add recommendation trend to the stock data

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
        self.data.tickers_info = Ticker(self.data.tickers)

    def save_closings_prices(self):
        """Save the previous closing prices of the companies."""

        # check if we already have logged the previous closing prices
        # update every 60 minutes
        if (self.data.closings_date_logged is None or
                datetime.now() - self.data.closings_date_logged >=
                timedelta(minutes=60)):

            # process the closing prices
            ticker_prices = self.data.tickers_info.price
            ticker_history = self.data.tickers_info.history(period="15d")
            self.data.closings_date_logged = datetime.now()

            for ticker in self.data.tickers:
                self.data.closings[ticker] = []
                # get the closing prices for the last 14 days
                history = ticker_history.loc[ticker]
                closing_prices = history.reset_index(
                )[["date", "close"]].values.tolist()
                # convert the date to string
                closing_prices = [[str(date), price]
                                  for date, price in closing_prices]
                # pop the last closing price, which is today's closing price
                closing_prices.pop()

                self.data.closings[ticker] = closing_prices

                self.data.previous_closing[ticker] = ticker_prices[ticker]["regularMarketPreviousClose"]

                # save the analyst recommendations
                # Because the recommendations are not updated as frequently, we
                # only update it every 60 minutes. Even then, it is overkill.
                self.save_analyst_recommendations(ticker)

    def save_analyst_recommendations(self, ticker):
        """Gets the analyst recommmendations from the API and saves it to the data."""
            
        recommendations = Ticker(ticker).recommendation_trend
        recommendations = recommendations.iloc[0][["strongBuy", "buy", "hold", "sell", "strongSell"]].to_dict()
        self.data.analyst_recommendations[ticker] = recommendations

    def save_current_prices(self):
        """Save the current prices of the companies. Should update every 15 seconds."""

        if (self.data.current_prices_date_logged is None or
                datetime.now() - self.data.current_prices_date_logged >=
                timedelta(seconds=15)):
            
            ticker_prices = self.data.tickers_info.price
            self.data.current_prices_date_logged = datetime.now()
            for ticker in self.data.tickers:
                self.data.current_prices[ticker] = ticker_prices[ticker]["regularMarketPrice"]

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
                "closings_prices": {},
                "analyst_recommendations": self.data.analyst_recommendations[ticker]
            }

            for closing in self.data.closings[ticker]:
                response["data"][ticker]["closings_prices"][closing[0]] = closing[1]

        return response

    def load_stock_data(self, database):
        """Loads the stock data from firebase"""
        # first, check if our data is recent
        if (self.data.current_prices_date_logged is not None and
                self.data.closings_date_logged is not None and
                datetime.now() - self.data.current_prices_date_logged <=
                timedelta(seconds=15) and
                datetime.now() - self.data.closings_date_logged <=
                timedelta(minutes=60)):
            print("Using cached stock data", flush=True)
            return True
        
        # check if the stock data in firebase is recent
        meta = database.get_stock_meta()
        if meta is None:
            return False

        current_prices_date_logged = meta.get("current_prices_date_logged")
        closings_date_logged = meta.get("closings_date_logged")

        if current_prices_date_logged is None or closings_date_logged is None:
            return False

        current_prices_date_logged = datetime.strptime(current_prices_date_logged, "%Y-%m-%d %H:%M:%S.%f")
        closings_date_logged = datetime.strptime(closings_date_logged, "%Y-%m-%d %H:%M:%S.%f")

        # if at least one of the data is recent, load the data
        if (datetime.now() - current_prices_date_logged > timedelta(seconds=15) and
                datetime.now() - closings_date_logged > timedelta(minutes=60)):
            return False

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

            self.data.analyst_recommendations[ticker] = data[ticker]["analyst_recommendations"]

        self.data.closings_date_logged = closings_date_logged
        self.data.current_prices_date_logged = current_prices_date_logged

        # if both data are recent, we don't need to update the data
        if (datetime.now() - self.data.current_prices_date_logged <= timedelta(seconds=15) and
                datetime.now() - self.data.closings_date_logged <= timedelta(minutes=60)):
            return True
        return False # we need to update the data