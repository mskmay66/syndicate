# Setup Guide

Getting started with Syndicate is quick and straightforward. This guide walks you through everything you need—from installing the package to configuring your AI-powered trading agent.

## 🚀 Prerequisites

Before you begin, make sure you have access to the following services:

## 📈 Brokerage Account (Required)

You’ll need an account with Alpaca for trading, account data, and real-time market feeds.

1. Sign up here: https://alpaca.markets/
2. Paper trading is supported (recommended for beginners)

## 📊 Market Data API

Syndicate uses Alpha Vantage for technical indicators and supplementary data.

1. Get a free API key: https://www.alphavantage.co/support/#api-key
2. Free tier includes limited requests per minute/day

## 🤖 LLM Provider

You’ll also need API access to at least one supported model provider:

* Anthropic
* Google
* OpenAI
* Qwen
* Moonshot

**Tip:** Choose based on your priorities:

* Lower cost → lightweight models
* Better reasoning → more advanced models
* Faster responses → low-latency models

## 📦 Installation

Install Syndicate via PyPI:

```bash
pip install syndicate
```
Or install the latest alpha directly from GitHub:

```bash
pip install git+https://github.com/mskmay66/syndicate@alpha
```

## 🖥️ Launch the Application

Start Syndicate by running:

```bash
syndicate
```

This opens the Terminal User Interface (TUI), your main control center.
* Press s → Open setup screen
* Press f → Save configuration

## ⚙️ Configuration Step-by-Step

### 1. Choose Your Watchlist

Select the stocks (tickers) you want the agent to monitor and trade.

* Small list → lower cost, more focused
* Large list → broader coverage, higher API usage

### 2. Select Your Model

Pick your preferred LLM provider.

Consider:

* Performance: Quality of reasoning on financial data
* Cost: API pricing differences
* Latency: Speed of responses

### 3. Add Your API Keys

Enter credentials for:

* Alpaca (trading + account data)
* Alpha Vantage (market data)
* Your chosen LLM provider

All keys are required for full functionality.

## 🛡️ Configure Risk Guardrails

These settings are critical—they define how your agent behaves in live markets.

### ⏱️ Execution Frequency

How often your agent runs:

* Preset intervals (hourly, daily, etc.)
* Or a custom cron schedule

## 📊 Position Concentration

Limit how much capital can be allocated to a single asset.

## 📉 Stop Loss (%)

Automatically exit positions when losses exceed a defined threshold.

## 📈 Take Profit (%)

Lock in gains once a target percentage is reached.

## 🧪 Enable Paper Trading (Recommended)

Syndicate integrates with Alpaca’s paper trading mode.

Use this when:

* Setting up your agent for the first time
* Testing strategies
* Experimenting with different models or guardrails

No real money is used, making it ideal for safe experimentation.

## 🔄 Updating Your Settings

Need to make changes later?

* Open the TUI
* Press `s` to return to setup
* Edit your configuration
* Press `f` to save

Your previous settings will automatically load for convenience.

## 📊 Monitoring Your Agent

Once configured, return to the main dashboard to:

* Track portfolio performance
* View recent trades
* Analyze decision-making in real time
* Chat with your trading team

This gives you full visibility into how your agent operates.

## ✅ You’re Ready

Once setup is complete, your Syndicate agent will:

* Monitor your selected stocks
* Analyze news, fundamentals, and technicals
* Make decisions within your defined risk limits
* Execute trades automatically

All with minimal manual intervention.

**Next step:** Head to the dashboard and watch your trading team in action.
