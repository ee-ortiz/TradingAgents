# TradingAgents: Multi-Agent LLM Financial Trading Framework

## Framework Overview

TradingAgents is a multi-agent trading framework that mirrors the dynamics of real-world trading firms. By deploying specialized LLM-powered agents—from fundamental analysts, sentiment experts, and technical analysts, to trader and risk management teams—the platform collaboratively evaluates market conditions and informs trading decisions through dynamic discussions.

This version has been optimized to work exclusively with **OpenRouter**, providing access to multiple state-of-the-art language models through a single, unified API **with native web search capabilities** for real-time financial data.

<p align="center">
  <img src="assets/schema.png" style="width: 100%; height: auto;">
</p>

### Multi-Agent Architecture

The framework decomposes complex trading tasks into specialized roles:

#### **Analyst Team**
- **Fundamentals Analyst**: Evaluates company financials and performance metrics **with real-time data**
- **Sentiment Analyst**: Analyzes social media and public sentiment **from current sources**
- **News Analyst**: Monitors global news and macroeconomic indicators **in real-time**
- **Technical Analyst**: Utilizes technical indicators (MACD, RSI, etc.) with live market data

<p align="center">
  <img src="assets/analyst.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

#### **Researcher Team**
- **Bull/Bear Researchers**: Critically assess insights through structured debates
- **Research Manager**: Synthesizes research and makes investment recommendations

<p align="center">
  <img src="assets/researcher.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

#### **Trading Team**
- **Trader Agent**: Makes informed trading decisions based on comprehensive analysis

<p align="center">
  <img src="assets/trader.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

#### **Risk Management Team**
- **Risk Analysts**: Evaluate portfolio risk from multiple perspectives
- **Portfolio Manager**: Final decision approval/rejection

<p align="center">
  <img src="assets/risk.png" width="70%" style="display: inline-block; margin: 0 2%;">
</p>

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ee-ortiz/TradingAgents.git
cd TradingAgents

# Create virtual environment
python3 -m venv venv # On Windows use `python -m venv venv`
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

### Required API Keys

To get started, you'll need these API keys:

