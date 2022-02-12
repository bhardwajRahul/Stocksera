from helpers import *
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer

conn = sqlite3.connect(r"database/database.db", check_same_thread=False)
db = conn.cursor()


def default_ticker(ticker):
    if not ticker:
        return "AAPL"
    return ticker.upper()


def get_days_params(request, default_days, max_days):
    try:
        num_days = int(request.GET.get("days", default_days))
        if num_days > max_days:
            num_days = max_days
    except ValueError:
        num_days = default_days

    date_threshold = str(datetime.utcnow() - timedelta(hours=24 * num_days))

    return date_threshold


def get_date(df, date_to, date_from, col_name="Date"):
    df[col_name] = df[col_name].astype(str)
    if date_to:
        df = df[df[col_name] <= date_to]
    if date_from:
        df = df[df[col_name] >= date_from]
    return df


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def stocksera_trending(request):
    df = pd.read_sql_query("SELECT * FROM stocksera_trending ORDER BY count DESC LIMIT 10", conn)
    df = df.to_dict(orient="records")
    return JSONResponse(df)


def historical_data(request, ticker_selected="AAPL"):
    """
    Allow users to filter/sort historical data of ticker
    """
    pd.options.display.float_format = '{:.2f}'.format
    ticker_selected = default_ticker(ticker_selected)

    if request.GET.get("sort"):
        sort_by = request.GET['sort'].replace("Sort By: ", "").title()
    else:
        sort_by = "Date"

    if request.GET.get("timeframe"):
        timeframe = request.GET['timeframe'].replace("Timeframe: ", "")
    else:
        timeframe = "1Y"

    ticker = yf.Ticker(ticker_selected)
    price_df = ticker.history(period=timeframe.lower(), interval="1d").reset_index().iloc[::-1]

    # del price_df["Dividends"]
    # del price_df["Stock Splits"]

    # Add % Price Change, Amplitude, % Vol Change columns
    price_df["% Price Change"] = price_df["Close"].shift(-1)
    price_df["% Price Change"] = 100 * (price_df["Close"] - price_df["% Price Change"]) / price_df["% Price Change"]

    price_df["Amplitude"] = 100 * (price_df["High"] - price_df["Low"]) / price_df["Open"]

    price_df["% Vol Change"] = price_df["Volume"].shift(-1)
    price_df["% Vol Change"] = 100 * (price_df["Volume"] - price_df["% Vol Change"]) / price_df["% Vol Change"]

    price_df["Volume / % Price Ratio"] = round(price_df["Volume"] / price_df["% Price Change"].abs())
    price_df.insert(0, 'Day', price_df["Date"].dt.day_name())

    if request.GET.get("order"):
        order = request.GET['order'].replace("Order: ", "")
    else:
        order = "Descending"

    price_df = price_df.round(2)
    price_df = price_df.replace([np.inf, -np.inf], np.nan)
    price_df = price_df.fillna(0)

    # summary_df = price_df.head(50).groupby(["Day"]).mean()
    # summary_df.reset_index(inplace=True)
    # summary_df = summary_df.groupby(['Day']).sum().reindex(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])
    # summary_df.reset_index(inplace=True)
    # summary_df = pd.DataFrame(summary_df[["Day", "% Price Change"]]).to_html(index=False)

    if order == "Descending":
        price_df.sort_values(by=[sort_by], inplace=True, ascending=False)
    else:
        price_df.sort_values(by=[sort_by], inplace=True)

    # price_df.reset_index(inplace=True, drop=True)
    # price_df.index = np.arange(1, len(price_df) + 1)
    # price_df.reset_index(inplace=True)
    # price_df.rename(columns={"index": "Rank"}, inplace=True)
    df = price_df.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def sec_fillings(request, ticker_selected="AAPL"):
    ticker_selected = default_ticker(ticker_selected)
    df = pd.read_sql_query("SELECT * FROM sec_fillings WHERE ticker='{}' ".format(ticker_selected), conn)
    if df.empty:
        df = get_sec_fillings(ticker_selected)
    else:
        del df["ticker"]
        df.rename(columns={"filling": "Filling", "description": "Description", "filling_date": "Filling Date"},
                  inplace=True)
    df = get_date(df, request.GET.get("date_to"), request.GET.get("date_from"), "Filling Date")
    df = df.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def news_sentiment(request, ticker_selected="AAPL"):
    """
    Show news and sentiment of ticker in /ticker?quote={TICKER}. Data from Finviz
    Note: News are only available if hosted locally. Read README.md for more details
    """
    ticker_selected = default_ticker(ticker_selected)
    df = pd.read_sql_query("SELECT * FROM daily_ticker_news WHERE ticker='{}' ".format(ticker_selected), conn)
    if df.empty:
        df = get_ticker_news(ticker_selected)
    else:
        del df["Ticker"]
    df = df.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def insider_trading(request, ticker_selected="AAPL"):
    """
    Get a specific ticker's insider trading data from Finviz
    """
    pd.options.display.float_format = '{:.2f}'.format
    ticker_selected = default_ticker(ticker_selected)
    df = pd.read_sql_query("SELECT * FROM insider_trading WHERE Ticker='{}' ".format(ticker_selected), conn)
    if df.empty:
        get_insider_trading(ticker_selected)
        df = pd.read_sql_query("SELECT * FROM insider_trading WHERE Ticker='{}' ".format(ticker_selected), conn)
    else:
        df.rename(columns={"TransactionDate": "Date",
                           "TransactionType": "Transaction",
                           "Value": "Value ($)",
                           "SharesLeft": "#Shares Total",
                           "URL": ""}, inplace=True)
    del df["Ticker"]
    df = get_date(df, request.GET.get("date_to"), request.GET.get("date_from"))
    df = df.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def latest_insider_summary(request):
    """
    Get latest insider trading data from Finviz and perform analysis
    """
    pd.options.display.float_format = '{:.2f}'.format

    df = pd.read_sql_query("SELECT * FROM latest_insider_trading_analysis", conn)
    df.rename(columns={"MktCap": "Market Cap", "Proportion": "% of Mkt Cap"}, inplace=True)
    df = df.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def latest_insider(request):
    """
    Get latest insider trading data from Finviz and perform analysis
    """
    pd.options.display.float_format = '{:.2f}'.format
    try:
        n_rows = int(request.GET.get("limit", 500))
        if n_rows <= 0 or n_rows > 5000:
            n_rows = 500
    except ValueError:
        n_rows = 500

    df = pd.read_sql_query("SELECT * FROM latest_insider_trading ORDER BY DateFilled DESC LIMIT {}".format(n_rows),
                           conn)

    df.rename(columns={"TransactionDate": "Date",
                       "TransactionType": "Transaction",
                       "Value": "Value ($)",
                       "SharesLeft": "#Shares Total",
                       "URL": ""}, inplace=True)

    df = df.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def top_short_volume(request):
    pd.options.display.float_format = '{:.2f}'.format
    df = pd.read_csv(r"database/highest_short_volume.csv")
    df.fillna('', inplace=True)
    df = df.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def short_volume(request, ticker_selected="AAPL"):
    """
    Get short volume of tickers (only popular ones). Data from Finra
    """
    pd.options.display.float_format = '{:.2f}'.format

    ticker_selected = default_ticker(ticker_selected)

    df = pd.read_csv("database/short_volume.csv")
    df = df[df["ticker"] == ticker_selected][::-1]
    history = pd.DataFrame(yf.Ticker(ticker_selected).history(interval="1d", period="1y")["Close"])
    history.reset_index(inplace=True)
    history["Date"] = history["Date"].astype(str)
    df = pd.merge(df, history, on=["Date"], how="left")
    df.rename(columns={"reported_date": "Date", "short_vol": "Short Volume",
                       "short_exempt_vol": "Short Exempt Vol", "total_vol": "Total Volume",
                       "percent": "% Shorted", "close_price": "Close Price"}, inplace=True)
    df = get_date(df, request.GET.get("date_to"), request.GET.get("date_from"))
    df = df.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def top_failure_to_deliver(request):
    top_ftd = pd.read_csv(r"database/failure_to_deliver/top_ftd.csv")
    top_ftd = top_ftd.replace(np.nan, "")
    df = top_ftd.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def failure_to_deliver(request, ticker_selected="AAPL"):
    """
    Get FTD of tickers. Data from SEC
    """
    ticker_selected = default_ticker(ticker_selected)

    ftd = pd.read_csv(r"database/failure_to_deliver/ftd.csv")
    ftd = ftd[ftd["Symbol"] == ticker_selected]
    ftd = ftd[::-1]
    ftd["Amount (FTD x $)"] = (ftd["Failure to Deliver"].astype(int) * ftd["Price"].astype(float)).astype(int)
    del ftd["Symbol"]
    ftd = ftd[['Date', 'Failure to Deliver', 'Price', 'Amount (FTD x $)', 'T+35 Date']]
    ftd = get_date(ftd, request.GET.get("date_to"), request.GET.get("date_from"))
    df = ftd.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def earnings_calendar(request):
    """
    Get earnings for the upcoming week. Data from yahoo finance
    """
    df = pd.read_sql_query("SELECT * FROM earnings_calendar ORDER BY earning_date ASC", conn)
    df = get_date(df, request.GET.get("date_to"), request.GET.get("date_from"), "earning_date")
    df = df.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def subreddit_count(request, ticker_selected="GME"):
    """
    Get subreddit user count, growth, active users over time.
    """
    pd.options.display.float_format = '{:.2f}'.format
    ticker_selected = default_ticker(ticker_selected)
    date_threshold = get_days_params(request, 100, 1000)
    df = pd.read_sql_query("SELECT * FROM subreddit_count WHERE ticker = '{}' AND "
                           "updated_date >= '{}' ".format(ticker_selected, date_threshold), conn)
    del df["ticker"]
    df.rename(columns={"subscribers": "Redditors", "active": "Active", "updated_date": "Date",
                       "percentage_active": "% Active", "growth": "% Growth",
                       "percentage_price_change": "% Price Change"}, inplace=True)
    df = df.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def wsb_mentions(request, ticker_selected=None):
    if ticker_selected:
        pd.options.display.float_format = '{:.2f}'.format
        date_threshold = get_days_params(request, 100, 1000)
        df = pd.read_sql_query("SELECT mentions, calls, puts, date_updated FROM wsb_trending_hourly WHERE "
                               "ticker='{}' AND date_updated >= '{}' ".format(ticker_selected, date_threshold), conn)
        df.fillna(0, inplace=True)
    else:
        date_threshold = get_days_params(request, 1, 14)

        query = "SELECT ticker AS Ticker, SUM(mentions) AS Mentions, AVG(sentiment) AS Sentiment FROM " \
                "wsb_trending_24H WHERE date_updated >= '{}' GROUP BY ticker " \
                "ORDER BY SUM(mentions) DESC".format(date_threshold)
        df = pd.read_sql_query(query, conn)
        df.index += 1
        df.reset_index(inplace=True)
        df.rename(columns={"index": "Rank"}, inplace=True)
    df = df.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def wsb_options(request):
    date_threshold = get_days_params(request, 1, 14)

    df = pd.read_sql_query("SELECT ticker as Ticker, SUM(calls) AS Calls, SUM(puts) AS Puts, "
                           "CAST(SUM(calls) AS float)/SUM(puts) as Ratio FROM wsb_trending_24H "
                           "WHERE date_updated >= '{}' GROUP BY ticker ORDER BY SUM(puts + calls) "
                           "DESC LIMIT 30".format(date_threshold), conn)
    df.fillna(0, inplace=True)
    df = df.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def government(request, gov_type="senate"):
    mapping_dict = {"senate": "Senator", "house": "Representative"}
    col_name = mapping_dict[gov_type]

    name = request.GET.get("name")
    ticker = request.GET.get("ticker")
    state = request.GET.get("state")

    df = pd.read_csv(f"database/government/{gov_type}.csv")
    df["Disclosure Date"] = df["Disclosure Date"].astype(str)
    df.fillna(0, inplace=True)
    df_copy = df.copy()

    final_dict = {}
    if name:
        name_list = df_copy[col_name].drop_duplicates().sort_values().to_list()
        df = df[df[col_name] == name]
        final_dict = {**final_dict, **{"names_available": name_list}}
    if ticker:
        ticker_list = df_copy["Ticker"].drop_duplicates().sort_values().to_list()
        ticker_list.remove("Unknown")
        ticker_list.sort()
        ticker = ticker.upper()
        df = df[df["Ticker"] == ticker]
        del df["Ticker"]
        del df["Asset Description"]
        final_dict = {**final_dict, **{"tickers_available": ticker_list}}
    if state:
        district_list = df_copy["District"].str[:2].unique().tolist()
        state = state.upper()
        df = df[df["District"].str.contains(state)]
        final_dict = {**final_dict, **{"districts_available": district_list}}
    df = get_date(df, request.GET.get("date_to"), request.GET.get("date_from"), "Transaction Date")
    df = df.to_dict(orient="records")
    final_dict = {**{gov_type: df}, **final_dict}
    return JSONResponse(final_dict)


