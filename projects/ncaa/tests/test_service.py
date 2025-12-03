from unittest.mock import Mock

import pytest

from ncaa.models import Gender, Season, Sport
from ncaa.service import NcaaSportsService, NcaaSportsServiceError, get_ncaa_sports


@pytest.fixture
def mock_html_fetcher():
    return Mock()


@pytest.fixture
def mock_gender_resolver():
    return Mock()


@pytest.fixture
def sample_sports():
    return [
        Sport(name="Basketball", gender=Gender.MEN, season=Season.WINTER),
        Sport(name="Soccer", gender=Gender.WOMEN, season=Season.FALL),
    ]


def test_ncaa_sports_service_init(mock_html_fetcher, mock_gender_resolver):
    service = NcaaSportsService(mock_html_fetcher, mock_gender_resolver)

    assert service.html_fetcher is mock_html_fetcher
    assert service.gender_resolver is mock_gender_resolver


def test_ncaa_sports_service_init_without_gender_resolver(mock_html_fetcher):
    service = NcaaSportsService(mock_html_fetcher)

    assert service.html_fetcher is mock_html_fetcher
    assert service.gender_resolver is None


def test_get_sports_success(mocker, mock_html_fetcher, sample_sports):
    mock_html_fetcher.fetch.return_value = "<html><body>Sports</body></html>"
    mock_parse = mocker.patch("ncaa.service.parse_sports", return_value=sample_sports)

    service = NcaaSportsService(mock_html_fetcher)
    result = service.get_sports()

    assert result == sample_sports
    mock_html_fetcher.fetch.assert_called_once_with("https://www.ncaa.com")
    mock_parse.assert_called_once()


def test_get_sports_with_gender_resolver(
    mocker, mock_html_fetcher, mock_gender_resolver, sample_sports
):
    mock_html_fetcher.fetch.return_value = "<html><body>Sports</body></html>"
    mock_parse = mocker.patch("ncaa.service.parse_sports", return_value=sample_sports)

    service = NcaaSportsService(mock_html_fetcher, mock_gender_resolver)
    result = service.get_sports()

    assert result == sample_sports
    mock_parse.assert_called_once_with(
        "<html><body>Sports</body></html>", gender_resolver=mock_gender_resolver
    )


def test_get_sports_parse_error(mocker, mock_html_fetcher):
    mock_html_fetcher.fetch.return_value = "<html><body>Invalid</body></html>"
    mocker.patch("ncaa.service.parse_sports", side_effect=ValueError("Parse error"))

    service = NcaaSportsService(mock_html_fetcher)

    with pytest.raises(NcaaSportsServiceError, match="Failed to parse sports data"):
        service.get_sports()


def test_get_sports_fetch_error(mock_html_fetcher):
    mock_html_fetcher.fetch.side_effect = RuntimeError("Network error")

    service = NcaaSportsService(mock_html_fetcher)

    with pytest.raises(NcaaSportsServiceError, match="Failed to fetch sports data"):
        service.get_sports()


def test_get_sports_unexpected_error(mocker, mock_html_fetcher):
    mock_html_fetcher.fetch.return_value = "<html></html>"
    mocker.patch("ncaa.service.parse_sports", side_effect=Exception("Unexpected error"))

    service = NcaaSportsService(mock_html_fetcher)

    with pytest.raises(
        NcaaSportsServiceError, match="Unexpected error retrieving NCAA sports"
    ):
        service.get_sports()


def test_get_ncaa_sports_with_fetcher(mocker, mock_html_fetcher, sample_sports):
    mock_html_fetcher.fetch.return_value = "<html><body>Sports</body></html>"
    mocker.patch("ncaa.service.parse_sports", return_value=sample_sports)

    result = get_ncaa_sports(mock_html_fetcher)

    assert result == sample_sports


def test_get_ncaa_sports_without_fetcher(mocker, sample_sports):
    mock_html = "<html><body>Sports</body></html>"
    mock_fetcher_class = mocker.patch("ncaa.html_fetcher.RequestsHtmlFetcher")
    mock_fetcher_instance = Mock()
    mock_fetcher_class.return_value = mock_fetcher_instance
    mock_fetcher_instance.fetch.return_value = mock_html
    mocker.patch("ncaa.service.parse_sports", return_value=sample_sports)

    result = get_ncaa_sports()

    assert result == sample_sports
    mock_fetcher_class.assert_called_once()
