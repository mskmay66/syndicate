```
   _____                        __    _                   __
  / ___/   __  __   ____   ____/ /   (_)  _____  ____ _  / /_  ___
  \__ \   / / / /  / __ \ / __  /   / /  / ___/ / __ `/ / __/ / _ \
 ___/ /  / /_/ /  / / / // /_/ /   / /  / /__  / /_/ / / /_  /  __/
/____/   \__, /  /_/ /_/ \__,_/   /_/   \___/  \__,_/  \__/  \___/
        /____/
```

Syndicate is an AI stock trading agent with a built-in integration with the [alpaca](https://alpaca.markets/) brokerage API. With it you can automatically follow and trade a given watchlist of tickers. It contains:

* A news analyst that reads recent news on your assets.
* A fundemental analyst to read each companies financial statements.
* A techinical analyst to look at the technical indicators for each stock, and
* A trader to buy or sell tickers based on the recommendations of the former analysts, subject to determinstic guardrails set by the user.

The package is free to download from pypi or this repo and open source, but the operates under a bring-your-own-tokens model: you need a funded account with an LLM provider in order to run it. Currently the package supports anthropic, google, openai, qwen, and moonshot models. The package provides a terminal user interface (TUI) to make setup and monitoring easy and intuitive.

## Prerequisites

Syndicate uses a variety of external tools in order to provide users with an excellent trading experience. In particular, you must have an alpca account (for trading, news, and realtime quotes), and [alphavantage](https://www.alphavantage.co/support/#api-key) for the technical indicators. You can open your accounts and claim your free api keys from the links in this document.

## Installation

You can install the package from pypi just as you would any other:

```bash
pip install syndicate
```

or, download the build artifacts from this repo:

```bash
pip install git+https://github.com/mskmay66/syndicate@alpha
```

## Setup

Configuring your syndicate agen is easy, simply open a terminal and run:

```bash
syndicate
```

You will then be confronted with the TUI which should look something like this:

![Splash Screen Demo](images/Screen%20Recording%202026-04-03%20at%205.48.05 PM.mov)

From there simply press the `s` key to toggle to the setup screen. This is what you should see (minus my setup, yours should be blank)

![Setup Screen](images/Screen Recording 2026-04-03 at 5.54.38 PM.mov)

From here just follow the prompts from the TUI to fill things out, if you are confused about what anything means, read on and it will be explained.

## How to Configure your Agent

There are lot of choices you need to make when you first confiure your agent, let's go through them one by one.

1. What stocks do you want to follow?

This should be straight forward, pick whatever tickers you are interested in.

2. What model do you want to use?

If you already have a subscription/account with a model provider that is support this could be easy, if not there are few factors to consider. First, which one is best. [This](https://arxiv.org/html/2510.02209v1) paper contains a ranking of llm's if you need to decide. TLDR: Kimi and Qwen seem to dominate for these sorts of task, but make up your own mind. Finally, what is the cost of these models? I will elave that to you, but from my demo you can see that i am running kimi becasue it is both good and relatively cheap.

## How do I get all these damn keys?
