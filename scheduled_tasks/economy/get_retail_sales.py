import os
import sys
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "../.."))

from scheduled_tasks.economy.ychart_connection import ychart_data
from helpers import connect_mysql_database

cnx, cur, engine = connect_mysql_database()


def retail_sales():
    """
    Get retail sales and compare it with avg monthly covid cases
    """
    print("Getting Retail Sales...")

    df = ychart_data("https://ycharts.com/indicators/us_retail_and_food_services_sales")

    combined_df = pd.concat([df[6][::-1], df[5][::-1]], axis=0)

    combined_df["Value"] = combined_df["Value"].str.replace("B", "")
    combined_df["Value"] = combined_df["Value"].astype(float)

    combined_df["Percent Change"] = combined_df["Value"].shift(1)
    combined_df["Percent Change"] = combined_df["Percent Change"].astype(float)
    combined_df["Percent Change"] = (
        100
        * (combined_df["Value"] - combined_df["Percent Change"])
        / combined_df["Percent Change"]
    )
    combined_df["Percent Change"] = combined_df["Percent Change"].round(2)

    combined_df["Date"] = combined_df["Date"].astype("datetime64[ns]").astype(str)

    covid_df = pd.read_csv(r"https://covid.ourworldindata.org/data/owid-covid-data.csv")

    usa_df = covid_df[covid_df["iso_code"] == "USA"]
    usa_df.index = pd.to_datetime(usa_df["date"], errors="coerce")
    usa_df = usa_df.groupby(pd.Grouper(freq="M"))
    usa_df = usa_df.mean()["new_cases"]
    usa_df = pd.DataFrame(usa_df)
    usa_df["new_cases"] = usa_df["new_cases"].round(2)
    usa_df.reset_index(inplace=True)
    usa_df["date"] = usa_df["date"].astype(str)
    usa_df.rename(columns={"date": "Date"}, inplace=True)

    combined_df = pd.merge(combined_df, usa_df, how="left", on="Date")
    combined_df.fillna(0, inplace=True)

    cur.executemany(
        "INSERT IGNORE INTO retail_sales VALUES (%s, %s, %s, %s)",
        combined_df.values.tolist(),
    )

    print("Retail Sales Successfully Completed...\n")


if __name__ == "__main__":
    retail_sales()
