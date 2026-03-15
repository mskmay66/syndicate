import json
from typing import List
from datetime import datetime, timedelta

import yfinance as yf

from alpaca.data.historical.news import NewsClient
from alpaca.data.requests import NewsRequest
from langchain_core.tools import tool

from ..secrets import get_secret_from_keyring

API_KEY = get_secret_from_keyring("broker_api_key")
API_SECRET_KEY = get_secret_from_keyring("broker_secret_key")

news_client = None
if API_KEY and API_SECRET_KEY:
    news_client = NewsClient(API_KEY, API_SECRET_KEY)


def _extract_article_data(article: dict) -> dict:
    """Extract article data from yfinance news format (handles nested 'content' structure)."""
    # Handle nested content structure
    if "content" in article:
        content = article["content"]
        title = content.get("title", "No title")
        summary = content.get("summary", "")
        provider = content.get("provider", {})
        publisher = provider.get("displayName", "Unknown")

        # Get URL from canonicalUrl or clickThroughUrl
        url_obj = content.get("canonicalUrl") or content.get("clickThroughUrl") or {}
        link = url_obj.get("url", "")

        # Get publish date
        pub_date_str = content.get("pubDate", "")
        pub_date = None
        if pub_date_str:
            try:
                pub_date = datetime.fromisoformat(pub_date_str.replace("Z", "+00:00"))
            except (ValueError, AttributeError):
                pass

        return {
            "title": title,
            "summary": summary,
            "publisher": publisher,
            "link": link,
            "pub_date": pub_date,
        }
    else:
        # Fallback for flat structure
        return {
            "title": article.get("title", "No title"),
            "summary": article.get("summary", ""),
            "publisher": article.get("publisher", "Unknown"),
            "link": article.get("link", ""),
            "pub_date": None,
        }


@tool(
    "get_news",
    return_direct=True,
    description="Gets the latest news for a given ticker or list of tickers. Example usage: get_news('AAPL') or get_news(['AAPL', 'GOOG'])",
)
def get_news(tickers: List[str], look_back: int = 7) -> str:
    keys_to_extract = ["source", "headline", "summary", "published_at"]
    symbols = ",".join(tickers)
    current_time = datetime.now()
    start_time = current_time - timedelta(days=look_back)
    news_request = NewsRequest(
        symbols=symbols, start=start_time, end=current_time, limit=50
    )
    if not news_client:
        return "Alpaca API key and secret key are required to use this tool. Please set the ALPACA_API_KEY and ALPACA_API_SECRET_KEY environment variables."
    news_response = news_client.get_news(news_request)
    if not news_response:
        return f"Failed to get news for {symbols}. Reason: {news_response['message']}"
    articles = news_response["news"]
    formatted_response = [
        {key: dict(article).get(key) for key in keys_to_extract} for article in articles
    ]
    return json.dumps(formatted_response, indent=2, default=str)


@tool(
    "get_global_news",
    return_direct=True,
    description="Gets the latest global news related to the stock market and economy. Example usage: get_global_news()",
)
def get_global_news(limit=10) -> str:
    search_queries = [
        "stock market economy",
        "Federal Reserve interest rates",
        "inflation economic outlook",
        "global markets trading",
    ]
    try:
        news = []
        for query in search_queries:
            search = yf.Search(query, news_count=limit, enable_fuzzy_query=True)

            if search.news:
                for article in search.news:
                    article_data = _extract_article_data(article)
                    news.append(article_data)
        return json.dumps(news, indent=2, default=str)
    except Exception:
        return "Failed to get global news."
