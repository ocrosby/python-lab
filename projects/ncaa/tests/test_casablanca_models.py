import pytest

from ncaa.api.models import (
    Conference,
    Game,
    GameState,
    GameWrapper,
    ScheduleResponse,
    ScoreboardResponse,
    Team,
    TeamNames,
    VideoState,
    Weather,
)


def test_game_state_has_pre_state():
    assert GameState.PRE == "pre"


def test_game_state_has_in_state():
    assert GameState.IN == "in"


def test_game_state_has_post_state():
    assert GameState.POST == "post"


def test_game_state_has_scheduled_state():
    assert GameState.SCHEDULED == "scheduled"


def test_game_state_has_inprogress_state():
    assert GameState.INPROGRESS == "inprogress"


def test_game_state_has_final_state():
    assert GameState.FINAL == "final"


def test_game_state_has_postponed_state():
    assert GameState.POSTPONED == "postponed"


def test_game_state_has_cancelled_state():
    assert GameState.CANCELLED == "cancelled"


def test_video_state_has_available_state():
    assert VideoState.AVAILABLE == "available"


def test_video_state_has_unavailable_state():
    assert VideoState.UNAVAILABLE == "unavailable"


def test_video_state_has_archived_state():
    assert VideoState.ARCHIVED == "archived"


def test_team_names_creates_with_all_fields():
    names = TeamNames(char6="DUKE", short="Duke", seo="duke", full="Duke Blue Devils")

    assert names.char6 == "DUKE"
    assert names.short == "Duke"
    assert names.seo == "duke"
    assert names.full == "Duke Blue Devils"


def test_conference_creates_with_required_field():
    conf = Conference(conferenceName="ACC")

    assert conf.conferenceName == "ACC"
    assert conf.conferenceSeo is None


def test_conference_creates_with_optional_field():
    conf = Conference(conferenceName="ACC", conferenceSeo="acc")

    assert conf.conferenceName == "ACC"
    assert conf.conferenceSeo == "acc"


@pytest.fixture
def team_names():
    return TeamNames(char6="DUKE", short="Duke", seo="duke", full="Duke")


def test_team_creates_with_required_fields(team_names):
    team = Team(names=team_names, score=70)

    assert team.names == team_names
    assert team.score == 70
    assert team.winner is None
    assert team.rank is None


def test_team_creates_with_all_fields(team_names):
    conf = Conference(conferenceName="ACC")
    team = Team(
        names=team_names,
        score=70,
        winner=True,
        rank=5,
        seed=2,
        description="Blue Devils",
        record="20-5",
        conferences=[conf],
    )

    assert team.winner is True
    assert team.rank == 5
    assert team.seed == 2
    assert team.description == "Blue Devils"
    assert team.record == "20-5"
    assert len(team.conferences) == 1


def test_team_conferences_defaults_to_empty_list(team_names):
    team = Team(names=team_names, score=70)

    assert team.conferences == []


def test_weather_creates_with_all_none():
    weather = Weather()

    assert weather.temperature is None
    assert weather.condition is None
    assert weather.wind is None
    assert weather.humidity is None
    assert weather.precipitation is None


def test_weather_creates_with_all_fields():
    weather = Weather(
        temperature="72°F",
        condition="Sunny",
        wind="5 mph",
        humidity="45%",
        precipitation="0%",
    )

    assert weather.temperature == "72°F"
    assert weather.condition == "Sunny"
    assert weather.wind == "5 mph"
    assert weather.humidity == "45%"
    assert weather.precipitation == "0%"


@pytest.fixture
def home_team(team_names):
    return Team(names=team_names, score=70, winner=True)


@pytest.fixture
def away_team(team_names):
    return Team(names=team_names, score=65, winner=False)


def test_game_creates_with_required_fields(home_team, away_team):
    game = Game(
        url="http://example.com",
        startTimeEpoch=1234567890,
        gameState=GameState.FINAL,
        home=home_team,
        away=away_team,
    )

    assert game.url == "http://example.com"
    assert game.startTimeEpoch == 1234567890
    assert game.gameState == GameState.FINAL
    assert game.home == home_team
    assert game.away == away_team
    assert game.currentPeriod == 0


def test_game_creates_with_all_fields(home_team, away_team):
    weather = Weather(temperature="72°F")
    game = Game(
        gameID="12345",
        url="http://example.com",
        startTimeEpoch=1234567890,
        startTime="7:00 PM",
        startDate="2024/03/15",
        gameState=GameState.IN,
        network="ESPN",
        venue="Cameron Indoor",
        location="Durham, NC",
        attendance=9314,
        liveVideoEnabled=True,
        videoState=VideoState.AVAILABLE,
        bracketRound="Elite Eight",
        bracketId="bracket-123",
        bracketRegion="East",
        currentPeriod=2,
        contestClock="15:32",
        title="NCAA Tournament",
        contestName="Elite Eight",
        finalMessage="Final",
        weather=weather,
        home=home_team,
        away=away_team,
    )

    assert game.gameID == "12345"
    assert game.network == "ESPN"
    assert game.venue == "Cameron Indoor"
    assert game.attendance == 9314
    assert game.currentPeriod == 2
    assert game.contestClock == "15:32"
    assert game.weather == weather


def test_game_wrapper_wraps_game(team_names):
    team = Team(names=team_names, score=70)
    game = Game(
        url="http://example.com",
        startTimeEpoch=1234567890,
        gameState=GameState.FINAL,
        home=team,
        away=team,
    )

    wrapper = GameWrapper(game=game)

    assert wrapper.game == game


def test_scoreboard_response_creates_with_empty_games():
    scoreboard = ScoreboardResponse()

    assert scoreboard.games == []


def test_scoreboard_response_creates_with_games(team_names):
    team = Team(names=team_names, score=70)
    game = Game(
        url="http://example.com",
        startTimeEpoch=1234567890,
        gameState=GameState.FINAL,
        home=team,
        away=team,
    )
    wrapper = GameWrapper(game=game)

    scoreboard = ScoreboardResponse(games=[wrapper])

    assert len(scoreboard.games) == 1
    assert scoreboard.games[0] == wrapper


def test_schedule_response_creates_with_empty_games():
    schedule = ScheduleResponse()

    assert schedule.games == []
    assert schedule.inputMD5Sum is None
    assert schedule.instanceId is None
    assert schedule.updated_at is None
    assert schedule.hideRank is None


def test_schedule_response_creates_with_all_fields(team_names):
    team = Team(names=team_names, score=0)
    game = Game(
        url="http://example.com",
        startTimeEpoch=1234567890,
        gameState=GameState.SCHEDULED,
        home=team,
        away=team,
    )
    wrapper = GameWrapper(game=game)

    schedule = ScheduleResponse(
        inputMD5Sum="abc123",
        instanceId="inst-456",
        updated_at="2024-03-15T10:00:00Z",
        hideRank=True,
        games=[wrapper],
    )

    assert schedule.inputMD5Sum == "abc123"
    assert schedule.instanceId == "inst-456"
    assert schedule.updated_at == "2024-03-15T10:00:00Z"
    assert schedule.hideRank is True
    assert len(schedule.games) == 1
