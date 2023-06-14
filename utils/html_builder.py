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
        change = (stock_data[ticker]["current_price"] - stock_data[ticker]["previous_closing_price"]) / stock_data[ticker]["previous_closing_price"] * 100
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
        temp_string = temp_string.replace("PRICE", format(previous_closings[date], ".2f"))
        # add the string to the result
        res += temp_string
    
    return res

def build_rec_charts_scripts(stock_data):
    """Builds the scripts for the rec charts"""

    res = ""

    values_string = """
    let yRecsTICKER = [STRONG_BUY, NORM_BUY, HOLD, NORM_SELL, STRONG_SELL];
    """

    html_string = """
    new Chart("chart-recs-TICKER", {
        type: "doughnut",
        data: {
            labels: ["Strong Buy", "Buy", "Hold", "Sell", "Strong Sell"],
            datasets: [
                {
                    label: [""],
                    data: yRecsTICKER,
                    backgroundColor: recColors
                }                                        
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            layout: {
                padding: 10
            }
        }
    });
    """

    for ticker in stock_data:
        # check if there's actually any recommendations
        if sum(stock_data[ticker]["analyst_recommendations"].values()) == 0:
            continue

        # values string
        temp_values_string = values_string
        temp_values_string = temp_values_string.replace("TICKER", ticker)
        temp_values_string = temp_values_string.replace("STRONG_BUY", str(stock_data[ticker]["analyst_recommendations"]["strongBuy"]))
        temp_values_string = temp_values_string.replace("NORM_BUY", str(stock_data[ticker]["analyst_recommendations"]["buy"]))
        temp_values_string = temp_values_string.replace("HOLD", str(stock_data[ticker]["analyst_recommendations"]["hold"]))
        temp_values_string = temp_values_string.replace("NORM_SELL", str(stock_data[ticker]["analyst_recommendations"]["sell"]))
        temp_values_string = temp_values_string.replace("STRONG_SELL", str(stock_data[ticker]["analyst_recommendations"]["strongSell"]))
        res += temp_values_string

        # html string
        temp_string = html_string
        temp_string = temp_string.replace("TICKER", ticker)
        res += temp_string

        # add a small version of the chart
        temp_string = temp_string.replace("chart-recs", "chart-recs-sm")
        res += temp_string


    return res

def build_sent_charts_scripts(news_data):
    """Builds the scripts for the sentiment charts"""

    res = ""

    values_string = """
    let ySentTICKER = [STRONG_POS, NORM_POS, WEAK_POS, WEAK_NEG, NORM_NEG, STRONG_NEG];
    """

    html_string = """
    new Chart("chart-sent-TICKER", {
        type: "doughnut",
        data: {
            labels: ["Strong Positive", "Positive", "Weak Positive", "Weak Negative", "Negative", "Strong Negative"],
            datasets: [
                {
                    label: [""],
                    data: ySentTICKER,
                    backgroundColor: sentColors
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            layout: {
                padding: 10
            }
        }
    });
    """

    for ticker in news_data:
        # check if there's actually any news
        if len(news_data[ticker]) == 0:
            continue

        # values string
        temp_values_string = values_string
        temp_values_string = temp_values_string.replace("TICKER", ticker)
        temp_values_string = temp_values_string.replace("STRONG_POS", str(news_data[ticker]["news_count"]["strong_positive"]))
        temp_values_string = temp_values_string.replace("NORM_POS", str(news_data[ticker]["news_count"]["moderate_positive"]))
        temp_values_string = temp_values_string.replace("WEAK_POS", str(news_data[ticker]["news_count"]["weak_positive"]))
        temp_values_string = temp_values_string.replace("WEAK_NEG", str(news_data[ticker]["news_count"]["weak_negative"]))
        temp_values_string = temp_values_string.replace("NORM_NEG", str(news_data[ticker]["news_count"]["moderate_negative"]))
        temp_values_string = temp_values_string.replace("STRONG_NEG", str(news_data[ticker]["news_count"]["strong_negative"]))
        res += temp_values_string

        # html string
        temp_string = html_string
        temp_string = temp_string.replace("TICKER", ticker)
        res += temp_string

        # add a small version of the chart
        temp_string = temp_string.replace("chart-sent", "chart-sent-sm")
        res += temp_string

    return res