@csrf_exempt
def reverse_repo(request):
    pd.options.display.float_format = '{:.2f}'.format
    date_threshold = get_days_params(request, 100, 10000)
    reverse_repo_stats = pd.read_sql_query("SELECT * FROM reverse_repo "
                                           "WHERE record_date >= '{}' ".format(date_threshold), conn)
    reverse_repo_stats['Moving Avg'] = reverse_repo_stats['amount'].rolling(window=7).mean()
    reverse_repo_stats.rename(columns={"record_date": "Date", "amount": "Amount", "parties": "Num Parties",
                                       "average": "Average"}, inplace=True)
    reverse_repo_stats.fillna(0, inplace=True)
    df = reverse_repo_stats.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def daily_treasury(request):
    pd.options.display.float_format = '{:.2f}'.format
    date_threshold = get_days_params(request, 100, 10000)
    daily_treasury_stats = pd.read_sql_query("SELECT * FROM daily_treasury "
                                             "WHERE record_date >= '{}' ".format(date_threshold), conn)
    daily_treasury_stats['Moving Avg'] = daily_treasury_stats['close_today_bal'].rolling(window=7).mean()
    daily_treasury_stats.rename(columns={"record_date": "Date", "close_today_bal": "Close Balance",
                                         "open_today_bal": "Open Balance", "amount_change": "Amount Change",
                                         "percent_change": "Percent Change"},
                                inplace=True)
    daily_treasury_stats.fillna(0, inplace=True)
    df = daily_treasury_stats.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def inflation(request):
    pd.options.display.float_format = '{:.1f}'.format
    inflation_stats = pd.read_sql_query("SELECT * FROM inflation", conn)
    inflation_stats.set_index("Year", inplace=True)
    inflation_stats.fillna(0, inplace=True)
    df = inflation_stats.to_dict(orient="index")
    return JSONResponse(df)


