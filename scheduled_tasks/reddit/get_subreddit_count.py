import os
import sys
import yfinance as yf
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "..//.."))
from scheduled_tasks.reddit.reddit_utils import *
from helpers import connect_mysql_database

cnx, cur, engine = connect_mysql_database()

# key of the dict is the symbol of the stock (if applicable), value is the subreddit
interested_stocks_subreddits = {
    "SUMMARY": [
        "wallstreetbets",
        "stocks",
        "options",
        "pennystocks",
        "SPACs",
        "Shortsqueeze",
    ],
    "GME": ["Superstonk"],
    "AMC": ["amcstock"],
    "CLOV": ["CLOV"],
    "BB": ["BB_Stock"],
    "AMD": ["AMD_Stock"],
    "UWMC": ["UWMCShareholders"],
    "NIO": ["NIO"],
    "TSLA": ["teslainvestorsclub"],
    "AAPL": ["AAPL"],
    "NOK": ["Nokia_stock"],
    "NVDA": ["NVDA_Stock"],
    "MSFT": ["Microsoft"],
    "RBLX": ["RBLX"],
    "F": ["Fordstock"],
    "PLTR": ["PLTR"],
    "COIN": ["CoinBase"],
    "RKT": ["TeamRKT"],
    "MVIS": ["MVIS"],
    "FUBO": ["fuboinvestors"],
    "VIAC": ["VIAC"],
    "SNDL": ["SNDL_Stock"],
    "SPCE": ["SPCE"],
    "SNAP": ["SNAP"],
    "OCGN": ["Ocugen"],
    "ROKU": ["Roku"],
    "BABA": ["baba"],
    "SE": ["SE_stock"],
    "EXPR": ["EXPR"],
    "KOSS": ["KOSSstock"],
    "SOFI": ["sofistock"],
    "WKHS": ["WKHS"],
    "TLRY": ["TLRY"],
    "CLNE": ["CLNE"],
    "WISH": ["Wishstock"],
    "CLF": ["clf_Stock"],
    "GOEV": ["canoo"],
    "DKNG": ["DKNG"],
    "AMZN": ["AMZN"],
    "XPEV": ["XPEV"],
    "NKLA": ["NKLA"],
    "CLVS": ["CLVSstock"],
    "BNGO": ["BNGO"],
    "SKLZ": ["SKLZ"],
    "CRSR": ["CRSR"],
    "NAKD": ["NAKDstock"],
    "ICLN": ["ICLN"],
    "PSFE": ["PSFE"],
    "XELA": ["XELAstock"],
    "SPRT": ["SPRT"],
    "MMAT": ["MMAT"],
    "HOOD": ["HOODstock"],
    "LCID": ["LCID"],
    "NVAX": ["NVAX"],
    "MRNA": ["ModernaStock"],
    "SOS": ["SOSStock"],
    "CTRM": ["CTRM"],
    "ATER": ["ATERstock"],
    "RKLB": ["RKLB"],
    "BBIG": ["BBIG"],
    "SAVA": ["SAVA_stock"],
    "GREE": ["gree"],
    "CEI": ["CEI_stock"],
}

interested_crypto_subreddits = {
    "CRYPTO": ["cryptocurrency"],
    "BTC": ["Bitcoin"],
    "ETH": ["ethereum"],
    "ADA": ["cardano"],
    "BNB": ["binance"],
    "UDST": ["Tether"],
    "XRP": ["XRP"],
    "DOGE": ["dogecoin"],
    "DOT": ["Polkadot"],
    "USDC": ["USDC"],
    "SOL": ["Solana"],
    "SHIB": ["SHIBArmy"],
    "BUSD": ["binance"],
    "UNI": ["UNISwap"],
    "LINK": ["Chainlink"],
    "MATIC": ["maticnetwork"],
    "ICP": ["ICPTrader"],
    "CAKE": ["pancakeswap"],
    "CRO": ["cro"],
    "ATOM": ["cosmosnetwork"],
    "ALGO": ["algorand"],
    "XLM": ["xlm"],
    "XMR": ["xmrtrader"],
    "AAVE": ["Aave_Official"],
    "NEO": ["NEO"],
    "BCH": ["Bitcoincash"],
    "LRC": ["loopringorg"],
    "IMX": ["ImmutableX"],
}
date_updated = str(datetime.now()).split()[0]


