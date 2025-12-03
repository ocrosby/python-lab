import pytest

from ncaa.api.filters import (
    CompletedGameFilter,
    LiveGameFilter,
    ScheduledGameFilter,
)
from ncaa.api.models import (
    Game,
    GameState,
    GameWrapper,
    Team,
    TeamNames,
)


@pytest.fixture
def team_names():
    return TeamNames(char6="DUKE", short="Duke", seo="duke", full="Duke")


@pytest.fixture
def sample_team(team_names):
    return Team(names=team_names, score=70, winner=True)


def create_game_wrapper(game_state: GameState, team) -> GameWrapper:
    game = Game(
        url="http://example.com",
        startTimeEpoch=1234567890,
        gameState=game_state,
        home=team,
        away=team,
    )
    return GameWrapper(game=game)


def test_live_game_filter_filters_in_progress_games(sample_team):
    games = [
        create_game_wrapper(GameState.IN, sample_team),
        create_game_wrapper(GameState.PRE, sample_team),
        create_game_wrapper(GameState.POST, sample_team),
    ]

    filter = LiveGameFilter()
    result = filter.filter(games)

    assert len(result) == 1
    assert result[0].game.gameState == GameState.IN


def test_live_game_filter_filters_inprogress_state_games(sample_team):
    games = [
        create_game_wrapper(GameState.INPROGRESS, sample_team),
        create_game_wrapper(GameState.SCHEDULED, sample_team),
        create_game_wrapper(GameState.FINAL, sample_team),
    ]

    filter = LiveGameFilter()
    result = filter.filter(games)

    assert len(result) == 1
    assert result[0].game.gameState == GameState.INPROGRESS


def test_live_game_filter_returns_both_live_states(sample_team):
    games = [
        create_game_wrapper(GameState.IN, sample_team),
        create_game_wrapper(GameState.INPROGRESS, sample_team),
        create_game_wrapper(GameState.PRE, sample_team),
    ]

    filter = LiveGameFilter()
    result = filter.filter(games)

    assert len(result) == 2


def test_live_game_filter_returns_empty_when_no_live_games(sample_team):
    games = [
        create_game_wrapper(GameState.PRE, sample_team),
        create_game_wrapper(GameState.POST, sample_team),
    ]

    filter = LiveGameFilter()
    result = filter.filter(games)

    assert len(result) == 0


def test_completed_game_filter_filters_post_games(sample_team):
    games = [
        create_game_wrapper(GameState.POST, sample_team),
        create_game_wrapper(GameState.PRE, sample_team),
        create_game_wrapper(GameState.IN, sample_team),
    ]

    filter = CompletedGameFilter()
    result = filter.filter(games)

    assert len(result) == 1
    assert result[0].game.gameState == GameState.POST


def test_completed_game_filter_filters_final_games(sample_team):
    games = [
        create_game_wrapper(GameState.FINAL, sample_team),
        create_game_wrapper(GameState.SCHEDULED, sample_team),
        create_game_wrapper(GameState.INPROGRESS, sample_team),
    ]

    filter = CompletedGameFilter()
    result = filter.filter(games)

    assert len(result) == 1
    assert result[0].game.gameState == GameState.FINAL


def test_completed_game_filter_returns_both_completed_states(sample_team):
    games = [
        create_game_wrapper(GameState.POST, sample_team),
        create_game_wrapper(GameState.FINAL, sample_team),
        create_game_wrapper(GameState.IN, sample_team),
    ]

    filter = CompletedGameFilter()
    result = filter.filter(games)

    assert len(result) == 2


def test_completed_game_filter_returns_empty_when_no_completed_games(sample_team):
    games = [
        create_game_wrapper(GameState.PRE, sample_team),
        create_game_wrapper(GameState.IN, sample_team),
    ]

    filter = CompletedGameFilter()
    result = filter.filter(games)

    assert len(result) == 0


def test_scheduled_game_filter_filters_pre_games(sample_team):
    games = [
        create_game_wrapper(GameState.PRE, sample_team),
        create_game_wrapper(GameState.IN, sample_team),
        create_game_wrapper(GameState.POST, sample_team),
    ]

    filter = ScheduledGameFilter()
    result = filter.filter(games)

    assert len(result) == 1
    assert result[0].game.gameState == GameState.PRE


def test_scheduled_game_filter_filters_scheduled_games(sample_team):
    games = [
        create_game_wrapper(GameState.SCHEDULED, sample_team),
        create_game_wrapper(GameState.INPROGRESS, sample_team),
        create_game_wrapper(GameState.FINAL, sample_team),
    ]

    filter = ScheduledGameFilter()
    result = filter.filter(games)

    assert len(result) == 1
    assert result[0].game.gameState == GameState.SCHEDULED


def test_scheduled_game_filter_returns_both_scheduled_states(sample_team):
    games = [
        create_game_wrapper(GameState.PRE, sample_team),
        create_game_wrapper(GameState.SCHEDULED, sample_team),
        create_game_wrapper(GameState.POST, sample_team),
    ]

    filter = ScheduledGameFilter()
    result = filter.filter(games)

    assert len(result) == 2


def test_scheduled_game_filter_returns_empty_when_no_scheduled_games(sample_team):
    games = [
        create_game_wrapper(GameState.IN, sample_team),
        create_game_wrapper(GameState.POST, sample_team),
    ]

    filter = ScheduledGameFilter()
    result = filter.filter(games)

    assert len(result) == 0


def test_scheduled_game_filter_excludes_cancelled_games(sample_team):
    games = [
        create_game_wrapper(GameState.PRE, sample_team),
        create_game_wrapper(GameState.CANCELLED, sample_team),
    ]

    filter = ScheduledGameFilter()
    result = filter.filter(games)

    assert len(result) == 1
    assert result[0].game.gameState == GameState.PRE


def test_scheduled_game_filter_excludes_postponed_games(sample_team):
    games = [
        create_game_wrapper(GameState.SCHEDULED, sample_team),
        create_game_wrapper(GameState.POSTPONED, sample_team),
    ]

    filter = ScheduledGameFilter()
    result = filter.filter(games)

    assert len(result) == 1
    assert result[0].game.gameState == GameState.SCHEDULED
