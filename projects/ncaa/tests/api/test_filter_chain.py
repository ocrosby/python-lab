import pytest

from ncaa.api.filters import (
    ConferenceFilter,
    FilterChain,
    LiveGameFilter,
    TeamFilter,
)
from ncaa.api.models import (
    Conference,
    Game,
    GameState,
    GameWrapper,
    Team,
    TeamNames,
)


@pytest.fixture
def sample_live_game():
    return GameWrapper(
        game=Game(
            url="/game/123",
            startTimeEpoch=1710518400,
            gameState=GameState.IN,
            currentPeriod=1,
            home=Team(
                names=TeamNames(
                    char6="DUKE",
                    short="Duke",
                    seo="duke",
                    full="Duke University",
                ),
                score=45,
                conferences=[Conference(conferenceName="ACC", conferenceSeo="acc")],
            ),
            away=Team(
                names=TeamNames(
                    char6="UNC",
                    short="North Carolina",
                    seo="north-carolina",
                    full="University of North Carolina",
                ),
                score=42,
                conferences=[Conference(conferenceName="ACC", conferenceSeo="acc")],
            ),
        )
    )


@pytest.fixture
def sample_scheduled_game():
    return GameWrapper(
        game=Game(
            url="/game/456",
            startTimeEpoch=1710618400,
            gameState=GameState.PRE,
            currentPeriod=0,
            home=Team(
                names=TeamNames(
                    char6="VILL",
                    short="Villanova",
                    seo="villanova",
                    full="Villanova University",
                ),
                score=0,
                conferences=[
                    Conference(conferenceName="Big East", conferenceSeo="big-east")
                ],
            ),
            away=Team(
                names=TeamNames(
                    char6="GTOWN",
                    short="Georgetown",
                    seo="georgetown",
                    full="Georgetown University",
                ),
                score=0,
                conferences=[
                    Conference(conferenceName="Big East", conferenceSeo="big-east")
                ],
            ),
        )
    )


def test_filter_chain_single_filter(sample_live_game, sample_scheduled_game):
    games = [sample_live_game, sample_scheduled_game]
    chain = FilterChain().add_filter(LiveGameFilter())

    result = chain.filter(games)

    assert len(result) == 1
    assert result[0].game.gameState == GameState.IN


def test_filter_chain_multiple_filters(sample_live_game):
    games = [sample_live_game]
    chain = FilterChain().add_filter(LiveGameFilter()).add_filter(TeamFilter("Duke"))

    result = chain.filter(games)

    assert len(result) == 1
    assert "Duke" in result[0].game.home.names.full


def test_filter_chain_filters_out_all(sample_scheduled_game):
    games = [sample_scheduled_game]
    chain = FilterChain().add_filter(LiveGameFilter()).add_filter(TeamFilter("Duke"))

    result = chain.filter(games)

    assert len(result) == 0


def test_team_filter_matches_home_team(sample_live_game):
    games = [sample_live_game]
    team_filter = TeamFilter("Duke")

    result = team_filter.filter(games)

    assert len(result) == 1


def test_team_filter_matches_away_team(sample_live_game):
    games = [sample_live_game]
    team_filter = TeamFilter("North Carolina")

    result = team_filter.filter(games)

    assert len(result) == 1


def test_team_filter_case_insensitive(sample_live_game):
    games = [sample_live_game]
    team_filter = TeamFilter("duke")

    result = team_filter.filter(games)

    assert len(result) == 1


def test_conference_filter(sample_live_game, sample_scheduled_game):
    games = [sample_live_game, sample_scheduled_game]
    conference_filter = ConferenceFilter("ACC")

    result = conference_filter.filter(games)

    assert len(result) == 1
    assert any(c.conferenceName == "ACC" for c in result[0].game.home.conferences)


def test_filter_chain_empty():
    games = []
    chain = FilterChain().add_filter(LiveGameFilter())

    result = chain.filter(games)

    assert len(result) == 0