def subreddit_count():
    """
    Get number of redditors, percentage of active redditors and growth in new redditors
    """
    for key, subreddit_names in {
        **interested_stocks_subreddits,
        **interested_crypto_subreddits,
    }.items():
        for subreddit_name in subreddit_names:
            try:
                subreddit = reddit.subreddit(subreddit_name)
                subscribers = subreddit.subscribers
                active = subreddit.accounts_active
                percentage_active = round((active / subscribers) * 100, 2)

                cur.execute(
                    "SELECT subscribers FROM subreddit_count WHERE subreddit=%s ORDER BY subscribers DESC LIMIT 1",
                    (subreddit_name,),
                )
                try:
                    prev_subscribers = cur.fetchone()[0]
                    growth = round((subscribers / prev_subscribers) * 100 - 100, 2)
                except TypeError:
                    growth = 0

                if key in interested_stocks_subreddits.keys() and key != "SUMMARY":
                    price_df = (
                        yf.Ticker(key)
                        .history(period="1y", interval="1d")
                        .reset_index()
                        .iloc[::-1]
                    )
                    price_df["% Price Change"] = price_df["Close"].shift(-1)
                    price_df["% Price Change"] = (
                        100
                        * (price_df["Close"] - price_df["% Price Change"])
                        / price_df["% Price Change"]
                    )
                    price_df["Date"] = price_df["Date"].astype(str)
                    price_df = price_df.round(2)
                    change_price = price_df[price_df["Date"] == date_updated][
                        "% Price Change"
                    ].values
                    if len(change_price == 1):
                        change_price = change_price[0]
                    else:
                        change_price = 0
                else:
                    change_price = 0

                cur.execute(
                    "INSERT IGNORE INTO subreddit_count VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        date_updated,
                        key,
                        subreddit_name,
                        subscribers,
                        active,
                        percentage_active,
                        growth,
                        change_price,
                    ),
                )
                cnx.commit()
            except:
                print("Error")


def update_last_price():
    """
    Update last close price of ticker after market close
    """
    cur.execute(
        "SELECT updated_date FROM subreddit_count WHERE ticker='AMC' ORDER BY updated_date DESC"
    )
    last_date = cur.fetchone()[0]
    for key, subreddit_names in interested_stocks_subreddits.items():
        for subreddit_name in subreddit_names:
            if key != "SUMMARY":
                price_df = (
                    yf.Ticker(key)
                    .history(period="1y", interval="1d")
                    .reset_index()
                    .iloc[::-1]
                )
                price_df["% Price Change"] = price_df["Close"].shift(-1)
                price_df["% Price Change"] = (
                    100
                    * (price_df["Close"] - price_df["% Price Change"])
                    / price_df["% Price Change"]
                )
                price_df["Date"] = price_df["Date"].astype(str)
                price_df = price_df.round(2)
                change_price = price_df[price_df["Date"] == last_date][
                    "% Price Change"
                ].values
                if len(change_price == 1):
                    change_price = change_price[0]
                else:
                    change_price = 0
                cur.execute(
                    "UPDATE subreddit_count SET percentage_price_change=%s WHERE ticker=%s AND updated_date=%s",
                    (change_price, key, last_date),
                )
                cnx.commit()


def main():
    print("Getting Subreddit Subscriber Count...")
    subreddit_count()
    update_last_price()
    print("Subreddit Subscriber Count Successfully Completed...\n")


if __name__ == "__main__":
    main()