1. **OpenRouter API Key** (Required)
   - Sign up at [OpenRouter.ai](https://openrouter.ai/)
   - Generate an API key in your dashboard
   - Provides access to 200+ LLM models including DeepSeek R1 and Chat
   - **Web search capability**: $4 per 1000 results for real-time data

2. **Yahoo Finance** (Free - Built-in)
   - Real-time stock prices and technical indicators
   - No API key required - handled automatically

Set your environment variables:

```bash
# Required
export OPENROUTER_API_KEY="your_openrouter_api_key"

# Optional: For OpenRouter usage tracking
export OPENROUTER_SITE_URL="your_site_url"
export OPENROUTER_SITE_NAME="TradingAgents"
```

Alternatively, copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
# Edit .env with your API keys
```

### Cost-Effective Setup

**Recommended Budget Configuration:**
- **DeepSeek R1**: Free reasoning model for complex analysis
- **DeepSeek Chat**: Free quick responses
- **Web Search**: ~$0.02 per search (5 results)
- **Total Cost**: ~$0.06 per complete analysis

```python
# Budget-friendly configuration
config = {
    "deep_think_llm": "deepseek/deepseek-r1-0528:free",
    "quick_think_llm": "deepseek/deepseek-chat-v3-0324:free", 
    "use_web_search": True,  # Real-time data for $0.02/search
}
```

### Basic Usage

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Initialize with real-time web search enabled
config = DEFAULT_CONFIG.copy()
config["use_web_search"] = True  # Enable real-time data access

ta = TradingAgentsGraph(debug=True, config=config)

# Run real-time analysis
_, decision = ta.propagate("NVDA", "2024-05-10")
print(f"Trading Decision: {decision}")
```

### Multiple Configuration Examples

See `main.py` for complete examples:

```python
# Budget Setup (~$0.06 per analysis)
config_budget = {
    "deep_think_llm": "deepseek/deepseek-r1-0528:free",
    "quick_think_llm": "deepseek/deepseek-chat-v3-0324:free",
    "use_web_search": True,
    "max_debate_rounds": 1,
}

# Balanced Setup (~$0.15 per analysis) 
config_balanced = {
    "deep_think_llm": "deepseek/deepseek-r1-0528:free",
    "quick_think_llm": "openai/gpt-4o-mini",
    "use_web_search": True,
    "max_debate_rounds": 2,
}

# Premium Setup (~$0.50+ per analysis)
config_premium = {
    "deep_think_llm": "openai/gpt-4o",
    "quick_think_llm": "openai/gpt-4o",
    "use_web_search": True,
    "max_debate_rounds": 3,
}
```

## OpenRouter Web Search Features

This version leverages OpenRouter's **native web search capabilities** for real-time financial data:

### **Real-Time Data Sources**
- **Current Stock News**: Latest articles and social media sentiment
- **Global Economic News**: Macroeconomic developments and market events
- **Company Fundamentals**: Recent earnings, analyst opinions, financial metrics
- **Market Context**: Real-time market conditions and sector trends

### **Web Search Implementation**
- **Source Citations**: OpenRouter provides URLs for verification
- **Cost Predictable**: $4 per 1000 search results ($0.02 per 5-result search)
- **No External APIs**: Eliminates need for FinnHub, NewsAPI, etc.

### **Model Configuration**
- **Easy Model Switching**: Change models via config without code changes

### **Performance Features**
- **No External Embeddings**: Memory system uses ChromaDB's built-in embeddings
- **Unified API**: Single OpenRouter client handles all LLM interactions

### **Cost Optimization**
- Uses free tier models by default (DeepSeek family)
- Optional upgrade to premium models via configuration

## Usage Examples

### Command Line Interface

```bash
python3 -m cli.main
```

The CLI provides an interactive interface for selecting tickers, dates and research depth.

<p align="center">
  <img src="assets/cli/cli_init.png" width="100%" style="display: inline-block; margin: 0 2%;">
</p>

### Python API

#### Basic Configuration
```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

# Use defaults (DeepSeek models)
ta = TradingAgentsGraph(debug=True, config=DEFAULT_CONFIG)
_, decision = ta.propagate("AAPL", "2024-05-10")
```

#### Custom Configuration
```python
config = DEFAULT_CONFIG.copy()

# Customize models
config["deep_think_llm"] = "openai/o4-mini-high"      # Reasoning model
config["quick_think_llm"] = "openai/gpt-4o-mini"    # Fast model

# Adjust debate rounds
config["max_debate_rounds"] = 3
config["max_risk_discuss_rounds"] = 2

# Initialize
ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("TSLA", "2024-05-10")
```

#### Memory and Reflection
```python
# Run analysis
_, decision = ta.propagate("NVDA", "2024-05-10")

# Learn from results (after knowing actual returns)
ta.reflect_and_remember(1000)  # Positive return
# ta.reflect_and_remember(-500)  # Negative return
```

### PDF Report Generation

TradingAgents automatically generates professional PDF reports alongside markdown reports for enhanced readability and presentation.

#### Automatic PDF Generation
PDFs are generated automatically after each analysis when the required dependencies are installed:

#### Manual PDF Generation
Generate PDFs from existing markdown reports:

```bash
# Generate PDFs for specific analysis
python3 generate_pdfs.py --symbol NVDA --date 2025-07-24

# Generate PDFs for latest analysis
python3 generate_pdfs.py --symbol NVDA --latest

# Generate PDFs for all analyses
python3 generate_pdfs.py --all

# List available analyses
python3 generate_pdfs.py --list
```

#### PDF Output Structure
```
results/
└── NVDA/
    └── 2025-07-24/
        ├── reports/           # Original markdown reports
        │   ├── market_report.md
        │   ├── sentiment_report.md
        │   └── ...
        └── reports_pdf/       # Generated PDF reports
            ├── NVDA_2025-07-24_analysis_report.pdf  # Comprehensive report
            └── NVDA_2025-07-24_summary.pdf          # Executive summary
```

## Configuration

### Available Models (OpenRouter)

#### **Free Models**
- `deepseek-r1-0528`: Advanced reasoning model (default for deep thinking)
- `deepseek-chat-v3-0324`: Fast chat model (default for quick thinking)
- `llama-3.3-70b-instruct`: Meta's Llama 3.3 70B Instruct
- `gemma-3-27b-it`: Google's Gemma 3 27B
- `mistral-small-3.1-24b-instruct`: Mistral Small 3.1 24B Instruct
- Many more available

#### **Model Configuration**
```python
# Full OpenRouter names
config["deep_think_llm"] = "deepseek/deepseek-r1-0528:free"
config["quick_think_llm"] = "deepseek/deepseek-chat-v3-0324:free"
```

### Configuration Options

```python
DEFAULT_CONFIG = {
    # LLM Settings
    "llm_provider": "openrouter",
    "deep_think_llm": "deepseek/deepseek-r1-0528:free",        # Model for deep analysis
    "quick_think_llm": "deepseek/deepseek-chat-v3-0324:free",     # Model for quick analysis

    # Debate Settings
    "max_debate_rounds": 1,                 # Bull/Bear debate rounds
    "max_risk_discuss_rounds": 1,           # Risk discussion rounds
    
    # Data Settings
    "online_tools": True,                   # True = live data, False = cached
    "use_web_search": True,                 # Enable real-time web search
    
    # OpenRouter Settings (optional)
    "openrouter_site_url": "",              # For rankings
    "openrouter_site_name": "TradingAgents", # For rankings
}
```

### Cost-Effective Configuration

```python
# Minimal cost configuration
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "deepseek/deepseek-chat-v3-0324:free"     # Use fast model for both
config["quick_think_llm"] = "deepseek/deepseek-chat-v3-0324:free"
config["max_debate_rounds"] = 1                # Fewer rounds
config["max_risk_discuss_rounds"] = 1
```

### High-Quality Configuration

```python
# Maximum quality configuration
config = DEFAULT_CONFIG.copy()
config["deep_think_llm"] = "openai/o3"       # Reasoning model
config["quick_think_llm"] = "openai/gpt-4.1"    # Fast model
config["max_debate_rounds"] = 3                # More debate rounds
config["max_risk_discuss_rounds"] = 2
config["online_tools"] = True                  # Live data
```

## Acknowledgments

This project is based on the original [TradingAgents](https://github.com/TauricResearch/TradingAgents) framework by [Tauric Research](https://tauric.ai/). We extend our gratitude to the original authors for their groundbreaking work in multi-agent financial analysis.

### Original Authors
- Yijia Xiao (UCLA)
- Edward Sun
- Di Luo
- Wei Wang

## Citation

If you use TradingAgents in your research, please cite the original work:

```bibtex
@misc{xiao2025tradingagentsmultiagentsllmfinancial,
      title={TradingAgents: Multi-Agents LLM Financial Trading Framework}, 
      author={Yijia Xiao and Edward Sun and Di Luo and Wei Wang},
      year={2025},
      eprint={2412.20138},
      archivePrefix={arXiv},
      primaryClass={q-fin.TR},
      url={https://arxiv.org/abs/2412.20138}, 
}
```

## License

This project maintains the same license as the original TradingAgents framework. Please refer to the LICENSE file for details.