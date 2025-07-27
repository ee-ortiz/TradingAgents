import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if exists
if Path(".env").exists():
    load_dotenv()

DEFAULT_CONFIG = {
    # ─────────── Paths ───────────
    "project_dir": os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
    "results_dir": os.getenv("TRADINGAGENTS_RESULTS_DIR", "./results"),
    "data_dir": os.getenv("TRADINGAGENTS_DATA_DIR", "./data"),
    "data_cache_dir": os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), ".")),
        "dataflows/data_cache",
    ),

    # ─────────── LLM (OpenRouter) ───────────
    "backend_url": "https://openrouter.ai/api/v1",
    "deep_think_llm": "deepseek/deepseek-r1-0528:free",
    "quick_think_llm": "deepseek/deepseek-chat-v3-0324:free",
    # Optional site tracking for OpenRouter analytics
    "openrouter_site_url": "https://github.com/ee-ortiz/TradingAgents",
    "openrouter_site_name": "TradingAgents",

    # ─────────── Debate parameters ───────────
    "max_debate_rounds": 1,        # Bull/Bear research debate rounds
    "max_risk_discuss_rounds": 1,  # Risk management debate rounds
    "max_recur_limit": 100,        # LangGraph recursion limit

    # ─────────── Data Source Controls ───────────
    "online_tools": True,        # True: Yahoo Finance API, False: local CSV files
    "use_web_search": True,      # True: LLM web search, False: pre-trained knowledge only
    "use_finnhub_api": True,     # True: Real-time Finnhub API, False: cached data only
    "finnhub_api_key": os.getenv("FINNHUB_API_KEY"),  # Finnhub API key for real-time data
}
