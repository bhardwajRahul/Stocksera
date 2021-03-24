import os
import requests
from datetime import *

from custom_words import *

import psycopg2
import yfinance as yf
import pandas as pd
from django.shortcuts import render
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

# If using database from Heroku
if os.environ.get('DATABASE_URL'):
    postgres_url = os.environ.get('DATABASE_URL')
    conn = psycopg2.connect(postgres_url, sslmode='require')
# If using local database
else:
    conn = psycopg2.connect(user="postgres",
                            password="admin",
                            database="stocks_analysis")

conn.autocommit = True
db = conn.cursor()

analyzer = SentimentIntensityAnalyzer()
analyzer.lexicon.update(new_words)

stopwords = nltk.corpus.stopwords.words("english")
url = 'https://newsapi.org/v2/everything?'


def home(request):
    tickers_list = pd.read_csv(r"nasdaq_screener_1613136998474.csv")
    list_of_sectors = sorted(tickers_list['Sector'].astype(str).unique().tolist())[:-1]
    list_of_industries = sorted(tickers_list['Industry'].astype(str).unique().tolist())[:-1]

    popular_ticker_list = ["SPY", "GOOG", "AAPL", "AMZN", "TSLA", "MSFT", "PLTR", "NVDA", "BB", "ARKK", "ARKF"]
    popular_name_list = ["S&P500 ETF", "Alphabet", "Apple", "Amazon", "Tesla", "Microsoft", "Palantir",
                         "NVIDIA", "BlackBerry", "ARK Invest", "ARK Fintech"]

    price_list = list()
    for ticker in popular_ticker_list:
        ticker = yf.Ticker(ticker)
        price_df = ticker.history(period="3d")['Close']
        opening_price = float(price_df.iloc[1])
        closing_price = float(price_df.iloc[2])

        price_change = str(round(closing_price - opening_price, 2))

        percentage_change = round((1 - opening_price / closing_price) * 100, 2)
        if percentage_change >= 0:
            price_change = '+' + price_change
            percentage_change = '+' + str(percentage_change)

        price_list.append([round(closing_price, 2), price_change, percentage_change])

    if request.method == "GET":
        return render(request, 'home.html', {"list_of_sectors": list_of_sectors,
                                             "list_of_industries": list_of_industries,
                                             "popular_ticker_list": popular_ticker_list,
                                             "popular_name_list": popular_name_list,
                                             "price_list": price_list
                                             })