@csrf_exempt
def retail_sales(request):
    """
    Get retail sales. Data is from https://ycharts.com/indicators/us_retail_and_food_services_sales
    """
    pd.options.display.float_format = '{:.2f}'.format
    date_threshold = get_days_params(request, 100, 10000)
    retail_stats = pd.read_sql_query("SELECT * FROM retail_sales "
                                     "WHERE record_date >= '{}' ".format(date_threshold), conn)
    retail_stats.rename(columns={"record_date": "Date", "value": "Amount", "percent_change": "Percent Change",
                                 "covid_monthly_avg": "Monthly Avg Cases"}, inplace=True)
    retail_stats.fillna(0, inplace=True)
    df = retail_stats.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def initial_jobless_claims(request):
    pd.options.display.float_format = '{:.2f}'.format
    date_threshold = get_days_params(request, 100, 10000)
    jobless_claims = pd.read_sql_query("SELECT * FROM initial_jobless_claims "
                                       "WHERE record_date >= '{}' ".format(date_threshold), conn)
    jobless_claims.rename(columns={"record_date": "Date", "value": "Number", "percent_change": "Percent Change"
                                   }, inplace=True)
    jobless_claims.fillna(0, inplace=True)
    df = jobless_claims.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def short_interest(request):
    """
    Get short interest of ticker. Data from https://www.stockgrid.io/shortinterest
    """
    pd.options.display.float_format = '{:.2f}'.format
    df_high_short_interest = pd.read_sql("SELECT * FROM short_interest", con=conn)
    df_high_short_interest.reset_index(inplace=True)
    df_high_short_interest.rename(columns={"index": "Rank"}, inplace=True)
    df_high_short_interest["Rank"] = df_high_short_interest["Rank"] + 1
    df = df_high_short_interest.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def low_float(request):
    """
    Get short interest of ticker. Data if from lowfloat.com
    """
    pd.options.display.float_format = '{:.2f}'.format
    df_low_float = pd.read_sql("SELECT * FROM low_float", con=conn)
    df_low_float.reset_index(inplace=True)
    df_low_float.rename(columns={"index": "Rank"}, inplace=True)
    df_low_float["Rank"] = df_low_float["Rank"] + 1
    df = df_low_float.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def ipo_calendar(request):
    df = pd.read_csv("database/ipo_calendar.csv").to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def stocktwits(request, ticker_selected=None):
    if ticker_selected:
        ticker_selected = default_ticker(ticker_selected)
        df = pd.read_sql_query("SELECT rank, watchlist, date_updated FROM stocktwits_trending WHERE "
                               "symbol='{}' ".format(ticker_selected), conn)
    else:
        df = pd.read_sql_query("SELECT rank, watchlist, symbol FROM stocktwits_trending "
                               "ORDER BY date_updated DESC LIMIT 30", conn)
    df = df.to_dict(orient="records")
    return JSONResponse(df)


