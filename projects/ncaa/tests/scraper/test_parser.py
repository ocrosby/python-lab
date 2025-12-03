import pytest
from bs4 import BeautifulSoup

from ncaa.scraper.models import Gender, Season
from ncaa.scraper.parser import (
    ParsedSportData,
    _create_sports_from_group,
    _find_sports_nav,
    _should_skip_unspecified_entry,
    parse_sports,
)


@pytest.fixture
def sample_html():
    return """
    <html>
        <div class="sports-nav">
            <div class="season">
                <h3 class="season-header">Fall Sports</h3>
                <a class="sport-link" href="/football">Football</a>
                <a class="sport-link" href="/soccer-men">Soccer - Men</a>
                <a class="sport-link" href="/soccer-women">Soccer - Women</a>
            </div>
            <div class="season">
                <h3 class="season-header">Winter Sports</h3>
                <a class="sport-link" href="/basketball-men">Basketball - Men</a>
                <a class="sport-link" href="/basketball-women">Basketball - Women</a>
            </div>
        </div>
    </html>
    """


@pytest.fixture
def mock_gender_resolver(mocker):
    resolver = mocker.Mock()
    resolver.resolve.side_effect = lambda name, gender: gender
    return resolver


def test_parsed_sport_data():
    entry = ParsedSportData("Basketball", Gender.MEN, "http://example.com")
    assert entry.name == "Basketball"
    assert entry.gender == Gender.MEN
    assert entry.url == "http://example.com"


def test_should_skip_unspecified_entry():
    assert _should_skip_unspecified_entry(
        Gender.UNSPECIFIED, {Gender.MEN, Gender.WOMEN}
    )
    assert not _should_skip_unspecified_entry(Gender.MEN, {Gender.MEN, Gender.WOMEN})
    assert not _should_skip_unspecified_entry(Gender.UNSPECIFIED, {Gender.UNSPECIFIED})


def test_create_sports_from_group():
    entries: list[tuple[Gender, str | None]] = [
        (Gender.MEN, "http://example.com/men"),
        (Gender.WOMEN, "http://example.com/women"),
    ]
    sports = _create_sports_from_group("Basketball", entries, Season.WINTER)

    assert len(sports) == 2
    assert sports[0].name == "Basketball"
    assert sports[0].gender == Gender.MEN
    assert sports[0].season == Season.WINTER
    assert sports[1].gender == Gender.WOMEN


def test_create_sports_from_group_filters_unspecified():
    entries: list[tuple[Gender, str | None]] = [
        (Gender.UNSPECIFIED, None),
        (Gender.MEN, "http://example.com/men"),
    ]
    sports = _create_sports_from_group("Basketball", entries, Season.WINTER)

    assert len(sports) == 1
    assert sports[0].gender == Gender.MEN


def test_parse_sports(sample_html, mock_gender_resolver):
    sports = parse_sports(sample_html, gender_resolver=mock_gender_resolver)

    assert len(sports) > 0
    sport_names = {s.name for s in sports}
    assert "Football" in sport_names
    assert "Soccer" in sport_names
    assert "Basketball" in sport_names


def test_parse_sports_with_default_resolver(sample_html):
    sports = parse_sports(sample_html)
    assert len(sports) > 0


def test_parse_sports_missing_nav():
    html = "<html><body>No sports nav here</body></html>"
    with pytest.raises(ValueError, match="Could not find"):
        parse_sports(html)


def test_find_sports_nav_success(sample_html):
    soup = BeautifulSoup(sample_html, "html.parser")
    nav = _find_sports_nav(soup)
    assert nav is not None
    assert nav.name == "div"


def test_find_sports_nav_missing():
    soup = BeautifulSoup("<html></html>", "html.parser")
    with pytest.raises(ValueError):
        _find_sports_nav(soup)
