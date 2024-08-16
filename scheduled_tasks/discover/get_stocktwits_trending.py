import os
import sys
import requests
import pandas as pd
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
from helpers import connect_mysql_database, header

cnx, cur, engine = connect_mysql_database()


def main():
    """
    Get stocktwits trending tickers
    """
    print("Getting Stocktwits...")
    trending = requests.get("https://api.stocktwits.com/api/2/trending/symbols.json", headers=header).json()["symbols"]
    df = pd.DataFrame.from_dict(trending)[["symbol", "watchlist_count"]]
    df["date_updated"] = str(datetime.utcnow()).split(":")[0] + ":00"
    df.index += 1
    df.reset_index(inplace=True)
    df.rename(columns={"index": "rank", "symbol": "ticker", "watchlist_count": "watchlist"}, inplace=True)
    df.to_sql("stocktwits_trending", engine, if_exists="append", index=False)
    print("Stocktwits Successfully Completed...\n")


if __name__ == '__main__':
    main()
