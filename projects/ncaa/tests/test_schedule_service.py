from unittest.mock import Mock

import pytest

from ncaa.casablanca_models import (
    Game,
    GameState,
    GameWrapper,
    ScheduleResponse,
    Team,
    TeamNames,
)
from ncaa.constants import DEFAULT_DIVISION
from ncaa.schedule_service import ScheduleService


@pytest.fixture
def mock_client():
    return Mock()


@pytest.fixture
def mock_schedule_helper():
    return Mock()


@pytest.fixture
def schedule_service(mock_client, mock_schedule_helper):
    return ScheduleService(client=mock_client, schedule_helper=mock_schedule_helper)


@pytest.fixture
def sample_game():
    team_names = TeamNames(char6="DUKE", short="Duke", seo="duke", full="Duke")
    team = Team(names=team_names, score=0, winner=None)

    game = Game(
        url="http://example.com",
        startTimeEpoch=1234567890,
        gameState=GameState.SCHEDULED,
        home=team,
        away=team,
    )

    return GameWrapper(game=game)


@pytest.fixture
def sample_schedule(sample_game):
    return ScheduleResponse(games=[sample_game])


def test_get_schedule_delegates_to_client(
    schedule_service, mock_client, sample_schedule
):
    mock_client.get_schedule.return_value = sample_schedule

    result = schedule_service.get_schedule("basketball-men", "2024/01/01", "d1")

    mock_client.get_schedule.assert_called_once_with(
        "basketball-men", "d1", "2024/01/01"
    )
    assert isinstance(result, ScheduleResponse)


def test_get_schedule_uses_default_division(
    schedule_service, mock_client, sample_schedule
):
    mock_client.get_schedule.return_value = sample_schedule

    schedule_service.get_schedule("basketball-women", "2024/01/01")

    mock_client.get_schedule.assert_called_once_with(
        "basketball-women", DEFAULT_DIVISION.value, "2024/01/01"
    )


def test_get_todays_schedule_delegates_to_client(
    schedule_service, mock_client, sample_schedule
):
    mock_client.get_todays_schedule.return_value = sample_schedule

    result = schedule_service.get_todays_schedule("basketball-men", "d1")

    mock_client.get_todays_schedule.assert_called_once_with("basketball-men", "d1")
    assert isinstance(result, ScheduleResponse)


def test_get_todays_schedule_uses_default_division(schedule_service, mock_client):
    mock_client.get_todays_schedule.return_value = ScheduleResponse(games=[])

    schedule_service.get_todays_schedule("football")

    mock_client.get_todays_schedule.assert_called_once_with(
        "football", DEFAULT_DIVISION.value
    )


def test_get_upcoming_schedules_delegates_to_client(
    schedule_service, mock_client, sample_schedule
):
    mock_client.get_upcoming_schedules.return_value = [
        sample_schedule,
        sample_schedule,
    ]

    result = schedule_service.get_upcoming_schedules("basketball-men", "d1", 7)

    mock_client.get_upcoming_schedules.assert_called_once_with(
        "basketball-men", "d1", 7
    )
    assert len(result) == 2


def test_get_upcoming_schedules_uses_default_days(schedule_service, mock_client):
    mock_client.get_upcoming_schedules.return_value = []

    schedule_service.get_upcoming_schedules("football")

    mock_client.get_upcoming_schedules.assert_called_once_with(
        "football", DEFAULT_DIVISION.value, 7
    )


def test_get_upcoming_games_collects_games_from_schedules(
    schedule_service, mock_client, mock_schedule_helper, sample_schedule
):
    mock_client.get_upcoming_schedules.return_value = [
        sample_schedule,
        sample_schedule,
    ]
    mock_schedule_helper.collect_games_from_schedules.return_value = [
        sample_schedule.games[0]
    ]

    result = schedule_service.get_upcoming_games("basketball-men", "d1", 5)

    mock_client.get_upcoming_schedules.assert_called_once_with(
        "basketball-men", "d1", 5
    )
    mock_schedule_helper.collect_games_from_schedules.assert_called_once()
    assert len(result) == 1


def test_get_football_schedule_gets_football_schedule(
    schedule_service, mock_client, sample_schedule
):
    mock_client.get_schedule.return_value = sample_schedule

    result = schedule_service.get_football_schedule("2024/01/01", "d1")

    mock_client.get_schedule.assert_called_once_with("football", "d1", "2024/01/01")
    assert isinstance(result, ScheduleResponse)


def test_get_football_schedule_uses_default_division(
    schedule_service, mock_client, sample_schedule
):
    mock_client.get_schedule.return_value = sample_schedule

    schedule_service.get_football_schedule("2024/01/01")

    mock_client.get_schedule.assert_called_once_with(
        "football", DEFAULT_DIVISION.value, "2024/01/01"
    )


def test_get_soccer_schedule_builds_mens_soccer_sport_name(
    schedule_service, mock_client, sample_schedule
):
    mock_client.get_schedule.return_value = sample_schedule

    result = schedule_service.get_soccer_schedule("men", "2024/01/01", "d1")

    mock_client.get_schedule.assert_called_once_with("soccer-men", "d1", "2024/01/01")
    assert isinstance(result, ScheduleResponse)


def test_get_soccer_schedule_builds_womens_soccer_sport_name(
    schedule_service, mock_client, sample_schedule
):
    mock_client.get_schedule.return_value = sample_schedule

    schedule_service.get_soccer_schedule("women", "2024/01/01")

    mock_client.get_schedule.assert_called_once_with(
        "soccer-women", DEFAULT_DIVISION.value, "2024/01/01"
    )


def test_clear_cache_delegates_to_client(schedule_service, mock_client):
    schedule_service.clear_cache()

    mock_client.clear_cache.assert_called_once()
