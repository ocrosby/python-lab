from unittest.mock import Mock

import pytest

from ncaa.api.filters import LiveGameFilter
from ncaa.api.models import (
    Game,
    GameState,
    GameWrapper,
    ScheduleResponse,
    ScoreboardResponse,
    Team,
    TeamNames,
)
from ncaa.api.services.basketball import BasketballService
from ncaa.core.constants import DEFAULT_DIVISION


@pytest.fixture
def mock_client():
    return Mock()


@pytest.fixture
def mock_schedule_helper():
    return Mock()


@pytest.fixture
def basketball_service(mock_client, mock_schedule_helper):
    return BasketballService(client=mock_client, schedule_helper=mock_schedule_helper)


@pytest.fixture
def sample_game():
    team_names = TeamNames(char6="DUKE", short="Duke", seo="duke", full="Duke")
    home_team = Team(names=team_names, score=70, winner=True)
    away_team = Team(names=team_names, score=65, winner=False)

    game = Game(
        url="http://example.com",
        startTimeEpoch=1234567890,
        gameState=GameState.FINAL,
        home=home_team,
        away=away_team,
    )

    return GameWrapper(game=game)


@pytest.fixture
def sample_scoreboard(sample_game):
    return ScoreboardResponse(games=[sample_game])


@pytest.fixture
def sample_schedule(sample_game):
    return ScheduleResponse(games=[sample_game])


def test_get_scoreboard_delegates_to_client(basketball_service, mock_client):
    mock_client.get_scoreboard.return_value = ScoreboardResponse(games=[])

    result = basketball_service.get_scoreboard("men", "2024/01/01", "d1")

    mock_client.get_scoreboard.assert_called_once_with("men", "d1", "2024/01/01")
    assert isinstance(result, ScoreboardResponse)


def test_get_scoreboard_uses_default_division(basketball_service, mock_client):
    mock_client.get_scoreboard.return_value = ScoreboardResponse(games=[])

    basketball_service.get_scoreboard("women", "2024/01/01")

    mock_client.get_scoreboard.assert_called_once_with(
        "women", DEFAULT_DIVISION.value, "2024/01/01"
    )


def test_get_todays_scoreboard_delegates_to_client(
    basketball_service, mock_client, sample_scoreboard
):
    mock_client.get_todays_scoreboard.return_value = sample_scoreboard

    result = basketball_service.get_todays_scoreboard("men", "d1")

    mock_client.get_todays_scoreboard.assert_called_once_with("men", "d1")
    assert isinstance(result, ScoreboardResponse)


def test_get_todays_scoreboard_uses_default_division(basketball_service, mock_client):
    mock_client.get_todays_scoreboard.return_value = ScoreboardResponse(games=[])

    basketball_service.get_todays_scoreboard("women")

    mock_client.get_todays_scoreboard.assert_called_once_with(
        "women", DEFAULT_DIVISION.value
    )


def test_get_schedule_delegates_to_client_with_sport_name(
    basketball_service, mock_client, sample_schedule
):
    mock_client.get_schedule.return_value = sample_schedule

    result = basketball_service.get_schedule("men", "2024/01/01", "d1")

    mock_client.get_schedule.assert_called_once_with(
        "basketball-men", "d1", "2024/01/01"
    )
    assert isinstance(result, ScheduleResponse)


def test_get_schedule_builds_womens_sport_name(basketball_service, mock_client):
    mock_client.get_schedule.return_value = ScheduleResponse(games=[])

    basketball_service.get_schedule("women", "2024/01/01")

    mock_client.get_schedule.assert_called_once_with(
        "basketball-women", DEFAULT_DIVISION.value, "2024/01/01"
    )


def test_get_todays_schedule_delegates_to_client_with_sport_name(
    basketball_service, mock_client, sample_schedule
):
    mock_client.get_todays_schedule.return_value = sample_schedule

    result = basketball_service.get_todays_schedule("men", "d1")

    mock_client.get_todays_schedule.assert_called_once_with("basketball-men", "d1")
    assert isinstance(result, ScheduleResponse)


def test_get_upcoming_schedules_delegates_to_client(
    basketball_service, mock_client, sample_schedule
):
    mock_client.get_upcoming_schedules.return_value = [
        sample_schedule,
        sample_schedule,
    ]

    result = basketball_service.get_upcoming_schedules("men", "d1", 7)

    mock_client.get_upcoming_schedules.assert_called_once_with(
        "basketball-men", "d1", 7
    )
    assert len(result) == 2


def test_get_upcoming_schedules_uses_default_days(basketball_service, mock_client):
    mock_client.get_upcoming_schedules.return_value = []

    basketball_service.get_upcoming_schedules("women")

    mock_client.get_upcoming_schedules.assert_called_once_with(
        "basketball-women", DEFAULT_DIVISION.value, 7
    )


def test_get_games_by_filter_filters_scoreboard_games(
    basketball_service, mock_client, sample_game
):
    live_game = GameWrapper(
        game=Game(
            url="http://example.com",
            startTimeEpoch=1234567890,
            gameState=GameState.IN,
            home=sample_game.game.home,
            away=sample_game.game.away,
        )
    )

    mock_client.get_scoreboard.return_value = ScoreboardResponse(
        games=[sample_game, live_game]
    )

    game_filter = LiveGameFilter()
    result = basketball_service.get_games_by_filter("men", "d1", game_filter)

    assert len(result) == 1
    assert result[0].game.gameState == GameState.IN


def test_get_live_games_returns_live_games(
    basketball_service, mock_client, sample_game
):
    live_game = GameWrapper(
        game=Game(
            url="http://example.com",
            startTimeEpoch=1234567890,
            gameState=GameState.INPROGRESS,
            home=sample_game.game.home,
            away=sample_game.game.away,
        )
    )

    mock_client.get_scoreboard.return_value = ScoreboardResponse(
        games=[sample_game, live_game]
    )

    result = basketball_service.get_live_games("men", "d1")

    assert len(result) == 1
    assert result[0].game.gameState == GameState.INPROGRESS


def test_get_upcoming_games_collects_games_from_schedules(
    basketball_service, mock_client, mock_schedule_helper, sample_schedule
):
    mock_client.get_upcoming_schedules.return_value = [
        sample_schedule,
        sample_schedule,
    ]
    mock_schedule_helper.collect_games_from_schedules.return_value = [
        sample_schedule.games[0]
    ]

    result = basketball_service.get_upcoming_games("men", "d1", 5)

    mock_client.get_upcoming_schedules.assert_called_once_with(
        "basketball-men", "d1", 5
    )
    mock_schedule_helper.collect_games_from_schedules.assert_called_once()
    assert len(result) == 1


def test_clear_cache_delegates_to_client(basketball_service, mock_client):
    basketball_service.clear_cache()

    mock_client.clear_cache.assert_called_once()
