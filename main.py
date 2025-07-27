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
# Free models + web search only for critical data
# Cost: ~$0.06 per analysis (3 web searches × $0.02)
config_budget = DEFAULT_CONFIG.copy()
config_budget.update({
    "use_web_search": True,           # Enable real-time data access
    "max_debate_rounds": 1,           # Limit rounds to control cost
})

# OPTION 2: BALANCED SETUP (Recommended)
# Free reasoning model + premium quick model with web search
# Cost: ~$0.15 per analysis
config_balanced = DEFAULT_CONFIG.copy()
config_balanced.update({
    "quick_think_llm": "openai/gpt-4o-mini",  # Will auto-add :online when needed
    "use_web_search": True,
    "max_debate_rounds": 2,
})

# OPTION 3: PREMIUM SETUP (Maximum Quality)
# Premium models with comprehensive web search
# Cost: ~$0.50+ per analysis
config_premium = DEFAULT_CONFIG.copy()
config_premium.update({
    "deep_think_llm": "openai/gpt-4o",
    "quick_think_llm": "openai/gpt-4o",
    "use_web_search": True,
    "max_debate_rounds": 3,
})

# OPTION 4: PERPLEXITY ALTERNATIVE
# Use Perplexity models for cost-effective web search
# Cost: ~$0.20 per analysis
config_perplexity = DEFAULT_CONFIG.copy()
config_perplexity.update({
    "quick_think_llm": "perplexity/llama-3.1-sonar-small-128k-online",
    "use_web_search": True,
})

# ====================================================================
# DEMONSTRATING use_web_search FLAG BEHAVIOR
# ====================================================================

# Example 1: Real-time data with web search
config_realtime = DEFAULT_CONFIG.copy()
config_realtime["use_web_search"] = True
print("CONFIG 1 - Real-time Data:")
print(f"  use_web_search: {config_realtime['use_web_search']}")
print(f"  Model used: {config_realtime['quick_think_llm']} → {config_realtime['quick_think_llm']}:online")
print("  Data source: Real-time web search")
print("  Cost: Model fee + $0.02 per search")
print()

# Example 2: Synthetic analysis without web search
config_synthetic = DEFAULT_CONFIG.copy()
config_synthetic["use_web_search"] = False
print("CONFIG 2 - Synthetic Analysis:")
print(f"  use_web_search: {config_synthetic['use_web_search']}")
print(f"  Model used: {config_synthetic['quick_think_llm']} (no :online suffix)")
print("  Data source: Pre-trained knowledge")
print("  Cost: Only model fee (DeepSeek = free)")
print()

# ====================================================================
# CHOOSE YOUR CONFIGURATION
# ====================================================================

# Select configuration based on your needs:
config = config_realtime  # ← Change this to config_synthetic for no web search

# Optional: Add site tracking (for OpenRouter analytics)
config["openrouter_site_url"] = "https://your-site.com"
config["openrouter_site_name"] = "TradingAgents"

print("Running TradingAgents with configuration:")
print(f"  Deep Think LLM: {config['deep_think_llm']}")
print(f"  Quick Think LLM: {config['quick_think_llm']}")
print(f"  Web Search: {'Enabled (real-time data)' if config.get('use_web_search') else 'Disabled (synthetic analysis)'}")
print(f"  Max Debate Rounds: {config.get('max_debate_rounds', 2)}")
print()

# Initialize TradingAgents with OpenRouter
ta = TradingAgentsGraph(debug=True, config=config)

# Run analysis
symbol = "NVDA"
date = "2025-07-24"

data_type = "REAL-TIME" if config.get("use_web_search") else "SYNTHETIC"
print(f"Analyzing {symbol} with {data_type} data...")
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
    print(f"\nPDF reports will be generated in: {pdf_dir}")
    print("Install PDF support for professional reports:")
    print("   pip install pdfkit markdown2")

# Optional: Reflect and learn from trading results
# ta.reflect_and_remember(1000)  # Position returns for learning
