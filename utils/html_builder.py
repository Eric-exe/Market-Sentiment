"""This file handles alll the HTML string building for the web app"""


def build_buttons(stock_data):
    """Builds the buttons for the web app"""

    res = ""

    html_string = """
    <button class="nav-link mb-1" id="tab-TICKER" data-bs-toggle="pill" data-bs-target="#pane-TICKER" type="button" role="tab" aria-controls="pane-TICKER" aria-selected="false">
        <div class="row text-left">
            <div class="col-4 d-none d-md-block"><b>TICKER</b></div>
            <div class="col-4 d-none d-md-block"><b>PRICE</b></div>
            <div class="col-4 d-none d-md-block text-danger"><b>CHANGE</b></div>
            <div class="col-12 d-md-none"><b>TICKER</b></div>
        </div>
    </button>
    """

    for ticker in stock_data:
        # create a copy of the html string
        temp_string = html_string
        # replace the data
        temp_string = temp_string.replace("TICKER", ticker)
        temp_string = temp_string.replace(
            "PRICE", format(stock_data[ticker]["current_price"], ".2f"))

        # if the change is positive, add a plus sign and add a green color
        change = float(stock_data[ticker]["change"])
        if change > 0:
            temp_string = temp_string.replace(
                "CHANGE", "+" + format(change, ".2f") + "%")
            temp_string = temp_string.replace("text-danger", "text-success")
        else:
            temp_string = temp_string.replace("CHANGE", format(change, ".2f") + "%")

        # add the string to the result
        res += temp_string

    return res

def build_table(previous_closings):
    """Builds the table for panes modal"""

    html_string = """
    <tr>
        <td>DATE</td>
        <td>PRICE</td>
    </tr>
    """

    res = ""

    for date in previous_closings:
        # create a copy of the html string
        temp_string = html_string
        # replace the data
        temp_string = temp_string.replace("DATE", date)
        temp_string = temp_string.replace("PRICE", str(format(float(previous_closings[date]), ".2f")))
        # add the string to the result
        res += temp_string
    
    return res

def build_panes(stock_data):
    """Builds the panes for the web app"""

    res = ""

    html_string = """
    <div class="tab-pane fade text-light p-2" id="pane-TICKER" role="tabpanel" aria-labelledby="tab-TICKER">
        <h5>COMPANY (TICKER)</h5>
        <div class="container p-0">
            <div class="row">
                <div class="col-6">
                    <b>Regular Market Price:</b> CURR_PRICE 
                    <div class="col-4 text-danger d-inline small"> DIFF </div><br>
                    <b>Previous Close:</b> PREV_CLOSE <br>
                    <div class="center-div">
                        <b>Last 14 Previous Closings: </b>
                        <!-- Modal button -->
                        <button type="button" class="btn btn-outline-primary py-0 px-2 mx-2" data-bs-toggle="modal" data-bs-target="#modal-TICKER">Show</button>
                    </div>
                </div>
                <!-- Modal content -->
                <div class="modal fade" id="modal-TICKER" tabindex="-1" aria-labelledby="modal-label-TICKER" aria-hidden="true">
                    <div class="modal-dialog modal-dialog-scrollable">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title text-dark" id="modal-label-TICKER">Last 14 Closings Prices</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body text-dark">
                                <table class="table table-hover table-sm">
                                    <thead>
                                        <tr>
                                            <th scope="col">Date</th>
                                            <th scope="col">Price</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        TABLE
                                    </table>
                                </div>
                                <div class="modal-footer">
                                    <div class="button btn btn-secondary" data-bs-dismiss="modal">Close</div>
                                </div>
                            </div>
                        </div>
                    </div>
                <div class="col-6">CONTENT2</div>
            </div>
        </div>
    </div>
    """

    tickers = list(stock_data.keys())

    for ticker in tickers:
        # create a copy of the html string
        temp_string = html_string
        # replace the data
        temp_string = temp_string.replace("TICKER", ticker)
        temp_string = temp_string.replace("COMPANY", stock_data[ticker]["company"])
        temp_string = temp_string.replace("CURR_PRICE", format(stock_data[ticker]["current_price"], ".2f"))

        # if the change is positive, add a plus sign and add a green color
        change = float(stock_data[ticker]["change"])

        # also calculate the difference between the current price and the previous close
        difference = format(stock_data[ticker]["current_price"] - stock_data[ticker]["previous_closing_price"], ".2f")
        if change > 0:
            temp_string = temp_string.replace("DIFF", "+" + difference + "&nbsp;(+" + format(change, ".2f") + "%)")
            temp_string = temp_string.replace("text-danger", "text-success")
        else:
            temp_string = temp_string.replace("DIFF", difference + "&nbsp;(" + format(change, ".2f") + "%)")

        temp_string = temp_string.replace("PREV_CLOSE", str(stock_data[ticker]["previous_closing_price"]))

        # build the table
        temp_string = temp_string.replace("TABLE", build_table(stock_data[ticker]["closings_prices"]))

        res += temp_string

    return res
