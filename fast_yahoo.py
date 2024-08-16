import scheduled_tasks.reddit.stocks.shared as shared
import requests
import numbers
import multitasking as multitasking
import time
import json
import pandas as pd
from datetime import datetime, timedelta

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/50.0.2661.102 Safari/537.36'}

# Refer to https://stackoverflow.com/questions/44030983/yahoo-finance-url-not-working for more configs
# key is the website link, value is the part to extract
config = {'summaryDetail': ['regularMarketOpen', 'previousClose', 'dayHigh', 'fiftyTwoWeekHigh', 'regularMarketDayLow',
                            'fiftyTwoWeekLow', 'regularMarketVolume', 'averageDailyVolume10Day', 'fiftyDayAverage',
                            'twoHundredDayAverage', 'trailingPE', 'forwardPE', 'marketCap', 'beta',
                            'trailingAnnualDividendYield', 'trailingAnnualDividendRate', 'totalAssets', 'navPrice'],
          'defaultKeyStatistics': ['sharesOutstanding', 'floatShares', 'shortRatio', 'shortPercentOfFloat',
                                   'trailingEps', 'pegRatio', 'enterpriseToRevenue', 'netIncomeToCommon',
                                   'threeYearAverageReturn', 'fiveYearAverageReturn'],
          'summaryProfile': ['industry', 'sector', 'website', 'longBusinessSummary', 'fullTimeEmployees', 'country'],
          'price': ['longName', 'symbol', 'regularMarketPrice', 'quoteType', 'marketState',
                    'regularMarketChangePercent', 'regularMarketChange',
                    'postMarketChangePercent', 'postMarketChange', 'preMarketChangePercent', 'preMarketChange'],
          'topHoldings': ['holdings', 'sectorWeightings']}


def get_yahoo_cookie():
    user_agent_key = "User-Agent"
    user_agent_value = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                       "Chrome/58.0.3029.110 Safari/537.36"

    headers = {user_agent_key: user_agent_value}
    response = requests.get(
        "https://fc.yahoo.com", headers=headers, allow_redirects=True
    )

    if not response.cookies:
        raise Exception("Failed to obtain Yahoo auth cookie.")

    cookie = list(response.cookies)[0]

    return cookie


def get_yahoo_crumb(cookie):
    user_agent_key = "User-Agent"
    user_agent_value = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                       "Chrome/58.0.3029.110 Safari/537.36"

    headers = {user_agent_key: user_agent_value}

    crumb_response = requests.get(
        "https://query1.finance.yahoo.com/v1/test/getcrumb",
        headers=headers,
        cookies={cookie.name: cookie.value},
        allow_redirects=True,
    )
    crumb = crumb_response.text

    if crumb is None:
        raise Exception("Failed to retrieve Yahoo crumb.")

    return crumb


def download_advanced_stats(symbol_list, threads=True):
    """
    Downloads advanced yahoo stats for many tickers by doing one request per ticker.
    """
    num_requests = len(symbol_list)
    if threads:
        num_threads = min([num_requests, multitasking.cpu_count() * 2])
        multitasking.set_max_threads(num_threads)

    # get raw responses
    for request_idx, symbol in enumerate(symbol_list):
        if threads:
            get_ticker_stats_threaded(symbol, symbol)
        else:
            shared.response_dict[symbol] = get_ticker_stats(symbol)

    if threads:
        while len(shared.response_dict) < num_requests:
            time.sleep(0.01)

    # construct stats table from responses
    stats_table = []
    for symbol, retrieved_modules_dict in shared.response_dict.items():

        stats_list = [symbol]

        for module_name, stat_name_dict in config.items():
            retrieved_module_dict = None
            if retrieved_modules_dict is not None and module_name in retrieved_modules_dict:
                retrieved_module_dict = retrieved_modules_dict[module_name]

            if retrieved_module_dict is not None:
                for stat_name in stat_name_dict:
                    stat_val = 'N/A'
                    if stat_name in retrieved_module_dict:
                        stat = retrieved_module_dict[stat_name]
                        if isinstance(stat, dict):
                            if stat:  # only if non-empty otherwise N/A
                                stat_val = stat['fmt']
                        elif isinstance(stat, str) or isinstance(stat, numbers.Number) or isinstance(stat, list):
                            stat_val = stat
                    stats_list.append(stat_val)
            else:
                stats_list.extend(['N/A'] * len(stat_name_dict))

        stats_table.append(stats_list)

    # reset for future reuse
    shared.response_dict = {}

    columns = ['Symbol']
    for stat_name_dict in config.values():
        columns.extend(stat_name_dict)

    financial_data_df = pd.DataFrame(stats_table, columns=columns)
    financial_data_df["next_update"] = str(datetime.utcnow() + timedelta(seconds=600))
    financial_data_df.set_index('Symbol', inplace=True)
    financial_data_df = financial_data_df.to_json(orient="index").replace("\/", "/")
    financial_data_df = json.loads(financial_data_df)
    return financial_data_df


@multitasking.task
def get_ticker_stats_threaded(request_idx, symbol):
    shared.response_dict[request_idx] = get_ticker_stats(symbol)


def get_ticker_stats(symbol):
    """
    Returns advanced stats for one ticker
    """

    url = f'https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}?' \
          f'modules=summaryDetail&' \
          f'modules=defaultKeyStatistics&' \
          f'modules=summaryProfile&' \
          f'modules=price&' \
          f'modules=topHoldings'

    result = requests.get(url, headers=headers)
    json_dict = result.json()
    if "quoteSummary" not in json_dict:
        return None
    if json_dict['quoteSummary']['result'] is None:
        return None
    module_dict = json_dict['quoteSummary']['result'][0]

    return module_dict
