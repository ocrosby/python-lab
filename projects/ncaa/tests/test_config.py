from datetime import datetime

from ncaa.config import (
    CASABLANCA_SCHEDULE_BASE_URL,
    CASABLANCA_SCOREBOARD_BASE_URL,
    NCAA_BASE_URL,
    NCAA_DATE_FORMAT,
    build_sport_name,
    format_date_offset,
    get_today_date_string,
)


def test_ncaa_base_url():
    assert NCAA_BASE_URL == "https://www.ncaa.com"


def test_casablanca_scoreboard_base_url():
    assert (
        CASABLANCA_SCOREBOARD_BASE_URL == "https://data.ncaa.com/casablanca/scoreboard"
    )


def test_casablanca_schedule_base_url():
    assert CASABLANCA_SCHEDULE_BASE_URL == "https://data.ncaa.com/casablanca/schedule"


def test_ncaa_date_format():
    assert NCAA_DATE_FORMAT == "%Y/%m/%d"


def test_get_today_date_string_returns_today_in_correct_format(mocker):
    mock_datetime = mocker.patch("ncaa.config.datetime")
    mock_datetime.now.return_value = datetime(2024, 3, 15, 10, 30, 0)

    result = get_today_date_string()

    assert result == "2024/03/15"


def test_get_today_date_string_formats_single_digit_month_and_day(mocker):
    mock_datetime = mocker.patch("ncaa.config.datetime")
    mock_datetime.now.return_value = datetime(2024, 1, 5, 10, 30, 0)

    result = get_today_date_string()

    assert result == "2024/01/05"


def test_format_date_offset_zero_offset_returns_today(mocker):
    mock_datetime = mocker.patch("ncaa.config.datetime")
    mock_datetime.now.return_value = datetime(2024, 3, 15, 10, 30, 0)

    result = format_date_offset(0)

    assert result == "2024/03/15"


def test_format_date_offset_positive_offset_adds_days(mocker):
    mock_datetime = mocker.patch("ncaa.config.datetime")
    mock_datetime.now.return_value = datetime(2024, 3, 15, 10, 30, 0)

    result = format_date_offset(7)

    assert result == "2024/03/22"


def test_format_date_offset_negative_offset_subtracts_days(mocker):
    mock_datetime = mocker.patch("ncaa.config.datetime")
    mock_datetime.now.return_value = datetime(2024, 3, 15, 10, 30, 0)

    result = format_date_offset(-5)

    assert result == "2024/03/10"


def test_format_date_offset_handles_month_rollover(mocker):
    mock_datetime = mocker.patch("ncaa.config.datetime")
    mock_datetime.now.return_value = datetime(2024, 3, 30, 10, 30, 0)

    result = format_date_offset(5)

    assert result == "2024/04/04"


def test_build_sport_name_combines_sport_and_gender_with_hyphen():
    result = build_sport_name("basketball", "men")

    assert result == "basketball-men"


def test_build_sport_name_works_with_women():
    result = build_sport_name("basketball", "women")

    assert result == "basketball-women"


def test_build_sport_name_works_with_different_sports():
    result = build_sport_name("soccer", "men")

    assert result == "soccer-men"


def test_build_sport_name_preserves_case():
    result = build_sport_name("BASKETBALL", "MEN")

    assert result == "BASKETBALL-MEN"
