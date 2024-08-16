"""
Script to create database inside scheduled_tasks folder
"""
import os
import sys
import mysql.connector

sys.path.append(os.path.join(os.path.dirname(__file__), "../"))

try:
    from helpers import connect_mysql_database, config_keys
    cnx, cur, engine = connect_mysql_database()
except mysql.connector.ProgrammingError:
    cnx = mysql.connector.connect(user=config_keys["MYSQL_USER"],
                                  password=config_keys["MYSQL_PASSWORD"],
                                  host=config_keys["MYSQL_HOST"])
    cur = cnx.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {config_keys['MYSQL_DATABASE']}")
    from helpers import connect_mysql_database
    cnx, cur, engine = connect_mysql_database()


def database():
    print("Creating/Updating DB...")

    if not os.path.exists("database"):
        os.mkdir("database")
        os.mkdir("database/failure_to_deliver")
        os.mkdir("database/failure_to_deliver/csv")
        os.mkdir("database/government")
        with open("database/yf_cached_api.json", "w") as r:
            r.write("{}")

    cur.execute("CREATE TABLE IF NOT EXISTS stocksera_trending ("
                "ticker VARCHAR(10), "
                "name VARCHAR(300), "
                "count INTEGER, "
                "UNIQUE(ticker))")

    cur.execute("CREATE table IF NOT EXISTS wsb_trending_24H ("
                "ticker VARCHAR(10), "
                "mentions INTEGER, "
                "sentiment FLOAT, "
                "calls INTEGER, "
                "puts INTEGER, "
                "date_updated VARCHAR(20), "
                "INDEX (date_updated), "
                "INDEX (ticker) )")

    cur.execute("CREATE table IF NOT EXISTS wsb_trending_hourly ("
                "ticker VARCHAR(10), "
                "mentions INTEGER, "
                "sentiment FLOAT, "
                "calls INTEGER, "
                "puts INTEGER, "
                "date_updated VARCHAR(20), "
                "INDEX (date_updated), "
                "INDEX (ticker) )")

    cur.execute("CREATE table IF NOT EXISTS wsb_discussions ("
                "ticker VARCHAR(10), "
                "text_body VARCHAR(500), "
                "sentiment FLOAT, "
                "date_posted VARCHAR(20), "
                "INDEX (ticker) )")

    cur.execute("CREATE table IF NOT EXISTS wsb_yf ("
                "ticker VARCHAR(10), "
                "mkt_cap VARCHAR(30), "
                "price_change FLOAT, "
                "difference_sma FLOAT, "
                "difference_52w_high FLOAT, "
                "difference_52w_low FLOAT, "
                "mentions INTEGER )")

    cur.execute("CREATE table IF NOT EXISTS crypto_trending_24H ("
                "ticker VARCHAR(10), "
                "mentions INTEGER, "
                "sentiment FLOAT, "
                "date_updated VARCHAR(20), "
                "INDEX (date_updated), "
                "INDEX (ticker) )")

    cur.execute("CREATE table IF NOT EXISTS crypto_trending_hourly ("
                "ticker VARCHAR(10), "
                "mentions INTEGER, "
                "sentiment FLOAT, "
                "date_updated VARCHAR(20), "
                "INDEX (date_updated), "
                "INDEX (ticker) )")

    for i in ["wsb", "crypto"]:
        cur.execute("CREATE table IF NOT EXISTS {}_change ("
                    "ticker VARCHAR(10), "
                    "mentions INTEGER, "
                    "percent_change FLOAT )".format(i))

        cur.execute("CREATE table IF NOT EXISTS {}_word_cloud ("
                    "word VARCHAR(100), "
                    "mentions INTEGER, "
                    "date_updated VARCHAR(20) )".format(i))

    cur.execute("CREATE table IF NOT EXISTS wsb_etf ("
                "ticker VARCHAR(10), "
                "open_date VARCHAR(20), "
                "open_price VARCHAR(20), "
                "close_date VARCHAR(20), "
                "close_price VARCHAR(20), "
                "percentage VARCHAR(20), "
                "status VARCHAR(20))")

    cur.execute("CREATE table IF NOT EXISTS earnings ("
                "`date` VARCHAR(20), "
                "`hour` VARCHAR(20), "
                "`ticker` VARCHAR(10), "
                "`eps_est` VARCHAR(20), "
                "`eps_act` VARCHAR(20), "
                "`revenue_est` VARCHAR(20), "
                "`revenue_act` VARCHAR(20), "
                "`year` VARCHAR(10), "
                "`quarter` VARCHAR(10),"
                "`mkt_cap` VARCHAR(20),"
                "UNIQUE(ticker, `hour`),"
                "INDEX (`date`)  )")

    cur.execute("CREATE table IF NOT EXISTS subreddit_count ("
                "updated_date VARCHAR(20),"
                "ticker VARCHAR(10), "
                "subreddit VARCHAR(50), "
                "subscribers INTEGER, "
                "active INTEGER, "
                "percentage_active FLOAT, "
                "growth FLOAT, "
                "percentage_price_change FLOAT, "
                "UNIQUE(ticker, subreddit, updated_date),"
                "INDEX (ticker) )")

    cur.execute("CREATE table IF NOT EXISTS twitter_followers ("
                "ticker VARCHAR(10), "
                "followers INTEGER, "
                "updated_date VARCHAR(20), "
                "UNIQUE(ticker, updated_date) )")

    cur.execute("CREATE table IF NOT EXISTS twitter_trending ("
                "ticker VARCHAR(10), "
                "tweet_count INTEGER, "
                "updated_date VARCHAR(20),"
                "UNIQUE(ticker, updated_date) )")

    cur.execute("CREATE table IF NOT EXISTS short_interest ("
                "ticker VARCHAR(10), "
                "date VARCHAR(20), "
                "short_interest INTEGER, "
                "average_vol INTEGER, "
                "days_to_cover FLOAT, "
                "percent_float_short FLOAT)")

    cur.execute("CREATE table IF NOT EXISTS low_float ("
                "ticker VARCHAR(10), "
                "company_name VARCHAR(200), "
                "exchange VARCHAR(100), "
                "previous_close FLOAT, "
                "one_day_change FLOAT, "
                "floating_shares VARCHAR(20), "
                "outstanding_shares VARCHAR(20),"
                "short_int VARCHAR(20), "
                "market_cap VARCHAR(20), "
                "industry VARCHAR(50) )")

    cur.execute("CREATE table IF NOT EXISTS fear_and_greed ("
                "date VARCHAR(20), "
                "value FLOAT, "
                "close_price FLOAT, "
                "rating VARCHAR(20), "
                "UNIQUE (date) )")
    
    cur.execute("CREATE table IF NOT EXISTS reverse_repo ("
                "record_date VARCHAR(20), "
                "amount FLOAT, "
                "parties INTEGER, "
                "average FLOAT, "
                "UNIQUE (record_date) )")

    cur.execute("CREATE table IF NOT EXISTS daily_treasury ("
                "record_date VARCHAR(20), "
                "close_today_bal FLOAT, "
                "open_today_bal FLOAT, "
                "amount_change FLOAT, "
                "percent_change FLOAT, "
                "UNIQUE (record_date) )")

    cur.execute("CREATE table IF NOT EXISTS interest_rates ("
                "record_date VARCHAR(20), "
                "interest FLOAT, "
                "UNIQUE (record_date) )")

    cur.execute("CREATE table IF NOT EXISTS retail_sales ("
                "record_date VARCHAR(20), "
                "value FLOAT, "
                "percent_change FLOAT, "
                "covid_monthly_avg INTEGER, "
                "UNIQUE (record_date) )")

    cur.execute("CREATE table IF NOT EXISTS initial_jobless_claims ("
                "record_date VARCHAR(20), "
                "value INTEGER, "
                "percent_change FLOAT, "
                "UNIQUE (record_date) )")

    cur.execute("CREATE table IF NOT EXISTS usa_inflation ("
                "Year VARCHAR(10), "
                "Jan FLOAT, "
                "Feb FLOAT, "
                "Mar FLOAT, "
                "Apr FLOAT, "
                "May FLOAT, "
                "Jun FLOAT, "
                "Jul FLOAT, "
                "Aug FLOAT, "
                "Sep FLOAT, "
                "Oct FLOAT, "
                "Nov FLOAT, "
                "`Dec` FLOAT, "
                "`Avg` FLOAT )")

    cur.execute("CREATE table IF NOT EXISTS world_inflation ("
                "Country VARCHAR(100), "
                "Last FLOAT, "
                "Previous FLOAT, "
                "Reference VARCHAR(20), "
                "Continent VARCHAR(50) )")

    cur.execute("CREATE table IF NOT EXISTS short_volume ("
                "`Date` VARCHAR(20), "
                "`Ticker` VARCHAR(10), "
                "`Short Vol` DOUBLE, "
                "`Short Exempt Vol` DOUBLE, "
                "`Total Vol` DOUBLE, "
                "`% Shorted` DOUBLE, "
                "UNIQUE (`Date`, `Ticker`), "
                "INDEX (Ticker) )")

    cur.execute("CREATE table IF NOT EXISTS highest_short_volume ("
                "`Rank` VARCHAR(20), "
                "`Ticker` VARCHAR(10), "
                "`Short Vol` DOUBLE, "
                "`Short Exempt Vol` DOUBLE, "
                "`Total Vol` DOUBLE, "
                "`% Shorted` FLOAT, "
                "`Previous Close` VARCHAR(20), "
                "`1 Day Change %` VARCHAR(20), "
                "`Market Cap` VARCHAR(20), "
                "INDEX (Ticker) )")

    cur.execute("CREATE table IF NOT EXISTS ftd ("
                "`Date` VARCHAR(20), "
                "`Ticker` VARCHAR(10), "
                "`Failure to Deliver` DOUBLE, "
                "`Price` VARCHAR(20), "
                "`T+35 Date` VARCHAR(20), "
                "UNIQUE (`Date`, `Ticker`), "
                "INDEX (Ticker) )")

    cur.execute("CREATE table IF NOT EXISTS top_ftd ("
                "`Date` VARCHAR(20), "
                "`Ticker` VARCHAR(10), "
                "`FTD` VARCHAR(20), "
                "`Price` VARCHAR(20), "
                "`FTD x $` VARCHAR(20), "
                "`T+35 Date` VARCHAR(20) )")

    cur.execute("CREATE table IF NOT EXISTS sec_fillings ("
                "ticker VARCHAR(10), "
                "filling VARCHAR(100), "
                "description VARCHAR(100), "
                "filling_date VARCHAR(20), "
                "report_url VARCHAR(300), "
                "filing_url VARCHAR(300) ) ")

    cur.execute("CREATE table IF NOT EXISTS daily_ticker_news ("
                "Ticker VARCHAR(10), "
                "Date VARCHAR(20), "
                "Title VARCHAR(500), "
                "Link VARCHAR(300), "
                "Sentiment VARCHAR(20) )")

    cur.execute("CREATE table IF NOT EXISTS insider_trading ("
                "Ticker VARCHAR(10), "
                "Name VARCHAR(200), "
                "Relationship VARCHAR(200), "
                "TransactionDate VARCHAR(20), "
                "TransactionType VARCHAR(100), "
                "Cost FLOAT, "
                "Shares INTEGER, "
                "Value INTEGER, "
                "SharesLeft INTEGER,"
                "URL VARCHAR(300) )")

    cur.execute("CREATE table IF NOT EXISTS latest_insider_trading ("
                "Ticker VARCHAR(10), "
                "Name VARCHAR(200), "
                "Relationship VARCHAR(200), "
                "TransactionDate VARCHAR(20), "
                "TransactionType VARCHAR(100), "
                "Cost FLOAT, "
                "Shares INTEGER, "
                "Value INTEGER, "
                "SharesLeft INTEGER,"
                "DateFilled VARCHAR(20), "
                "URL VARCHAR(300), "
                "UNIQUE (Ticker, Name, Relationship, TransactionDate, TransactionType, Cost, Shares, "
                "Value, SharesLeft, DateFilled) )")

    cur.execute("CREATE table IF NOT EXISTS latest_insider_trading_analysis ("
                "Ticker VARCHAR(10), "
                "Amount INTEGER, "
                "MktCap INTEGER, "
                "Proportion FLOAT) ")

    cur.execute("CREATE table IF NOT EXISTS related_tickers ("
                "ticker VARCHAR(10), "
                "ticker1 VARCHAR(10), "
                "ticker2 VARCHAR(10), "
                "ticker3 VARCHAR(10), "
                "ticker4 VARCHAR(10), "
                "ticker5 VARCHAR(10), "
                "ticker6 VARCHAR(10) )")

    cur.execute("CREATE table IF NOT EXISTS stocktwits_trending ("
                "`rank` INTEGER, "
                "watchlist INTEGER, "
                "ticker VARCHAR(10), "
                "date_updated VARCHAR(20),"
                "INDEX (ticker) )")

    cur.execute("CREATE TABLE IF NOT EXISTS shares_available ("
                "ticker VARCHAR(10), "
                "fee  FLOAT, "
                "available INTEGER, "
                "date_updated VARCHAR(20), "
                "UNIQUE(ticker, fee, available, date_updated),"
                "INDEX (ticker) )")

    cur.execute("CREATE TABLE IF NOT EXISTS highest_shares_available ("
                "ticker VARCHAR(10), "
                "fee  FLOAT, "
                "available INTEGER, "
                "UNIQUE(ticker, fee, available),"
                "INDEX (ticker) )")

    cur.execute("CREATE TABLE IF NOT EXISTS threshold_securities ("
                "ticker VARCHAR(10), "
                "date_updated VARCHAR(20), "
                "UNIQUE(ticker, date_updated),"
                "INDEX (ticker) )")

    cur.execute("CREATE TABLE IF NOT EXISTS ipo_calendar ("
                "`Date` VARCHAR(20), "
                "`Symbol`  VARCHAR(10), "
                "`Name` VARCHAR(200), "
                "`Expected Price` VARCHAR(10), "
                "`Number Shares` VARCHAR(20), "
                "`Mkt Cap` VARCHAR(20), "
                "`Status` VARCHAR(50), "
                "`Exchange` VARCHAR(50) )")

    cur.execute("CREATE TABLE IF NOT EXISTS market_news ("
                "`Date` VARCHAR(20), "
                "`Title`  VARCHAR(300), "
                "`Source` VARCHAR(100), "
                "`URL` VARCHAR(300), "
                "`Section` VARCHAR(50), "
                "UNIQUE(Date, Title), "
                "INDEX (Date) )")

    cur.execute("CREATE TABLE IF NOT EXISTS trading_halts ("
                "`Halt Date` VARCHAR(20), "
                "`Halt Time`  VARCHAR(20), "
                "`Ticker` VARCHAR(10), "
                "`Exchange` VARCHAR(100), "
                "`Reason` VARCHAR(100), "
                "`Resume Date` VARCHAR(20), "
                "`Resume Time` VARCHAR(20), "
                "UNIQUE(`Halt Date`, `Halt Time`, `Ticker`), "
                "INDEX(`Halt Date`, `Halt Time`) )")

    cur.execute("CREATE TABLE IF NOT EXISTS stock_splits ("
                "`Date` VARCHAR(20), "
                "`Split From`  VARCHAR(20), "
                "`Split To` VARCHAR(20), "
                "`Ticker` VARCHAR(10), "
                "`Reverse` VARCHAR(10), "
                "UNIQUE(`Date`, `Split From`, `Split To`, `Ticker`, `Reverse`), "
                "INDEX(`Date`) )")

    cur.execute("CREATE TABLE IF NOT EXISTS dividends ("
                "`Ticker` VARCHAR(10), "
                "`Cash` FLOAT, "
                "`Declaration Date`  VARCHAR(10), "
                "`Ex-Div Date` VARCHAR(10), "
                "`Pay Date` VARCHAR(10), "
                "`Record Date` VARCHAR(10), "
                "`Type` VARCHAR(10), "
                "`Frequency` VARCHAR(10), "
                "UNIQUE(`Ticker`, `Declaration Date`), "
                "INDEX(`Declaration Date`) )")

    cur.execute("CREATE TABLE IF NOT EXISTS largest_companies ("
                "`Ticker` VARCHAR(10), "
                "`Price` FLOAT, "
                "`Change`  FLOAT, "
                "`% Change` FLOAT, "
                "`Market Cap` VARCHAR(20), "
                "UNIQUE(`Ticker`), "
                "INDEX(`Ticker`) )")

    print("Creating/Updating DB Successfully Completed...\n")


if __name__ == '__main__':
    database()
