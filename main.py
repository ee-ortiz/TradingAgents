# TradingAgents with OpenRouter Web Search - Usage Examples
import os
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if exists
if Path(".env").exists():
    load_dotenv()

# ====================================================================
# CONFIGURATION EXAMPLES - Choose based on your needs and budget
# ====================================================================

# OPTION 1: BUDGET SETUP (Most Cost-Effective)
# Free models + web search + free tier Finnhub for essential data
# Cost: ~$0.06 per analysis (3 web searches × $0.02)
config_budget = DEFAULT_CONFIG.copy()
config_budget.update({
    "use_web_search": True,           # Enable real-time data access
    "use_finnhub_api": True,          # Free tier Finnhub for structured data
    "max_debate_rounds": 1,           # Limit rounds to control cost
})

# OPTION 2: BALANCED SETUP (Recommended)
# Free reasoning model + premium quick model with hybrid data sources
# Cost: ~$0.15 per analysis
config_balanced = DEFAULT_CONFIG.copy()
config_balanced.update({
    "quick_think_llm": "openai/gpt-4o-mini",  # Will auto-add :online when needed
    "use_web_search": True,           # OpenRouter web search for context
    "use_finnhub_api": True,          # Finnhub for structured financial data
    "max_debate_rounds": 2,
})

# OPTION 3: PREMIUM SETUP (Maximum Quality)
# Premium models with comprehensive hybrid data sources
# Cost: ~$0.50+ per analysis
config_premium = DEFAULT_CONFIG.copy()
config_premium.update({
    "deep_think_llm": "openai/gpt-4o",
    "quick_think_llm": "openai/gpt-4o",
    "use_web_search": True,           # Comprehensive web search
    "use_finnhub_api": True,          # Real-time structured financial data
    "max_debate_rounds": 3,
})

# OPTION 4: HYBRID DATA FOCUS
# Use both OpenRouter web search and Finnhub for maximum data coverage
# Cost: ~$0.20 per analysis
config_hybrid = DEFAULT_CONFIG.copy()
config_hybrid.update({
    "quick_think_llm": "perplexity/llama-3.1-sonar-small-128k-online",
    "use_web_search": True,           # Real-time web context
    "use_finnhub_api": True,          # Structured financial data
    "max_debate_rounds": 2,
})

# ====================================================================
# DEMONSTRATING HYBRID DATA SOURCE BEHAVIOR
# ====================================================================

# Example 1: Full hybrid data approach
config_hybrid_full = DEFAULT_CONFIG.copy()
config_hybrid_full["use_web_search"] = True
config_hybrid_full["use_finnhub_api"] = True
print("CONFIG 1 - Hybrid Data (OpenRouter + Finnhub):")
print(f"  use_web_search: {config_hybrid_full['use_web_search']}")
print(f"  use_finnhub_api: {config_hybrid_full['use_finnhub_api']}")
print(f"  Model used: {config_hybrid_full['quick_think_llm']} → {config_hybrid_full['quick_think_llm']}:online")
print("  Data sources: OpenRouter web search + Finnhub structured data + Yahoo Finance")
print("  Cost: Model fee + $0.02 per search + Finnhub free tier")
print()

# Example 2: OpenRouter only
config_openrouter_only = DEFAULT_CONFIG.copy()
config_openrouter_only["use_web_search"] = True
config_openrouter_only["use_finnhub_api"] = False
print("CONFIG 2 - OpenRouter Web Search Only:")
print(f"  use_web_search: {config_openrouter_only['use_web_search']}")
print(f"  use_finnhub_api: {config_openrouter_only['use_finnhub_api']}")
print(f"  Model used: {config_openrouter_only['quick_think_llm']} → {config_openrouter_only['quick_think_llm']}:online")
print("  Data sources: OpenRouter web search + Yahoo Finance")
print("  Cost: Model fee + $0.02 per search")
print()

# Example 3: Synthetic analysis (no real-time APIs)
config_synthetic = DEFAULT_CONFIG.copy()
config_synthetic["use_web_search"] = False
config_synthetic["use_finnhub_api"] = False
print("CONFIG 3 - Synthetic Analysis (No Real-time APIs):")
print(f"  use_web_search: {config_synthetic['use_web_search']}")
print(f"  use_finnhub_api: {config_synthetic['use_finnhub_api']}")
print(f"  Model used: {config_synthetic['quick_think_llm']} (no :online suffix)")
print("  Data sources: Pre-trained knowledge + Yahoo Finance + cached data")
print("  Cost: Only model fee (DeepSeek = free)")
print()

# ====================================================================
# CHOOSE YOUR CONFIGURATION
# ====================================================================

# Select configuration based on your needs:
config = config_hybrid_full  # ← Change this to any config above

print("Running TradingAgents with Hybrid Configuration:")
print(f"  Deep Think LLM: {config['deep_think_llm']}")
print(f"  Quick Think LLM: {config['quick_think_llm']}")
print(f"  OpenRouter Web Search: {'Enabled' if config.get('use_web_search') else 'Disabled'}")
print(f"  Finnhub API: {'Enabled' if config.get('use_finnhub_api') else 'Disabled'}")
print(f"  Max Debate Rounds: {config.get('max_debate_rounds', 2)}")

data_sources = []
if config.get('use_web_search'): data_sources.append("OpenRouter Web Search")
if config.get('use_finnhub_api'): data_sources.append("Finnhub Structured Data")
data_sources.append("Yahoo Finance")

print(f"  Data Sources: {', '.join(data_sources)}")
print()

# Initialize TradingAgents with OpenRouter
ta = TradingAgentsGraph(debug=True, config=config)

# Run analysis
symbol = "NVDA"
date = "2025-07-24"

print(f"Analyzing {symbol} with hybrid data sources...")
_, decision = ta.propagate(symbol, date)

print(f"\nTrading Decision: {decision}")

# Show PDF generation status
pdf_dir = f"./results/{symbol}/{date}/reports_pdf"
if os.path.exists(pdf_dir):
    print("\nPDF Reports Generated:")
    print(f"   Directory: {pdf_dir}")
    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
    for pdf_file in pdf_files:
        print(f"   {pdf_file}")
else:
    print(f"\nNo PDF reports generated. Check your configuration or run settings.")

# Optional: Reflect and learn from trading results
# ta.reflect_and_remember(1000)  # Position returns for learning
