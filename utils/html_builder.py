"""This file handles alll the HTML string building for the web app"""


def build_buttons(stock_data):
    """Builds the buttons for the web app"""

    res = ""

    html_string = """
    <button class="nav-link mb-1" id="tab-TICKER" data-bs-toggle="pill" data-bs-target="#pane-TICKER" type="button" role="tab" aria-controls="pane-TICKER" aria-selected="false">
        <div class="container">
            <div class="row text-left">
                <div class="col-4"><b>TICKER</b></div>
                <div class="col-4"><b>PRICE</b></div>
                <div class="col-4 text-danger"><b>CHANGE</b></div>
            </div>
        </div>
    </button>
    """

    for ticker in stock_data:
        # create a copy of the html string
        temp_string = html_string
        # replace the data
        temp_string = temp_string.replace("TICKER", ticker)
        temp_string = temp_string.replace("PRICE", str(stock_data[ticker]["current_price"]))

        # if the change is positive, add a plus sign and add a green color
        change = round(stock_data[ticker]["change"], 5)
        if change > 0:
            temp_string = temp_string.replace("CHANGE", "+" + str(change) + "%")
            temp_string = temp_string.replace("text-danger", "text-success")
        else:
            temp_string = temp_string.replace("CHANGE", str(change) + "%")

        # add the string to the result
        res += temp_string

    return res

def build_panes(stock_data, news_data):
    """Builds the panes for the web app"""

    res = ""

    html_string = """
    <div class="tab-pane fade text-light px-2" id="pane-TICKER" role="tabpanel" aria-labelledby="tab-TICKER">Content</div>
    """

    tickers = list(stock_data.keys())

    for ticker in tickers:
        # create a copy of the html string
        temp_string = html_string
        # replace the data
        temp_string = temp_string.replace("TICKER", ticker)
    
        res += temp_string
    
    return res