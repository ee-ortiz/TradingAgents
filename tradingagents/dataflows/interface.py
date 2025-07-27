from typing import Annotated, Dict
from .yfin_utils import *
from .stockstats_utils import *
from .googlenews_utils import *
from .finnhub_utils import get_data_in_range, FinnhubAPI
from dateutil.relativedelta import relativedelta
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
import os
import os
import pandas as pd
from tqdm import tqdm
import yfinance as yf
from openai import OpenAI
from .config import get_config, set_config, DATA_DIR


def get_finnhub_news(
    ticker: Annotated[
        str,
        "Search query of a company's, e.g. 'AAPL, TSM, etc.",
    ],
    curr_date: Annotated[str, "Current date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
):
    """
    Retrieve news about a company within a time frame

    Args
        ticker (str): ticker for the company you are interested in
        curr_date (str): Current date in yyyy-mm-dd format
        look_back_days (int): how many days to look back
    Returns
        str: formatted news data containing the news of the company in the time frame

    """

    start_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    # Try to get API key for real-time data
    config = get_config()
    finnhub_api_key = config.get("finnhub_api_key") or os.getenv("FINNHUB_API_KEY")
    
    if finnhub_api_key and config.get("use_finnhub_api", True):
        # Use real-time Finnhub API
        try:
            api = FinnhubAPI(finnhub_api_key)
            news_data = api.get_company_news(ticker, before, curr_date)
            
            if news_data:
                combined_result = ""
                for article in news_data:
                    date_str = datetime.fromtimestamp(article.get('datetime', 0)).strftime('%Y-%m-%d')
                    headline = article.get('headline', 'No headline')
                    summary = article.get('summary', 'No summary available')
                    
                    current_news = f"### {headline} ({date_str})\n{summary}"
                    combined_result += current_news + "\n\n"
                
                return f"## {ticker} Real-time News from {before} to {curr_date}:\n" + combined_result
        except Exception as e:
            print(f"Finnhub API error, falling back to cached data: {e}")
    
    # Fallback to cached data
    result = get_data_in_range(ticker, before, curr_date, "news_data", DATA_DIR)

    if len(result) == 0:
        return f"No news data available for {ticker} from {before} to {curr_date}"

    combined_result = ""
    for day, data in result.items():
        if len(data) == 0:
            continue
        for entry in data:
            current_news = (
                "### " + entry["headline"] + f" ({day})" + "\n" + entry["summary"]
            )
            combined_result += current_news + "\n\n"

    return f"## {ticker} Cached News from {before} to {curr_date}:\n" + str(combined_result)


def get_finnhub_company_insider_sentiment(
    ticker: Annotated[str, "ticker symbol for the company"],
    curr_date: Annotated[
        str,
        "current date of you are trading at, yyyy-mm-dd",
    ],
    look_back_days: Annotated[int, "number of days to look back"],
):
    """
    Retrieve insider sentiment about a company (retrieved from public SEC information) for the past period
    Args:
        ticker (str): ticker symbol of the company
        curr_date (str): current date you are trading on, yyyy-mm-dd
        look_back_days (int): number of days to look back
    Returns:
        str: a report of the sentiment in the specified period
    """

    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    # Try to get API key for real-time data
    config = get_config()
    finnhub_api_key = config.get("finnhub_api_key") or os.getenv("FINNHUB_API_KEY")
    
    if finnhub_api_key and config.get("use_finnhub_api", True):
        # Use real-time Finnhub API
        try:
            api = FinnhubAPI(finnhub_api_key)
            sentiment_data = api.get_insider_sentiment(ticker, before, curr_date)
            
            if sentiment_data and 'data' in sentiment_data:
                result_str = ""
                for entry in sentiment_data['data']:
                    result_str += f"### {entry.get('year', 'N/A')}-{entry.get('month', 'N/A')}:\n"
                    result_str += f"Change: {entry.get('change', 'N/A')}\n"
                    result_str += f"Monthly Share Purchase Ratio: {entry.get('mspr', 'N/A')}\n\n"
                
                return (
                    f"## {ticker} Real-time Insider Sentiment from {before} to {curr_date}:\n"
                    + result_str
                    + "The change field refers to the net buying/selling from all insiders' transactions. The mspr field refers to monthly share purchase ratio."
                )
        except Exception as e:
            print(f"Finnhub API error, falling back to cached data: {e}")

    # Fallback to cached data
    data = get_data_in_range(ticker, before, curr_date, "insider_senti", DATA_DIR)

    if len(data) == 0:
        return f"No insider sentiment data available for {ticker} from {before} to {curr_date}"

    result_str = ""
    seen_dicts = []
    for date, senti_list in data.items():
        for entry in senti_list:
            if entry not in seen_dicts:
                result_str += f"### {entry['year']}-{entry['month']}:\nChange: {entry['change']}\nMonthly Share Purchase Ratio: {entry['mspr']}\n\n"
                seen_dicts.append(entry)

    return (
        f"## {ticker} Cached Insider Sentiment from {before} to {curr_date}:\n"
        + result_str
        + "The change field refers to the net buying/selling from all insiders' transactions. The mspr field refers to monthly share purchase ratio."
    )


def get_finnhub_company_insider_transactions(
    ticker: Annotated[str, "ticker symbol"],
    curr_date: Annotated[
        str,
        "current date you are trading at, yyyy-mm-dd",
    ],
    look_back_days: Annotated[int, "how many days to look back"],
):
    """
    Retrieve insider transaction information about a company (retrieved from public SEC information)
    Args:
        ticker (str): ticker symbol of the company
        curr_date (str): current date you are trading at, yyyy-mm-dd
        look_back_days (int): how many days to look back
    Returns:
        str: a report of the company's insider transaction/trading information
    """

    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    # Try to get API key for real-time data
    config = get_config()
    finnhub_api_key = config.get("finnhub_api_key") or os.getenv("FINNHUB_API_KEY")
    
    if finnhub_api_key and config.get("use_finnhub_api", True):
        # Use real-time Finnhub API
        try:
            api = FinnhubAPI(finnhub_api_key)
            trans_data = api.get_insider_transactions(ticker, before, curr_date)
            
            if trans_data and 'data' in trans_data:
                result_str = ""
                seen_transactions = set()
                
                for entry in trans_data['data']:
                    # Create unique identifier to avoid duplicates
                    trans_id = f"{entry.get('filingDate', '')}-{entry.get('name', '')}-{entry.get('change', '')}"
                    
                    if trans_id not in seen_transactions:
                        result_str += f"### Filing Date: {entry.get('filingDate', 'N/A')}, {entry.get('name', 'N/A')}:\n"
                        result_str += f"Change: {entry.get('change', 'N/A')}\n"
                        result_str += f"Shares: {entry.get('share', 'N/A')}\n"
                        result_str += f"Transaction Price: {entry.get('transactionPrice', 'N/A')}\n"
                        result_str += f"Transaction Code: {entry.get('transactionCode', 'N/A')}\n\n"
                        seen_transactions.add(trans_id)
                
                return (
                    f"## {ticker} Real-time Insider Transactions from {before} to {curr_date}:\n"
                    + result_str
                    + "The change field reflects the variation in share count—here a negative number indicates a reduction in holdings—while share specifies the total number of shares involved. The transactionPrice denotes the per-share price at which the trade was executed, and transactionDate marks when the transaction occurred. The name field identifies the insider making the trade, and transactionCode (e.g., S for sale) clarifies the nature of the transaction. FilingDate records when the transaction was officially reported, and the unique id links to the specific SEC filing, as indicated by the source."
                )
        except Exception as e:
            print(f"Finnhub API error, falling back to cached data: {e}")

    # Fallback to cached data
    data = get_data_in_range(ticker, before, curr_date, "insider_trans", DATA_DIR)

    if len(data) == 0:
        return f"No insider transaction data available for {ticker} from {before} to {curr_date}"

    result_str = ""
    seen_dicts = []
    for date, senti_list in data.items():
        for entry in senti_list:
            if entry not in seen_dicts:
                result_str += f"### Filing Date: {entry['filingDate']}, {entry['name']}:\nChange:{entry['change']}\nShares: {entry['share']}\nTransaction Price: {entry['transactionPrice']}\nTransaction Code: {entry['transactionCode']}\n\n"
                seen_dicts.append(entry)

    return (
        f"## {ticker} Cached Insider Transactions from {before} to {curr_date}:\n"
        + result_str
        + "The change field reflects the variation in share count—here a negative number indicates a reduction in holdings—while share specifies the total number of shares involved. The transactionPrice denotes the per-share price at which the trade was executed, and transactionDate marks when the transaction occurred. The name field identifies the insider making the trade, and transactionCode (e.g., S for sale) clarifies the nature of the transaction. FilingDate records when the transaction was officially reported, and the unique id links to the specific SEC filing, as indicated by the source. Additionally, the symbol ties the transaction to a particular company, isDerivative flags whether the trade involves derivative securities, and currency notes the currency context of the transaction."
    )


def get_finnhub_company_profile(
    ticker: Annotated[str, "ticker symbol"],
):
    """
    Retrieve company profile information from Finnhub API
    Args:
        ticker (str): ticker symbol of the company
    Returns:
        str: company profile information including industry, description, market cap, etc.
    """
    
    # Try to get API key for real-time data
    config = get_config()
    finnhub_api_key = config.get("finnhub_api_key") or os.getenv("FINNHUB_API_KEY")
    
    if finnhub_api_key and config.get("use_finnhub_api", True):
        try:
            api = FinnhubAPI(finnhub_api_key)
            profile_data = api.get_company_profile(ticker)
            
            if profile_data:
                result = f"## {ticker} Company Profile:\n\n"
                result += f"**Company Name**: {profile_data.get('name', 'N/A')}\n"
                result += f"**Industry**: {profile_data.get('finnhubIndustry', 'N/A')}\n"
                result += f"**Market Cap**: ${profile_data.get('marketCapitalization', 'N/A')}M\n"
                result += f"**Country**: {profile_data.get('country', 'N/A')}\n"
                result += f"**Currency**: {profile_data.get('currency', 'N/A')}\n"
                result += f"**Exchange**: {profile_data.get('exchange', 'N/A')}\n"
                result += f"**IPO Date**: {profile_data.get('ipo', 'N/A')}\n"
                result += f"**Outstanding Shares**: {profile_data.get('shareOutstanding', 'N/A')}M\n"
                result += f"**Website**: {profile_data.get('weburl', 'N/A')}\n\n"
                
                # Company description if available
                if 'description' in profile_data:
                    result += f"**Description**: {profile_data['description'][:500]}{'...' if len(profile_data['description']) > 500 else ''}\n"
                
                return result
        except Exception as e:
            print(f"Finnhub API error for company profile: {e}")
    
    return f"Company profile data not available for {ticker}"


def get_finnhub_basic_financials(
    ticker: Annotated[str, "ticker symbol"],
):
    """
    Retrieve basic financial metrics from Finnhub API
    Args:
        ticker (str): ticker symbol of the company
    Returns:
        str: basic financial metrics including P/E ratio, ROE, debt/equity, etc.
    """
    
    # Try to get API key for real-time data
    config = get_config()
    finnhub_api_key = config.get("finnhub_api_key") or os.getenv("FINNHUB_API_KEY")
    
    if finnhub_api_key and config.get("use_finnhub_api", True):
        try:
            api = FinnhubAPI(finnhub_api_key)
            financials_data = api.get_basic_financials(ticker)
            
            if financials_data and 'metric' in financials_data:
                metrics = financials_data['metric']
                result = f"## {ticker} Basic Financial Metrics:\n\n"
                
                # Key valuation metrics
                result += "### Valuation Metrics\n"
                result += f"**P/E Ratio (TTM)**: {metrics.get('peBasicExclExtraTTM', 'N/A')}\n"
                result += f"**P/B Ratio (TTM)**: {metrics.get('pbAnnual', 'N/A')}\n"
                result += f"**P/S Ratio (TTM)**: {metrics.get('psAnnual', 'N/A')}\n"
                result += f"**EV/EBITDA (TTM)**: {metrics.get('evEbitdaTTM', 'N/A')}\n\n"
                
                # Profitability metrics
                result += "### Profitability Metrics\n"
                result += f"**ROE (TTM)**: {metrics.get('roeTTM', 'N/A')}%\n"
                result += f"**ROA (TTM)**: {metrics.get('roaTTM', 'N/A')}%\n"
                result += f"**ROI (TTM)**: {metrics.get('roiTTM', 'N/A')}%\n"
                result += f"**Gross Margin (TTM)**: {metrics.get('grossMarginTTM', 'N/A')}%\n"
                result += f"**Operating Margin (TTM)**: {metrics.get('operatingMarginTTM', 'N/A')}%\n"
                result += f"**Net Profit Margin (TTM)**: {metrics.get('netProfitMarginTTM', 'N/A')}%\n\n"
                
                # Financial health
                result += "### Financial Health\n"
                result += f"**Current Ratio (Annual)**: {metrics.get('currentRatioAnnual', 'N/A')}\n"
                result += f"**Quick Ratio (Annual)**: {metrics.get('quickRatioAnnual', 'N/A')}\n"
                result += f"**Debt/Equity (Annual)**: {metrics.get('totalDebtToEquityAnnual', 'N/A')}\n"
                result += f"**Long-term Debt/Capital (Annual)**: {metrics.get('longTermDebtCapitalAnnual', 'N/A')}\n\n"
                
                # Growth metrics
                result += "### Growth Metrics\n"
                result += f"**Revenue Growth (TTM YoY)**: {metrics.get('revenueGrowthTTMYoy', 'N/A')}%\n"
                result += f"**EPS Growth (TTM YoY)**: {metrics.get('epsGrowthTTMYoy', 'N/A')}%\n"
                
                return result
        except Exception as e:
            print(f"Finnhub API error for basic financials: {e}")
    
    return f"Basic financial metrics not available for {ticker}"


def get_google_news(
    query: Annotated[str, "Query to search with"],
    curr_date: Annotated[str, "Curr date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:
    query = query.replace(" ", "+")

    start_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = start_date - relativedelta(days=look_back_days)
    before = before.strftime("%Y-%m-%d")

    news_results = getNewsData(query, before, curr_date)

    news_str = ""

    for news in news_results:
        news_str += (
            f"### {news['title']} (source: {news['source']}) \n\n{news['snippet']}\n\n"
        )

    if len(news_results) == 0:
        return ""

    return f"## {query} Google News, from {before} to {curr_date}:\n\n{news_str}"


def get_stock_stats_indicators_window(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        str, "The current trading date you are trading on, YYYY-mm-dd"
    ],
    look_back_days: Annotated[int, "how many days to look back"],
    online: Annotated[bool, "to fetch data online or offline"],
) -> str:

    best_ind_params = {
        # Moving Averages
        "close_50_sma": (
            "50 SMA: A medium-term trend indicator. "
            "Usage: Identify trend direction and serve as dynamic support/resistance. "
            "Tips: It lags price; combine with faster indicators for timely signals."
        ),
        "close_200_sma": (
            "200 SMA: A long-term trend benchmark. "
            "Usage: Confirm overall market trend and identify golden/death cross setups. "
            "Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries."
        ),
        "close_10_ema": (
            "10 EMA: A responsive short-term average. "
            "Usage: Capture quick shifts in momentum and potential entry points. "
            "Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals."
        ),
        # MACD Related
        "macd": (
            "MACD: Computes momentum via differences of EMAs. "
            "Usage: Look for crossovers and divergence as signals of trend changes. "
            "Tips: Confirm with other indicators in low-volatility or sideways markets."
        ),
        "macds": (
            "MACD Signal: An EMA smoothing of the MACD line. "
            "Usage: Use crossovers with the MACD line to trigger trades. "
            "Tips: Should be part of a broader strategy to avoid false positives."
        ),
        "macdh": (
            "MACD Histogram: Shows the gap between the MACD line and its signal. "
            "Usage: Visualize momentum strength and spot divergence early. "
            "Tips: Can be volatile; complement with additional filters in fast-moving markets."
        ),
        # Momentum Indicators
        "rsi": (
            "RSI: Measures momentum to flag overbought/oversold conditions. "
            "Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. "
            "Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis."
        ),
        # Volatility Indicators
        "boll": (
            "Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. "
            "Usage: Acts as a dynamic benchmark for price movement. "
            "Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals."
        ),
        "boll_ub": (
            "Bollinger Upper Band: Typically 2 standard deviations above the middle line. "
            "Usage: Signals potential overbought conditions and breakout zones. "
            "Tips: Confirm signals with other tools; prices may ride the band in strong trends."
        ),
        "boll_lb": (
            "Bollinger Lower Band: Typically 2 standard deviations below the middle line. "
            "Usage: Indicates potential oversold conditions. "
            "Tips: Use additional analysis to avoid false reversal signals."
        ),
        "atr": (
            "ATR: Averages true range to measure volatility. "
            "Usage: Set stop-loss levels and adjust position sizes based on current market volatility. "
            "Tips: It's a reactive measure, so use it as part of a broader risk management strategy."
        ),
        # Volume-Based Indicators
        "vwma": (
            "VWMA: A moving average weighted by volume. "
            "Usage: Confirm trends by integrating price action with volume data. "
            "Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses."
        ),
        "mfi": (
            "MFI: The Money Flow Index is a momentum indicator that uses both price and volume to measure buying and selling pressure. "
            "Usage: Identify overbought (>80) or oversold (<20) conditions and confirm the strength of trends or reversals. "
            "Tips: Use alongside RSI or MACD to confirm signals; divergence between price and MFI can indicate potential reversals."
        ),
    }

    if indicator not in best_ind_params:
        raise ValueError(
            f"Indicator {indicator} is not supported. Please choose from: {list(best_ind_params.keys())}"
        )

    end_date = curr_date
    curr_date = datetime.strptime(curr_date, "%Y-%m-%d")
    before = curr_date - relativedelta(days=look_back_days)

    if not online:
        # read from YFin data
        data = pd.read_csv(
            os.path.join(
                DATA_DIR,
                f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
            )
        )
        data["Date"] = pd.to_datetime(data["Date"], utc=True)
        dates_in_df = data["Date"].astype(str).str[:10]

        ind_string = ""
        while curr_date >= before:
            # only do the trading dates
            if curr_date.strftime("%Y-%m-%d") in dates_in_df.values:
                indicator_value = get_stockstats_indicator(
                    symbol, indicator, curr_date.strftime("%Y-%m-%d"), online
                )

                ind_string += f"{curr_date.strftime('%Y-%m-%d')}: {indicator_value}\n"

            curr_date = curr_date - relativedelta(days=1)
    else:
        # online gathering
        ind_string = ""
        while curr_date >= before:
            indicator_value = get_stockstats_indicator(
                symbol, indicator, curr_date.strftime("%Y-%m-%d"), online
            )

            ind_string += f"{curr_date.strftime('%Y-%m-%d')}: {indicator_value}\n"

            curr_date = curr_date - relativedelta(days=1)

    result_str = (
        f"## {indicator} values from {before.strftime('%Y-%m-%d')} to {end_date}:\n\n"
        + ind_string
        + "\n\n"
        + best_ind_params.get(indicator, "No description available.")
    )

    return result_str


def get_stockstats_indicator(
    symbol: Annotated[str, "ticker symbol of the company"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        str, "The current trading date you are trading on, YYYY-mm-dd"
    ],
    online: Annotated[bool, "to fetch data online or offline"],
) -> str:

    curr_date = datetime.strptime(curr_date, "%Y-%m-%d")
    curr_date = curr_date.strftime("%Y-%m-%d")

    try:
        indicator_value = StockstatsUtils.get_stock_stats(
            symbol,
            indicator,
            curr_date,
            os.path.join(DATA_DIR, "market_data", "price_data"),
            online=online,
        )
    except Exception as e:
        print(
            f"Error getting stockstats indicator data for indicator {indicator} on {curr_date}: {e}"
        )
        return ""

    return str(indicator_value)


def get_YFin_data_window(
    symbol: Annotated[str, "ticker symbol of the company"],
    curr_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:
    # calculate past days
    date_obj = datetime.strptime(curr_date, "%Y-%m-%d")
    before = date_obj - relativedelta(days=look_back_days)
    start_date = before.strftime("%Y-%m-%d")

    # read in data
    data = pd.read_csv(
        os.path.join(
            DATA_DIR,
            f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
        )
    )

    # Extract just the date part for comparison
    data["DateOnly"] = data["Date"].str[:10]

    # Filter data between the start and end dates (inclusive)
    filtered_data = data[
        (data["DateOnly"] >= start_date) & (data["DateOnly"] <= curr_date)
    ]

    # Drop the temporary column we created
    filtered_data = filtered_data.drop("DateOnly", axis=1)

    # Set pandas display options to show the full DataFrame
    with pd.option_context(
        "display.max_rows", None, "display.max_columns", None, "display.width", None
    ):
        df_string = filtered_data.to_string()

    return (
        f"## Raw Market Data for {symbol} from {start_date} to {curr_date}:\n\n"
        + df_string
    )


def get_YFin_data_online(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
):

    datetime.strptime(start_date, "%Y-%m-%d")
    datetime.strptime(end_date, "%Y-%m-%d")

    # Create ticker object
    ticker = yf.Ticker(symbol.upper())

    # Fetch historical data for the specified date range
    data = ticker.history(start=start_date, end=end_date)

    # Check if data is empty
    if data.empty:
        return (
            f"No data found for symbol '{symbol}' between {start_date} and {end_date}"
        )

    # Remove timezone info from index for cleaner output
    if data.index.tz is not None:
        data.index = data.index.tz_localize(None)

    # Round numerical values to 2 decimal places for cleaner display
    numeric_columns = ["Open", "High", "Low", "Close", "Adj Close"]
    for col in numeric_columns:
        if col in data.columns:
            data[col] = data[col].round(2)

    # Convert DataFrame to CSV string
    csv_string = data.to_csv()

    # Add header information
    header = f"# Stock data for {symbol.upper()} from {start_date} to {end_date}\n"
    header += f"# Total records: {len(data)}\n"
    header += f"# Data retrieved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

    return header + csv_string


def get_YFin_data(
    symbol: Annotated[str, "ticker symbol of the company"],
    start_date: Annotated[str, "Start date in yyyy-mm-dd format"],
    end_date: Annotated[str, "End date in yyyy-mm-dd format"],
) -> str:
    # read in data
    data = pd.read_csv(
        os.path.join(
            DATA_DIR,
            f"market_data/price_data/{symbol}-YFin-data-2015-01-01-2025-03-25.csv",
        )
    )

    if end_date > "2025-03-25":
        raise Exception(
            f"Get_YFin_Data: {end_date} is outside of the data range of 2015-01-01 to 2025-03-25"
        )

    # Extract just the date part for comparison
    data["DateOnly"] = data["Date"].str[:10]

    # Filter data between the start and end dates (inclusive)
    filtered_data = data[
        (data["DateOnly"] >= start_date) & (data["DateOnly"] <= end_date)
    ]

    # Drop the temporary column we created
    filtered_data = filtered_data.drop("DateOnly", axis=1)

    # remove the index from the dataframe
    filtered_data = filtered_data.reset_index(drop=True)

    return filtered_data


def get_stock_news_openai(ticker, curr_date):
    """
    Get stock news and social media analysis using OpenRouter with web search capabilities.
    
    Args:
        ticker (str): Stock ticker symbol
        curr_date (str): Current date in YYYY-MM-DD format
        
    Returns:
        str: Real-time analysis of stock news and social media sentiment
    """
    config = get_config()
    client = OpenAI(
        base_url=config["backend_url"],
        api_key=os.getenv("OPENROUTER_API_KEY"),
        default_headers={
            "HTTP-Referer": config.get("openrouter_site_url", ""),
            "X-Title": config.get("openrouter_site_name", ""),
        }
    )

    try:
        # Use web search enabled model if configured
        model = config["quick_think_llm"]
        
        # Add :online suffix for web search only if use_web_search is enabled
        if config.get("use_web_search", False):
            if ":online" not in model and not model.startswith("perplexity/"):
                model = f"{model}:online"
        
        # Adjust system prompt based on web search availability
        if config.get("use_web_search", False):
            system_content = f"You are a financial analyst with access to real-time web search. Analyze current social media sentiment and recent news for {ticker} around {curr_date}. Use web search to find the most recent and relevant information."
        else:
            system_content = f"You are a financial analyst. Analyze social media sentiment and news patterns for {ticker} based on your training data. Provide analysis based on typical market patterns and known company information."
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_content
                },
                {
                    "role": "user", 
                    "content": f"{'Search for and ' if config.get('use_web_search', False) else ''}Analyze the latest news, social media sentiment, and market discussions about {ticker} stock around {curr_date}. Include key sentiment indicators, major news events, analyst opinions, and their potential impact on stock price. Focus on information from the last 7 days."
                }
            ],
            temperature=0.7,
            max_tokens=2048,
        )
        
        # Add prefix to indicate data source type
        data_source = "[REAL-TIME WEB SEARCH DATA]" if config.get("use_web_search", False) else "[SYNTHETIC ANALYSIS]"
        return f"{data_source}\n\n{response.choices[0].message.content}"
        
    except Exception as e:
        print(f"Error getting stock news via OpenRouter: {e}")
        return f"Unable to retrieve stock news for {ticker} due to API error."


