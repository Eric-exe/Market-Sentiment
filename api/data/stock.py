"""This file gets the stock information from the API yfinance and saves it to a CSV file."""

from datetime import datetime, timedelta
import yfinance as yf

# ==================================================================================================
# yfinance API


def get_stock_info(ticker):
    """Return the stock information from the API."""
    return yf.Ticker(ticker).info


def get_stock_price(info):
    """Return the stock price from the API."""
    return info["currentPrice"]


def get_stock_previous_close(info):
    """Return the stock previous close from the API."""
    return info["previousClose"]


def get_stock_change(info):
    """Return the stock change percentage from the API."""
    return round(
        (get_stock_price(info) - get_stock_previous_close(info)) /
        get_stock_previous_close(info) * 100,
        2)


def get_five_day_stock_change(info, previous_closings):
    """Return the stock change percentage from the COMPANY_STATS if applicable. Else, return -1."""
    current_price = get_stock_price(info)
    previous_closings = previous_closings[info["symbol"]]
    if len(previous_closings) == 14:
        previous_closing = previous_closings[0]
        return round((current_price - previous_closing) / previous_closing * 100, 2)
    return -1

# ==================================================================================================


class Stock:
    """The class for getting the stock information."""

    def __init__(self, data):
        """Initialize the Stock class."""
        self.data = data
        data.companies = None  # {name : ticker}
        data.tickers = None  # [ticker]
        data.previous_closings = None
        data.current_prices = None
        data.previous_closings_date_logged = None
        data.current_prices_date_logged = None

        self.get_companies()

    def get_companies(self):
        """Update the company data."""
        self.data.companies = {}
        self.data.tickers = []
        # read the company data from the CSV file
        with open('api/data/companies.csv', 'r', encoding="utf-8") as file:
            data = file.read().split("\n")
            data.pop(0)  # remove header
            for company in data:
                company_info = company.split(",")
                name = company_info[0]
                ticker = company_info[1]
                self.data.companies[name] = ticker
                self.data.tickers.append(ticker)

        self.data.previous_closings = {}
        self.data.current_prices = {}

    def save_previous_closings(self):
        """Save the previous closing prices of the companies."""

        # check if we already have logged the previous closing prices
        if (self.data.previous_closings_date_logged is None or
                self.data.previous_closings_date_logged != datetime.today().date()):

            self.data.previous_closings_date_logged = datetime.today().date()
            # process the previous closing prices
            for ticker in self.data.tickers:
                # get the previous closing price
                info = get_stock_info(ticker)
                previous_close = get_stock_previous_close(info)
                # save the previous closing price
                if ticker not in self.data.previous_closings:
                    self.data.previous_closings[ticker] = []
                self.data.previous_closings[ticker].insert(0, previous_close)

                # we only want to save the previous closing prices for the past 14 days
                if len(self.data.previous_closings[ticker]) > 14:
                    self.data.previous_closings[ticker].pop()

    def save_current_prices(self):
        """Save the current prices of the companies. Should update every 10 minutes."""
        if (self.data.current_prices_date_logged is None or
                datetime.today().now() - self.data.current_prices_date_logged >=
                timedelta(minutes=10)):

            self.data.current_prices_date_logged = datetime.today().now()
            for ticker in self.data.tickers:
                info = get_stock_info(ticker)
                current_price = get_stock_price(info)
                self.data.current_prices[ticker] = current_price