def stock_price(request):
    tickers_list = pd.read_csv(r"nasdaq_screener_1613136998474.csv")
    symbols_list = tickers_list["Symbol"]

    if request.method == "GET":
        return render(request, 'ticker_price.html', {"symbols_list": symbols_list})

    if request.method == "POST":
        ticker_selected = request.POST.get("ticker").upper()
        ticker = yf.Ticker(ticker_selected)

        # if "one_day_btn" in request.POST:
        price_df = ticker.history(period="1d", interval="1m")
        ticker_date_max = list(map(lambda x: x.split(" ")[1].split("-")[0].rsplit(":", 1)[0],
                                   price_df.index.astype(str).to_list()))
        if "five_day_btn" in request.POST:
            price_df = ticker.history(period="5d", interval="30m")
            ticker_date_max = list(map(lambda x: x.split(" ")[0], price_df.index.astype(str).to_list()))
        elif "one_month_btn" in request.POST:
            price_df = ticker.history(period="1mo", interval="1d")
            ticker_date_max = list(map(lambda x: x.rsplit(" ", 1)[0], price_df.index.astype(str).to_list()))
        elif "one_year_btn" in request.POST:
            price_df = ticker.history(period="1y")
            ticker_date_max = list(map(lambda x: x.rsplit(" ", 1)[0], price_df.index.astype(str).to_list()))
        elif "five_year_btn" in request.POST:
            price_df = ticker.history(period="5y")
            ticker_date_max = list(map(lambda x: x.rsplit(" ", 1)[0], price_df.index.astype(str).to_list()))

        # one_day_price_df = ticker.history(period="1d", interval="1m")
        # one_day_price_df['Date'] = one_day_price_df.index
        # one_day_price = list(map(lambda x: round(x, 2), one_day_price_df['Close'].to_list()))
        # one_day_date = list(map(lambda x: x.split(" ")[1].split("-")[0].rsplit(":", 1)[0],
        #                            one_day_price_df.index.astype(str).to_list()))
        # print(one_day_date)
        # five_day_price_df = ticker.history(period="5d", interval="30m")
        # five_day_price_df['Date'] = five_day_price_df.index
        # five_day_price = list(map(lambda x: round(x, 2), five_day_price_df['Close'].to_list()))
        # five_day_date = list(map(lambda x: x.split(" ")[0], five_day_price_df.index.astype(str).to_list()))
        #
        # one_month_price_df = ticker.history(period="1mo", interval="1d")
        # one_month_price_df['Date'] = one_month_price_df.index
        # one_month_price = list(map(lambda x: round(x, 2), one_month_price_df['Close'].to_list()))
        # one_month_date = list(map(lambda x: x.rsplit(" ", 1)[0], one_month_price_df.index.astype(str).to_list()))
        #
        # one_year_price_df = ticker.history(period="1y")
        # one_year_price_df['Date'] = one_year_price_df.index
        # one_year_price = list(map(lambda x: round(x, 2), one_year_price_df['Close'].to_list()))
        # one_year_date = list(map(lambda x: x.rsplit(" ", 1)[0], one_year_price_df.index.astype(str).to_list()))
        #
        # five_year_price_df = ticker.history(period="5y")
        # five_year_price_df['Date'] = five_year_price_df.index
        # five_year_price = list(map(lambda x: round(x, 2), five_year_price_df['Close'].to_list()))
        # five_year_date = list(map(lambda x: x.rsplit(" ", 1)[0], five_year_price_df.index.astype(str).to_list()))
        #
        # price_df_list = [one_day_price, five_day_price, one_month_price, one_year_price, five_year_price]
        # date_list = [one_day_date, five_day_date, one_month_date, one_year_date, five_year_date]
        # print("------------------------------------")
        # print(date_list)
        information = ticker.info
        img = information["logo_url"]
        official_name = information["longName"]
        try:
            sector = information["sector"]
            industry = information["industry"]
        except KeyError:
            sector = "-"
            industry = "-"

        mkt_open = information["regularMarketOpen"]
        mkt_close = information["previousClose"]
        mkt_low = information["regularMarketDayLow"]
        mkt_high = information["dayHigh"]
        mkt_vol = information["regularMarketVolume"]
        if mkt_vol < 1000000:
            mkt_vol = str(round(mkt_vol/1000, 2)) + "K"
        elif 1000000 <= mkt_vol < 1000000000:
            mkt_vol = str(round(mkt_vol / 1000000, 2)) + "M"
        else:
            mkt_vol = str(round(mkt_vol / 1000000000, 2)) + "B"

        mkt_year_high = information["fiftyTwoWeekHigh"]
        mkt_year_low = information["fiftyTwoWeekLow"]

        website = information["website"]
        summary = information["longBusinessSummary"]
        return render(request, 'ticker_price.html', {"ticker_selected": ticker_selected, "symbols_list": symbols_list,
                                                     "ticker_date_max": ticker_date_max,
                                                     "ticker_price_max": list(map(lambda x: round(x, 2),
                                                                                  price_df["Close"].to_list())),
                                                     "img": img, "official_name": official_name, "sector": sector,
                                                     "industry": industry, "mkt_open": mkt_open, "mkt_close": mkt_close,
                                                     "mkt_low": mkt_low, "mkt_high": mkt_high, "mkt_vol": mkt_vol,
                                                     "mkt_year_high": mkt_year_high, "mkt_year_low": mkt_year_low,
                                                     "website": website, "summary": summary,
                                                     })


def reddit_analysis(request):
    if request.method == "GET":
        return render(request, 'reddit_sentiment.html')
    else:
        subreddit = request.POST.get("subreddit")
        if subreddit == "all":
            db.execute("SELECT * FROM reddit_trending ORDER BY score DESC")
        else:
            db.execute("SELECT * FROM {} ORDER BY recent DESC".format(subreddit))
        trending_tickers = db.fetchall()
        return render(request, 'reddit_sentiment.html', {"trending_tickers": trending_tickers})


def google_analysis(request):
    url = 'https://newsapi.org/v2/everything?'
    today_date = str(datetime.now()).split(" ")[0]
    yesterday_date = str(datetime.strptime(today_date, "%Y-%m-%d") - timedelta(days=1)).split(" ")[0]
    print(today_date, yesterday_date)
    print(os.getenv('API'))
    parameters = {
        'q': 'Apple',
        'sortBy': 'popularity',
        'from': yesterday_date,
        'to': today_date,
        'language': 'en',
        'pageSize': 100,  # maximum is 100 for developer version
        'apiKey': '1fb4fff1c2f84f918ec39adca24ed426'
    }

    all_news = set()
    response = requests.get(url, params=parameters)
    print(response)
    print(len(response.json()['articles']))

    for news in response.json()['articles']:
        print(news)
        print(news['publishedAt'])
        print(news['title'])
        try:
            vs = analyzer.polarity_scores(news['title'])
            print(str(vs))
        except AttributeError:
            pass

        # words = [w for w in news['title'].split() if w.lower() not in stopwords]
        # words = nltk.word_tokenize(news['title'])
        # print(words)
        # print(news['title'])
        print(news['description'])
        try:
            vs = analyzer.polarity_scores(news['description'])
            print(str(vs))
        except AttributeError:
            pass
        print()
    return render(request, 'google_sentiment.html')


def industries_analysis(request):
    return render(request, 'industry.html')