def get_global_news_openai(curr_date):
    """
    Get global news and macroeconomic analysis using OpenRouter with web search capabilities.
    
    Args:
        curr_date (str): Current date in YYYY-MM-DD format
        
    Returns:
        str: Real-time analysis of global news and macroeconomic trends
    """
    config = get_config()
    client = OpenAI(
        base_url=config["backend_url"],
        api_key=os.getenv("OPENROUTER_API_KEY"),
        default_headers={
            "HTTP-Referer": config.get("openrouter_site_url", ""),
            "X-Title": config.get("openrouter_site_name", ""),
        }
    )

    try:
        # Use web search enabled model if configured
        model = config["quick_think_llm"]
        
        # Add :online suffix for web search only if use_web_search is enabled
        if config.get("use_web_search", False):
            if ":online" not in model and not model.startswith("perplexity/"):
                model = f"{model}:online"
        
        # Adjust system prompt based on web search availability
        if config.get("use_web_search", False):
            system_content = f"You are a macroeconomic analyst with access to real-time web search. Analyze current global news and macroeconomic trends around {curr_date} that would be relevant for trading decisions. Use web search to find the most recent and relevant information."
        else:
            system_content = f"You are a macroeconomic analyst. Analyze global news patterns and macroeconomic trends based on your training data. Provide analysis based on typical economic patterns and known market factors relevant around {curr_date}."
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_content
                },
                {
                    "role": "user",
                    "content": f"{'Search for and ' if config.get('use_web_search', False) else ''}Analyze the latest global news, economic indicators, central bank policies, geopolitical developments, and market-moving events around {curr_date}. Focus on information from the last 7 days that could impact financial markets. Include specific data points, policy changes, and expert opinions."
                }
            ],
            temperature=0.7,
            max_tokens=2048,
        )
        
        # Add prefix to indicate data source type
        data_source = "[REAL-TIME WEB SEARCH DATA]" if config.get("use_web_search", False) else "[SYNTHETIC ANALYSIS]"
        return f"{data_source}\n\n{response.choices[0].message.content}"
        
    except Exception as e:
        print(f"Error getting global news via OpenRouter: {e}")
        return f"Unable to retrieve global news due to API error."


