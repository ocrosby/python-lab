import pytest

from ncaa.casablanca_client import CasablancaClient
from ncaa.casablanca_models import (
    Game,
    GameState,
    GameWrapper,
    ScoreboardResponse,
    Team,
    TeamNames,
)
from ncaa.casablanca_service import CasablancaService


@pytest.fixture
def mock_client(mocker):
    return mocker.Mock(spec=CasablancaClient)


@pytest.fixture
def service(mock_client):
    return CasablancaService(client=mock_client)


@pytest.fixture
def sample_game():
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
                conferences=[],
            ),
            away=Team(
                names=TeamNames(
                    char6="UNC",
                    short="North Carolina",
                    seo="north-carolina",
                    full="University of North Carolina",
                ),
                score=42,
                conferences=[],
            ),
        )
    )


def test_init_with_client(mock_client):
    service = CasablancaService(client=mock_client)
    assert service.basketball.client == mock_client
    assert service.schedule.client == mock_client


def test_init_without_client():
    from ncaa.casablanca_service import get_casablanca_service

    service = get_casablanca_service()
    assert isinstance(service.basketball.client, CasablancaClient)
    assert isinstance(service.schedule.client, CasablancaClient)


def test_get_basketball_scoreboard_men(service, mock_client):
    mock_response = ScoreboardResponse(games=[])
    mock_client.get_scoreboard.return_value = mock_response

    result = service.get_basketball_scoreboard("men", "2024/03/15")

    assert result == mock_response
    mock_client.get_scoreboard.assert_called_once_with("men", "d1", "2024/03/15")


def test_get_basketball_scoreboard_women(service, mock_client):
    mock_response = ScoreboardResponse(games=[])
    mock_client.get_scoreboard.return_value = mock_response

    result = service.get_basketball_scoreboard("women", "2024/03/15", "d2")

    assert result == mock_response
    mock_client.get_scoreboard.assert_called_once_with("women", "d2", "2024/03/15")


def test_get_todays_basketball_games_men(service, mock_client):
    mock_response = ScoreboardResponse(games=[])
    mock_client.get_todays_scoreboard.return_value = mock_response

    result = service.get_todays_basketball_games("men")

    assert result == mock_response
    mock_client.get_todays_scoreboard.assert_called_once_with("men", "d1")


def test_get_todays_basketball_games_women(service, mock_client):
    mock_response = ScoreboardResponse(games=[])
    mock_client.get_todays_scoreboard.return_value = mock_response

    result = service.get_todays_basketball_games("women", "d3")

    assert result == mock_response
    mock_client.get_todays_scoreboard.assert_called_once_with("women", "d3")


def test_clear_cache(service, mock_client):
    service.clear_cache()
    assert mock_client.clear_cache.call_count == 1
