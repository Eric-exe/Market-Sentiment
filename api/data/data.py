"""
This class stores all the information for the companies and their stocks,
as well as the news data and their sentiments.
"""


class Data:
    """This class stores all the information for the companies and their stocks,
        as well as the news data and their sentiments."""

    def __init__(self):
        self.companies = {}  # dict {name : ticker} and {ticker : name}
        self.tickers = []  # list [ticker]

        self.previous_closings = {} # dict {ticker : [previous_closings]}, 14 days
        self.previous_closings_date_logged = None  # datetime, last logged

        self.current_prices = {}  # dict {ticker : current_price}
        self.current_prices_date_logged = None  # datetime, last logged

        self.news = {}  # dict {ticker : [news]}
        self.sentiment = {}  # dict {ticker : sentiment}
        self.news_count = {}  # dict {ticker : [news_count]}
        self.news_date_logged = {}  # dict {ticker : datetime}, last logged
