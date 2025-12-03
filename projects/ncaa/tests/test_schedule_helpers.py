import pytest

from ncaa.casablanca_models import (
    Game,
    GameState,
    GameWrapper,
    ScheduleResponse,
    Team,
    TeamNames,
)
from ncaa.schedule_helpers import ScheduleHelper


@pytest.fixture
def team_names():
    return TeamNames(char6="DUKE", short="Duke", seo="duke", full="Duke")


@pytest.fixture
def sample_team(team_names):
    return Team(names=team_names, score=0, winner=None)


@pytest.fixture
def sample_game(sample_team):
    game = Game(
        url="http://example.com",
        startTimeEpoch=1234567890,
        gameState=GameState.SCHEDULED,
        home=sample_team,
        away=sample_team,
    )
    return GameWrapper(game=game)


def test_collect_games_from_single_schedule(sample_game):
    schedule = ScheduleResponse(games=[sample_game])
    helper = ScheduleHelper()

    result = helper.collect_games_from_schedules([schedule])

    assert len(result) == 1
    assert result[0] == sample_game


def test_collect_games_from_multiple_schedules(sample_game, sample_team):
    game2 = GameWrapper(
        game=Game(
            url="http://example2.com",
            startTimeEpoch=1234567891,
            gameState=GameState.SCHEDULED,
            home=sample_team,
            away=sample_team,
        )
    )

    schedule1 = ScheduleResponse(games=[sample_game])
    schedule2 = ScheduleResponse(games=[game2])
    helper = ScheduleHelper()

    result = helper.collect_games_from_schedules([schedule1, schedule2])

    assert len(result) == 2
    assert result[0] == sample_game
    assert result[1] == game2


def test_collect_games_returns_empty_list_for_empty_schedules():
    schedule = ScheduleResponse(games=[])
    helper = ScheduleHelper()

    result = helper.collect_games_from_schedules([schedule])

    assert len(result) == 0


def test_collect_games_returns_empty_list_for_no_schedules():
    helper = ScheduleHelper()

    result = helper.collect_games_from_schedules([])

    assert len(result) == 0


def test_collect_games_handles_schedule_with_multiple_games(sample_game, sample_team):
    game2 = GameWrapper(
        game=Game(
            url="http://example2.com",
            startTimeEpoch=1234567891,
            gameState=GameState.SCHEDULED,
            home=sample_team,
            away=sample_team,
        )
    )
    game3 = GameWrapper(
        game=Game(
            url="http://example3.com",
            startTimeEpoch=1234567892,
            gameState=GameState.SCHEDULED,
            home=sample_team,
            away=sample_team,
        )
    )

    schedule = ScheduleResponse(games=[sample_game, game2, game3])
    helper = ScheduleHelper()

    result = helper.collect_games_from_schedules([schedule])

    assert len(result) == 3


def test_static_method_can_be_called_without_instance(sample_game):
    schedule = ScheduleResponse(games=[sample_game])

    result = ScheduleHelper.collect_games_from_schedules([schedule])

    assert len(result) == 1
    assert result[0] == sample_game