def build_panes(stock_data, news_data):
    """Builds the panes for the web app"""

    res = ""

    html_string = """
    <div class="tab-pane fade text-light p-2 mb-3" id="pane-TICKER" role="tabpanel" aria-labelledby="tab-TICKER">
        <h5>COMPANY (TICKER)</h5>
        <div class="container p-0">
            <div class="row">

                <!-- Medium and Large -->
                <div class="col-5 d-none d-md-block">
                    <b>Regular Market Price:</b> CURR_PRICE 
                    <div class="text-danger d-inline small"> DIFF </div><br>
                    <b>Previous Close:</b> PREV_CLOSE <br>
                    <div class="center-div">
                        <b>Last 14 Previous Closings: </b>
                        <!-- Modal button -->
                        <button type="button" class="btn btn-outline-primary py-0 px-3 mx-2" data-bs-toggle="modal" data-bs-target="#modal-TICKER">Show</button>
                    </div>
                </div>

                <!-- Small -->
                <div class="col-12 d-md-none">
                    <b>Regular Market Price:</b><br> CURR_PRICE
                    <div class="text-danger d-inline small"> DIFF </div><br>
                    <b>Previous Close:</b><br> PREV_CLOSE <br>
                    <b>Last 14 Previous Closings: </b>
                    <div class="center-div">
                        <!-- Modal button -->
                        <button type="button" class="btn btn-outline-primary py-0 px-3 mx-0 mb-1" data-bs-toggle="modal" data-bs-target="#modal-TICKER">Show</button>
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

                <!-- Charts -->
                <!-- Medium and large -->
                <div class="col-7 d-none d-md-block">
                    <div class="container">
                        <div class="row">

                            <div class="col-6">
                                <b>Analyst Recommendations</b>
                                <div style="max-height: 150px;">
                                    <canvas id="chart-recs-TICKER"></canvas>
                                </div>
                                <b>Total recommendations:</b> TOTAL_RECS
                            </div>

                            <div class="col-6">
                                <b>Market Sentiment</b>
                                <div class="max-height: 150px;">
                                    <canvas id="chart-sent-TICKER"></canvas>
                                </div>
                                <b>Total news:</b> TOTAL_NEWS<br>
                                <b>Sentiment:</b> 
                                <div class="sentiment-text">SENTIMENT_VAL</div>
                            </div>

                        </div>
                    </div>
                </div>

                <!-- Small -->
                <div class="col-12 d-md-none">
                    <div class="container px-0 pb-3">
                        <div class="row">
                            <hr>
                            <div class="col-12">
                                <b>Analyst Recommendations</b>
                                <div style="max-height: 175px;">
                                    <canvas id="chart-recs-sm-TICKER"></canvas>
                                </div>
                                <b>Total recommendations:</b> TOTAL_RECS
                            </div>
                        </div>
                        <div class="row">
                            <hr>
                            <div class="col-12">
                                <b>Market Sentiment</b>
                                <div style="max-height: 175px;">
                                    <canvas id="chart-sent-sm-TICKER"></canvas>
                                </div>
                                <b>Total news:</b> TOTAL_NEWS<br>
                                <b>Sentiment:</b>
                                <div class="sentiment-text">SENTIMENT_VAL</div>
                            </div>
                        </div>
                    </div>
                </div>

                <hr>

                <!-- News -->
                <!-- Medium and large -->
                <div class="col-12 d-none d-md-block">
                    <b>COMPANY in the News</b>
                </div>

                <!-- Small -->
                <div class="col-12 d-md-none">
                    <b>COMPANY in the News</b>
                </div>
            </div>
        </div>
    </div>
    """

    tickers = list(stock_data.keys())

    for ticker in tickers:
        # create a copy of the html string
        temp_string = html_string
        # replace the data
        temp_string = temp_string.replace("TICKER", ticker) # should take care of most of the replacements
        temp_string = temp_string.replace("COMPANY", stock_data[ticker]["company"])
        temp_string = temp_string.replace("CURR_PRICE", format(stock_data[ticker]["current_price"], ".2f"))

        # if the change is positive, add a plus sign and add a green color
        change = (stock_data[ticker]["current_price"] - stock_data[ticker]["previous_closing_price"]) / stock_data[ticker]["previous_closing_price"] * 100

        # also calculate the difference between the current price and the previous close
        difference = format(stock_data[ticker]["current_price"] - stock_data[ticker]["previous_closing_price"], ".2f")
        if change > 0:
            temp_string = temp_string.replace("DIFF", "+" + difference + "&nbsp;(+" + format(change, ".2f") + "%)")
            temp_string = temp_string.replace("text-danger", "text-success")
        else:
            temp_string = temp_string.replace("DIFF", difference + "&nbsp;(" + format(change, ".2f") + "%)")

        temp_string = temp_string.replace("PREV_CLOSE", format(stock_data[ticker]["previous_closing_price"], ".2f"))

        # build the table
        temp_string = temp_string.replace("TABLE", build_table(stock_data[ticker]["closings_prices"]))

        # remove the recommendations chart if there are no recommendations
        if sum(stock_data[ticker]["analyst_recommendations"].values()) == 0:
            temp_string = temp_string.replace("<canvas id=\"chart-recs-" + ticker + "\"></canvas>", "")
            temp_string = temp_string.replace("<b>Total recommendations:</b> TOTAL_RECS", "No data from Yahoo Finance available for this month :(")

            # small chart
            temp_string = temp_string.replace("<canvas id=\"chart-recs-sm-" + ticker + "\"></canvas>", "")
        else:
            temp_string = temp_string.replace("TOTAL_RECS", str(sum(stock_data[ticker]["analyst_recommendations"].values())))

        # sentiment chart
        if sum(news_data[ticker]["news_count"].values()) == 0:
            temp_string = temp_string.replace("<canvas id=\"chart-sent-" + ticker + "\"></canvas>", "")
            temp_string = temp_string.replace("<b>Total news:</b> TOTAL_NEWS<br>", "No data from Marketaux API :(")
            temp_string = temp_string.replace("<b>Sentiment:</b> <div class=\"sentiment-text\">SENTIMENT_VAL</div>", "")
        else:
            temp_string = temp_string.replace("TOTAL_NEWS", str(sum(news_data[ticker]["news_count"].values())))
            temp_string = temp_string.replace("SENTIMENT_VAL", format(news_data[ticker]["sentiment"], ".5f"))

        res += temp_string

    return res
