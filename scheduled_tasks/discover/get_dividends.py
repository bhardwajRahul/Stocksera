import os
import sys
import requests
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))
from helpers import connect_mysql_database, config_keys

cnx, cur, engine = connect_mysql_database()


def main():
    """
    Get Dividends from Polygon API
    """
    print("Getting Dividends...")

    url = f"https://api.polygon.io/v3/reference/dividends?limit=1000&apiKey={config_keys['POLYGON_KEY']}"

    df = pd.DataFrame(requests.get(url).json()["results"])
    df = df[
        [
            "ticker",
            "cash_amount",
            "declaration_date",
            "ex_dividend_date",
            "pay_date",
            "record_date",
            "dividend_type",
            "frequency",
        ]
    ]
    df.fillna(0, inplace=True)

    cur.executemany(
        "INSERT IGNORE INTO dividends VALUES (%s ,%s ,%s ,%s, %s ,%s ,%s ,%s)",
        df.values.tolist(),
    )
    cnx.commit()

    print("Dividends Successfully Completed...\n")


if __name__ == "__main__":
    main()
