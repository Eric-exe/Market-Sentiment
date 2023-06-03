"""This file gets the stock information from the API yfinance and saves it to a CSV file."""

import os
from datetime import datetime, timedelta
import yfinance as yf
import data

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

    def __init__(self):
        """Initialize the Stock class."""
        self.companies = None
        self.previous_closings = None
        self.current_prices = None
        self.previous_closing_date = None
        self.current_prices_date = None

        self.get_companies()
        self.save_previous_closings()
        self.save_current_prices()

    def get_companies(self):
        """Return the company data."""
        self.companies = data.load_companies()
        self.previous_closings = {}
        self.current_prices = {}

    def save_previous_closings(self):
        """Save the previous closing prices of the companies."""

        # check if we already have logged the previous closing prices
        # if file does not exist, create it and write today's date
        self.previous_closing_date = str(datetime.today().date())

        # check if stock directory exists
        if not os.path.isdir("data/stock"):
            os.mkdir("data/stock")

        if not os.path.isfile("data/stock/stats"):
            with open("data/stock/stats", "w", encoding="utf-8") as file:
                file.write("Last previous closings logged: " + self.previous_closing_date + "\n" +
                           "Last current prices logged: ")

        # if file exists, read the date and compare to today's date
        else:
            with open("data/stock/stats", "r", encoding="utf-8") as file:
                date_previous = file.readline().split(
                    "\n")[0].split(": ")[1].strip()
                date_current = file.readline().split(
                    "\n")[0].split(": ")[1].strip()

                if date_previous == self.previous_closing_date:
                    # save stats to COMPANY_PREVIOUS_CLOSINGS
                    with open("data/stock/previous_closings.csv", "r", encoding="utf-8") as file:
                        previous_closing_data = data.read_csv(
                            "data/stock/previous_closings.csv")
                        previous_closing_data.pop(0)
                        for company in previous_closing_data:
                            ticker = company[1]
                            self.previous_closings[ticker] = company[2:]
                    return

                else:
                    # update the date
                    with open("data/stock/stats", "w", encoding="utf-8") as file:
                        file.write("Last previous closings logged: " +
                                   self.previous_closing_date +
                                   "\n" +
                                   "Last current prices logged: " +
                                   date_current)

        # read the previous closing prices from the CSV file
        previous_closing_prices = data.load_previous_closings()

        for company in self.companies:
            ticker = self.companies[company]
            info = get_stock_info(ticker)
            # if the company is not in the dictionary, add it
            if company not in previous_closing_prices:
                previous_closing_prices[company] = []
                previous_closing_prices[company].insert(
                    0, get_stock_previous_close(info))
            # if the list has more than 14 elements, remove the last element
            if len(previous_closing_prices[company]) > 14:
                previous_closing_prices[company].pop()

        # save the previous closing prices to the CSV file
        header = ["Company",
                  "Ticker",
                  "Previous Close 1",
                  "Previous Close 2",
                  "Previous Close 3",
                  "Previous Close 4",
                  "Previous Close 5",
                  "Previous Close 6",
                  "Previous Close 7",
                  "Previous Close 8",
                  "Previous Close 9",
                  "Previous Close 10",
                  "Previous Close 11",
                  "Previous Close 12",
                  "Previous Close 13",
                  "Previous Close 14"]

        # turn the dictionary into a list
        previous_closing_prices_list = []
        for company in previous_closing_prices:
            ticker = self.companies[company]
            previous_closing_prices_list.append(
                [company, ticker] + previous_closing_prices[company])
            # save to COMPANY_PREVIOUS_CLOSINGS
            self.previous_closings[ticker] = previous_closing_prices[company]

        data.save_data("data/stock/previous_closings.csv",
                       header, previous_closing_prices_list)

    def save_current_prices(self):
        """Save the current prices of the companies. Should update every 10 minutes."""

        # read the last time the current prices were logged
        with open("data/stock/stats", "r", encoding="utf-8") as file:
            date_previous = file.readline().split(
                "\n")[0].split(": ")[1].strip()
            date_current = file.readline().split(
                "\n")[0].split(": ")[1].strip()

            if date_current == "":
                date_current = "1970-01-01 00:00:00.000000"
                date_current = datetime.strptime(
                    date_current, "%Y-%m-%d %H:%M:%S.%f")
            else:
                date_current = datetime.strptime(
                    date_current, "%Y-%m-%d %H:%M:%S.%f")

            # calculate the difference between the current time and
            # the last time the current prices were logged
            difference = datetime.today().now() - date_current
            if difference < timedelta(minutes=10):
                # current prices last logged less than 10 minutes ago, we don't need to update
                # save stats into COMPANY_CURRENT_PRICES
                with open("data/stock/current_prices.csv", "r", encoding="utf-8") as file:
                    current_price_data = data.read_csv(
                        "data/stock/current_prices.csv")
                    current_price_data.pop(0)
                    for company in current_price_data:
                        ticker = company[1]
                        self.current_prices[ticker] = company[2]
                    return

            # update the time
            with open("data/stock/stats", "w", encoding="utf-8") as file:
                self.current_prices_date = str(datetime.today().now())
                file.write("Last previous closings logged: " + date_previous + "\n" +
                           "Last current prices logged: " + self.current_prices_date)

        current_prices = {}

        for company in self.companies:
            ticker = self.companies[company]
            info = get_stock_info(ticker)
            current_prices[company] = get_stock_price(info)

        # save the current prices to the CSV file
        header = ["Company",
                  "Ticker",
                  "Current Price"]
        # turn the dictionary into a list
        current_prices_list = []
        for company in current_prices.items():
            current_prices_list.append(
                [company[0], self.companies[company[0]], company[1]])

        data.save_data("data/stock/current_prices.csv",
                       header, current_prices_list)


stock = Stock()
