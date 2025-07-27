"""
TradingAgents: Multi-Agent LLM Financial Trading Framework

A comprehensive multi-agent trading framework powered by OpenRouter API
with real-time web search capabilities for financial analysis.
"""

__version__ = "1.0.0"
__author__ = "TradingAgents Team"

from .default_config import DEFAULT_CONFIG
from .graph.trading_graph import TradingAgentsGraph

__all__ = [
    "DEFAULT_CONFIG",
    "TradingAgentsGraph",
]
