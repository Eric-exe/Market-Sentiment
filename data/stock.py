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
        with open('data/companies.csv', 'r', encoding="utf-8") as file:
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

        self.data.ticker_data = Ticker(self.data.tickers)

    def save_closings_prices(self):
        """Save the previous closing prices of the companies."""

        # check if we already have logged the previous closing prices
        # update every 60 minutes
        if (self.data.closings_date_logged is None or
                datetime.today().now() - self.data.closings_date_logged >=
                timedelta(minutes=60)):

            # update the time we logged the previous closing prices
            self.data.closings_date_logged = datetime.today().now()

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
                self.data.previous_closing[ticker] = self.data.ticker_data.price[ticker]["regularMarketPreviousClose"]

    def save_current_prices(self):
        """Save the current prices of the companies. Should update every minute."""
        if (self.data.current_prices_date_logged is None or
                datetime.today().now() - self.data.current_prices_date_logged >=
                timedelta(minutes=1)):

            self.data.current_prices_date_logged = datetime.today().now()
            for ticker in self.data.tickers:
                self.data.current_prices[ticker] = self.data.ticker_data.price[ticker]["regularMarketPrice"]

    def get_stock_change(self, ticker):
        """Return the stock change percentage."""
        current_price = self.data.current_prices[ticker]
        previous_closing = self.data.previous_closing[ticker]
        return (current_price - previous_closing) / previous_closing * 100