def get_fundamentals_openai(ticker, curr_date):
    """
    Get fundamental analysis using OpenRouter with web search capabilities.
    
    Args:
        ticker (str): Stock ticker symbol
        curr_date (str): Current date in YYYY-MM-DD format
        
    Returns:
        str: Real-time fundamental analysis report with current financial data
    """
    config = get_config()
    client = OpenAI(
        base_url=config["backend_url"],
        api_key=os.getenv("OPENROUTER_API_KEY"),
        default_headers={
            "HTTP-Referer": config.get("openrouter_site_url", ""),
            "X-Title": config.get("openrouter_site_name", ""),
        }
    )

    try:
        # Use web search enabled model if configured
        model = config["quick_think_llm"]
        
        # Add :online suffix for web search only if use_web_search is enabled
        if config.get("use_web_search", False):
            if ":online" not in model and not model.startswith("perplexity/"):
                model = f"{model}:online"
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": f"You are a fundamental analyst{'with access to real-time web search' if config.get('use_web_search', False) else ''}. Analyze the {'current ' if config.get('use_web_search', False) else ''}fundamental situation of {ticker} around {curr_date}. {'Use web search to find the most recent financial data, earnings reports, and analyst opinions.' if config.get('use_web_search', False) else 'Provide analysis based on typical fundamental patterns and known company characteristics.'}"
                },
                {
                    "role": "user",
                    "content": f"{'Search for and ' if config.get('use_web_search', False) else ''}Analyze the latest fundamental data for {ticker} stock around {curr_date}. Include recent earnings reports, financial metrics (P/E, P/S, P/B ratios, cash flow, debt levels, revenue growth, profit margins), analyst price targets, credit ratings, and any recent fundamental changes. Focus on the most current financial information available. Present key metrics in table format when possible."
                }
            ],
            temperature=0.7,
            max_tokens=2048,
        )
        
        # Add prefix to indicate data source type
        data_source = "[REAL-TIME WEB SEARCH DATA]" if config.get("use_web_search", False) else "[SYNTHETIC ANALYSIS]"
        return f"{data_source}\n\n{response.choices[0].message.content}"
        
    except Exception as e:
        print(f"Error getting fundamentals via OpenRouter: {e}")
        return f"Unable to retrieve real-time fundamental analysis for {ticker} due to API error."
