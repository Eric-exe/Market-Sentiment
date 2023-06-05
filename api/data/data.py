"""
This class stores all the information for the companies and their stocks,
as well as the news data and their sentiments.
"""


class Data:
    """This class stores all the information for the companies and their stocks,
        as well as the news data and their sentiments."""

    def __init__(self):
        self.companies = None  # dict {name : ticker}
        self.tickers = None  # list [ticker]

        # dict {ticker : [previous_closings]}, 14 days
        self.previous_closings = None
        self.previous_closings_date_logged = None  # datetime, last logged

        self.current_prices = None  # dict {ticker : current_price}
        self.current_prices_date_logged = None  # datetime, last logged

        self.news = None  # dict {ticker : [news]}
        self.sentiment = None  # dict {ticker : sentiment}
        self.news_count = None  # dict {ticker : [news_count]}
        self.news_date_logged = None  # dict {ticker : datetime}, last logged
