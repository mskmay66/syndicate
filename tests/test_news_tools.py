from unittest.mock import MagicMock, patch
from datetime import datetime

from syndicate.tools import NewsTools


class DummyUser:
    def __init__(self):
        self.broker_api_key = MagicMock()
        self.broker_secret_key = MagicMock()
        self.broker_api_key.get_secret_value.return_value = "key"
        self.broker_secret_key.get_secret_value.return_value = "secret"


def test_extract_article_data_nested():
    article = {
        "content": {
            "title": "Test Title",
            "summary": "Test Summary",
            "provider": {"displayName": "Reuters"},
            "canonicalUrl": {"url": "http://example.com"},
            "pubDate": "2024-01-01T12:00:00Z",
        }
    }

    result = NewsTools._extract_article_data(article)

    assert result["title"] == "Test Title"
    assert result["summary"] == "Test Summary"
    assert result["publisher"] == "Reuters"
    assert result["link"] == "http://example.com"
    assert isinstance(result["pub_date"], datetime)


def test_extract_article_data_flat():
    article = {
        "title": "Flat Title",
        "summary": "Flat Summary",
        "publisher": "Bloomberg",
        "link": "http://flat.com",
    }

    result = NewsTools._extract_article_data(article)

    assert result == {
        "title": "Flat Title",
        "summary": "Flat Summary",
        "publisher": "Bloomberg",
        "link": "http://flat.com",
        "pub_date": None,
    }


def test_extract_article_data_invalid_date():
    article = {
        "content": {
            "title": "Bad Date",
            "pubDate": "not-a-date",
        }
    }

    result = NewsTools._extract_article_data(article)

    assert result["pub_date"] is None


def test_get_news_success():
    user = DummyUser()
    tools = NewsTools(user)

    mock_news = {
        "news": [
            {
                "source": "Reuters",
                "headline": "Market up",
                "summary": "Stocks are rising",
                "published_at": "2024-01-01",
            }
        ]
    }

    tools.news_client.get_news = MagicMock(return_value=mock_news)

    get_news = tools.build_tools()[0].func

    result = get_news(["AAPL"])

    assert "Market up" in result
    tools.news_client.get_news.assert_called_once()


def test_get_news_failure():
    user = DummyUser()
    tools = NewsTools(user)

    tools.news_client.get_news = MagicMock(return_value=None)

    get_news = tools.build_tools()[0].func

    result = get_news(["AAPL"])

    assert "Failed to get news" in result


def test_get_news_multiple_tickers():
    user = DummyUser()
    tools = NewsTools(user)

    tools.news_client.get_news = MagicMock(return_value={"news": []})

    get_news = tools.build_tools()[0].func

    get_news(["AAPL", "GOOG"])

    args, kwargs = tools.news_client.get_news.call_args
    request = args[0]

    assert "AAPL,GOOG" in request.symbols


@patch("syndicate.tools.news.yf.Search")
def test_get_global_news_success(mock_search):
    user = DummyUser()
    tools = NewsTools(user)

    mock_search.return_value.news = [
        {
            "content": {
                "title": "Global News",
                "summary": "Big event",
                "provider": {"displayName": "WSJ"},
                "canonicalUrl": {"url": "http://news.com"},
            }
        }
    ]

    _, get_global_news = tools.build_tools()

    result = get_global_news.func()

    assert "Global News" in result


@patch("syndicate.tools.news.yf.Search", side_effect=Exception("boom"))
def test_get_global_news_failure(mock_search):
    user = DummyUser()
    tools = NewsTools(user)

    _, get_global_news = tools.build_tools()

    result = get_global_news.func()

    assert result == "Failed to get global news."


def test_extract_article_url_fallback():
    article = {"content": {"clickThroughUrl": {"url": "http://fallback.com"}}}

    result = NewsTools._extract_article_data(article)

    assert result["link"] == "http://fallback.com"
