import json
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time


class FinnhubAPI:
    """Finnhub API client for real-time financial data."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://finnhub.io/api/v1"
        self.headers = {"X-Finnhub-Token": api_key}
        
    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make API request to Finnhub."""
        try:
            url = f"{self.base_url}/{endpoint}"
            response = requests.get(url, headers=self.headers, params=params or {})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Finnhub API error: {e}")
            return {}
    
    def get_company_news(self, symbol: str, start_date: str, end_date: str) -> List[Dict]:
        """Get company news from Finnhub API."""
        # Convert dates to timestamps
        start_ts = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp())
        end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp())
        
        params = {
            "symbol": symbol.upper(),
            "from": start_ts,
            "to": end_ts
        }
        
        result = self._make_request("company-news", params)
        return result if isinstance(result, list) else []
    
    def get_insider_sentiment(self, symbol: str, start_date: str, end_date: str) -> Dict:
        """Get insider sentiment from Finnhub API."""
        params = {
            "symbol": symbol.upper(),
            "from": start_date,
            "to": end_date
        }
        
        return self._make_request("stock/insider-sentiment", params)
    
    def get_insider_transactions(self, symbol: str, start_date: str, end_date: str) -> Dict:
        """Get insider transactions from Finnhub API."""
        params = {
            "symbol": symbol.upper(),
            "from": start_date,
            "to": end_date
        }
        
        return self._make_request("stock/insider-transactions", params)
    
    def get_company_profile(self, symbol: str) -> Dict:
        """Get company profile from Finnhub API."""
        params = {"symbol": symbol.upper()}
        return self._make_request("stock/profile2", params)
    
    def get_basic_financials(self, symbol: str, metric: str = "all") -> Dict:
        """Get basic financials from Finnhub API."""
        params = {
            "symbol": symbol.upper(),
            "metric": metric
        }
        return self._make_request("stock/metric", params)


def get_data_in_range(ticker, start_date, end_date, data_type, data_dir, period=None):
    """
    Gets finnhub data saved and processed on disk.
    Args:
        start_date (str): Start date in YYYY-MM-DD format.
        end_date (str): End date in YYYY-MM-DD format.
        data_type (str): Type of data from finnhub to fetch. Can be insider_trans, SEC_filings, news_data, insider_senti, or fin_as_reported.
        data_dir (str): Directory where the data is saved.
        period (str): Default to none, if there is a period specified, should be annual or quarterly.
    """

    if period:
        data_path = os.path.join(
            data_dir,
            "finnhub_data",
            data_type,
            f"{ticker}_{period}_data_formatted.json",
        )
    else:
        data_path = os.path.join(
            data_dir, "finnhub_data", data_type, f"{ticker}_data_formatted.json"
        )

    # If file doesn't exist, return empty dict (will trigger API call)
    if not os.path.exists(data_path):
        return {}

    try:
        with open(data_path, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

    # filter keys (date, str in format YYYY-MM-DD) by the date range (str, str in format YYYY-MM-DD)
    filtered_data = {}
    for key, value in data.items():
        if start_date <= key <= end_date and len(value) > 0:
            filtered_data[key] = value
    return filtered_data
