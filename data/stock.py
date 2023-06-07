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

def get_stock_close_date(ticker):
    """Return the stock previous close date from the API."""
    ticker_info = yf.Ticker(ticker)
    history = ticker_info.history(period="1d")
    return history.index[-1].strftime("%Y-%m-%d")

# ==================================================================================================


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
                # compare the closing date with the current date
                close_date = self.data.closings_company_date_logged.get(ticker)
                current_close_date = get_stock_close_date(ticker)

                if (close_date is None
                    or close_date != current_close_date):
                    # get the closing prices for the last 14 trading days
                    stock = yf.Ticker(ticker)
                    closings_data = stock.history(period="14d")['Close']
                    closings_list = [
                        [str(date.date()), price] for date, price in closings_data.items()
                    ]

                    # reverse the list so that the most recent date is first
                    closings_list.reverse()

                    # update the closing prices
                    self.data.closings[ticker] = closings_list

                    # upadte the previous closing price
                    self.data.previous_closing[ticker] = get_stock_previous_close(stock.info)

                    # update the closing date logged
                    self.data.closings_company_date_logged[ticker] = current_close_date


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

    def get_stock_change(self, ticker):
        """Return the stock change percentage."""
        current_price = self.data.current_prices[ticker]
        previous_closing = self.data.previous_closing[ticker]
        return (current_price - previous_closing) / previous_closing * 100
        