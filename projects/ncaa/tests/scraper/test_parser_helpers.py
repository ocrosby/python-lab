import pytest
from bs4 import BeautifulSoup

from ncaa.scraper.models import Gender, Season
from ncaa.scraper.parser_helpers import (
    _strip_suffix,
    _strip_suffix_case_insensitive,
    apply_default_gender,
    extract_gender,
    extract_season_name,
    map_season,
    normalize_sport_name,
)


def test_extract_gender_men():
    assert extract_gender("Soccer - Men") == Gender.MEN
    assert extract_gender("Basketball Men") == Gender.MEN
    assert extract_gender("men's soccer") == Gender.MEN


def test_extract_gender_women():
    assert extract_gender("Soccer - Women") == Gender.WOMEN
    assert extract_gender("Basketball Women") == Gender.WOMEN
    assert extract_gender("women's basketball") == Gender.WOMEN


def test_extract_gender_unspecified():
    assert extract_gender("Football") == Gender.UNSPECIFIED
    assert extract_gender("Baseball") == Gender.UNSPECIFIED


def test_strip_suffix():
    assert _strip_suffix("Soccer - Men", " - Men") == "Soccer"
    assert _strip_suffix("Basketball", " - Men") == "Basketball"
    assert _strip_suffix("Test  ", " ") == "Test"


def test_strip_suffix_case_insensitive():
    assert _strip_suffix_case_insensitive("Soccer - MEN", " - men") == "Soccer"
    assert _strip_suffix_case_insensitive("Soccer - Men", " - MEN") == "Soccer"
    assert _strip_suffix_case_insensitive("Basketball", " - Men") == "Basketball"


def test_normalize_sport_name():
    assert normalize_sport_name("Soccer - Men", Gender.MEN) == "Soccer"
    assert normalize_sport_name("Soccer - Women", Gender.WOMEN) == "Soccer"
    assert normalize_sport_name("Football", Gender.UNSPECIFIED) == "Football"


def test_normalize_sport_name_case_insensitive():
    assert normalize_sport_name("Soccer - MEN", Gender.MEN) == "Soccer"
    assert normalize_sport_name("Soccer - WOMEN", Gender.WOMEN) == "Soccer"


def test_extract_season_name():
    html = '<div><div class="season-header">Fall Sports</div></div>'
    soup = BeautifulSoup(html, "html.parser")
    season_block = soup.select_one("div")

    result = extract_season_name(season_block)
    assert result == "Fall Sports"


def test_extract_season_name_missing():
    html = "<div>No header</div>"
    soup = BeautifulSoup(html, "html.parser")
    season_block = soup.select_one("div")

    result = extract_season_name(season_block)
    assert result is None


def test_extract_season_name_with_extra_whitespace():
    html = '<div><div class="season-header">Fall   Sports  </div></div>'
    soup = BeautifulSoup(html, "html.parser")
    season_block = soup.select_one("div")

    result = extract_season_name(season_block)
    assert result == "Fall Sports"


def test_map_season_fall():
    assert map_season("Fall Sports") == Season.FALL
    assert map_season("FALL") == Season.FALL


def test_map_season_winter():
    assert map_season("Winter Sports") == Season.WINTER
    assert map_season("winter") == Season.WINTER


def test_map_season_spring():
    assert map_season("Spring Sports") == Season.SPRING
    assert map_season("SPRING") == Season.SPRING


def test_map_season_unknown():
    with pytest.raises(ValueError, match="Unknown season"):
        map_season("Summer")


def test_apply_default_gender_keeps_specified_gender():
    result = apply_default_gender("Soccer", Gender.MEN)
    assert result == Gender.MEN


def test_apply_default_gender_applies_default_for_softball():
    result = apply_default_gender("Softball", Gender.UNSPECIFIED)
    assert result == Gender.WOMEN


def test_apply_default_gender_applies_default_for_baseball():
    result = apply_default_gender("Baseball", Gender.UNSPECIFIED)
    assert result == Gender.MEN


def test_apply_default_gender_keeps_unspecified_for_unknown():
    result = apply_default_gender("UnknownSport", Gender.UNSPECIFIED)
    assert result == Gender.UNSPECIFIED
