"""
Setup script for the TradingAgents package (OpenRouter-only version).
"""

from setuptools import setup, find_packages

setup(
    name="tradingagents-openrouter",
    version="0.1.0",
    description="Multi‑Agent LLM Financial Trading Framework with OpenRouter Integration",
    author="Esteban Ortiz",
    author_email="ee.ortiz@uniandes.edu.co",
    url="https://github.com/ee-ortiz/TradingAgents",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        # Core dependencies
        "python-dotenv>=1.0.0",
        "typing-extensions>=4.14.0",

        # LangChain and OpenAI
        "langchain-openai>=0.3.23",
        "langchain-experimental>=0.3.4",
        "langgraph>=0.4.8",
        "openai>=1.14.2",

        # Data processing
        "pandas>=2.3.0",
        "yfinance>=0.2.63",
        "stockstats>=0.6.5",

        # Web scraping and APIs
        "requests>=2.32.4",
        "feedparser>=6.0.11",
        "praw>=7.8.1",

        # PDF generation
        "pdfkit>=1.0.0",
        "markdown2>=2.4.0",

        # Utilities
        "tqdm>=4.67.1",
        "pytz>=2025.2",
        "python-dateutil>=2.8.2",

        # Memory and embeddings
        "chromadb>=1.0.12",
    ],
    entry_points={
        "console_scripts": [
            "tradingagents=cli.main:app",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Financial and Trading Industry",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
)
