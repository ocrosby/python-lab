import pytest
import requests

from ncaa.scraper.fetcher import RequestsHtmlFetcher


def test_requests_html_fetcher_success(mocker):
    mock_response = mocker.Mock()
    mock_response.text = "<html><body>Test</body></html>"
    mock_response.raise_for_status = mocker.Mock()

    mock_get = mocker.patch("requests.get", return_value=mock_response)

    fetcher = RequestsHtmlFetcher()
    result = fetcher.fetch("http://example.com")

    assert result == "<html><body>Test</body></html>"
    mock_get.assert_called_once_with(
        "http://example.com",
        timeout=10,
        headers={"User-Agent": "Mozilla/5.0 (compatible; ncaa-scraper/1.0)"},
    )


def test_requests_html_fetcher_error(mocker):
    mocker.patch(
        "requests.get",
        side_effect=requests.RequestException("Network error"),
    )

    fetcher = RequestsHtmlFetcher()
    with pytest.raises(RuntimeError, match="Error fetching"):
        fetcher.fetch("http://example.com")


def test_requests_html_fetcher_custom_timeout(mocker):
    mock_response = mocker.Mock()
    mock_response.text = "<html></html>"
    mock_response.raise_for_status = mocker.Mock()

    mock_get = mocker.patch("requests.get", return_value=mock_response)

    fetcher = RequestsHtmlFetcher(timeout=30)
    fetcher.fetch("http://example.com")

    mock_get.assert_called_once()
    assert mock_get.call_args[1]["timeout"] == 30


def test_requests_html_fetcher_default_timeout(mocker):
    mock_response = mocker.Mock()
    mock_response.text = "<html></html>"
    mock_response.raise_for_status = mocker.Mock()

    mock_get = mocker.patch("requests.get", return_value=mock_response)

    fetcher = RequestsHtmlFetcher()
    fetcher.fetch("http://example.com")

    assert mock_get.call_args[1]["timeout"] == 10


def test_requests_html_fetcher_includes_user_agent(mocker):
    mock_response = mocker.Mock()
    mock_response.text = "<html></html>"
    mock_response.raise_for_status = mocker.Mock()

    mock_get = mocker.patch("requests.get", return_value=mock_response)

    fetcher = RequestsHtmlFetcher()
    fetcher.fetch("http://example.com")

    headers = mock_get.call_args[1]["headers"]
    assert "User-Agent" in headers
    assert headers["User-Agent"] == "Mozilla/5.0 (compatible; ncaa-scraper/1.0)"