@csrf_exempt
def market_summary(request):
    pd.options.display.float_format = '{:.2f}'.format

    if request.GET.get("type") == "nasdaq100":
        filename = "database/indices/nasdaq100_heatmap.csv"
        title = "Nasdaq 100"
    elif request.GET.get("type") == "dia":
        filename = "database/indices/dia_heatmap.csv"
        title = "DIA"
    elif request.GET.get("type") == "wsb":
        title = "Wallstreetbets"
        df = pd.read_sql_query("SELECT ticker, mentions, mkt_cap, price_change FROM wsb_yf", conn)
        df.fillna(0, inplace=True)
        df = {title: df.to_dict(orient="records")}
        return JSONResponse(df)
    else:
        filename = "database/indices/snp500_heatmap.csv"
        title = "S&P 500"

    df = pd.read_csv(filename)
    df.fillna("N/A", inplace=True)
    return JSONResponse({title: df.to_dict(orient="records")})


@csrf_exempt
def jim_cramer(request, ticker_selected=None):
    df = pd.read_sql_query("SELECT DISTINCT * FROM jim_cramer_trades ORDER BY Date DESC", conn)
    if ticker_selected:
        df = df[df["Symbol"] == ticker_selected.upper()]
    if request.GET.get("segment"):
        df = df[df["Segment"] == request.GET.get("segment").title()]
    if request.GET.get("call"):
        df = df[df["Call"] == request.GET.get("call").title()]
    df = get_date(df, request.GET.get("date_to"), request.GET.get("date_from"))
    df = df.to_dict(orient="records")
    return JSONResponse(df)
