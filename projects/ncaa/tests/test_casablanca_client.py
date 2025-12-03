import pytest
import requests

from ncaa.casablanca_client import CasablancaClient, CasablancaClientError
from ncaa.casablanca_models import ScheduleResponse, ScoreboardResponse


@pytest.fixture
def mock_scoreboard_data():
    return {
        "games": [
            {
                "game": {
                    "url": "/game/1234567",
                    "startTimeEpoch": 1710518400,
                    "gameState": "pre",
                    "network": "ESPN",
                    "currentPeriod": 0,
                    "contestClock": None,
                    "home": {
                        "names": {
                            "char6": "DUKE",
                            "short": "Duke",
                            "seo": "duke",
                            "full": "Duke University",
                        },
                        "score": 0,
                        "conferences": [],
                    },
                    "away": {
                        "names": {
                            "char6": "UNC",
                            "short": "North Carolina",
                            "seo": "north-carolina",
                            "full": "University of North Carolina",
                        },
                        "score": 0,
                        "conferences": [],
                    },
                }
            }
        ]
    }


@pytest.fixture
def mock_schedule_data():
    return {
        "inputMD5Sum": "946b0d7ecce3877d6cd036a19daf95ed",
        "instanceId": "52aa051f77b7475da1baba2df45d5e98",
        "updated_at": "11-24-2024 15:30:45",
        "hideRank": False,
        "games": [
            {
                "game": {
                    "gameID": "3146430",
                    "startTime": "12:00PM ET",
                    "startDate": "11-24-2024",
                    "startTimeEpoch": "1700931600",
                    "gameState": "scheduled",
                    "url": "/game/3146430",
                    "network": "ESPN+",
                    "venue": "Michigan Stadium",
                    "location": "Ann Arbor, MI",
                    "currentPeriod": 0,
                    "home": {
                        "names": {
                            "full": "University of Michigan",
                            "short": "Michigan",
                            "seo": "michigan",
                            "char6": "MICH",
                        },
                        "score": 0,
                        "conferences": [],
                    },
                    "away": {
                        "names": {
                            "full": "The Ohio State University",
                            "short": "Ohio St.",
                            "seo": "ohio-st",
                            "char6": "OHIOST",
                        },
                        "score": 0,
                        "conferences": [],
                    },
                }
            }
        ],
    }


@pytest.fixture
def client():
    return CasablancaClient()


def test_init():
    client = CasablancaClient()
    assert client.scoreboard_base_url == "https://data.ncaa.com/casablanca/scoreboard"
    assert client.schedule_base_url == "https://data.ncaa.com/casablanca/schedule"
    assert client.timeout == 10


def test_init_with_custom_params():
    client = CasablancaClient(
        scoreboard_base_url="https://custom.com/scoreboard",
        schedule_base_url="https://custom.com/schedule",
        timeout=20,
    )
    assert client.scoreboard_base_url == "https://custom.com/scoreboard"
    assert client.schedule_base_url == "https://custom.com/schedule"
    assert client.timeout == 20


def test_get_scoreboard(mocker, client, mock_scoreboard_data):
    mock_response = mocker.Mock()
    mock_response.json.return_value = mock_scoreboard_data
    mock_response.raise_for_status.return_value = None
    mock_get = mocker.patch(
        "ncaa.casablanca_client.requests.get", return_value=mock_response
    )

    result = client.get_scoreboard("men", "d1", "2024/03/15")

    assert isinstance(result, ScoreboardResponse)
    assert len(result.games) == 1
    assert result.games[0].game.home.names.short == "Duke"
    mock_get.assert_called_once()


def test_get_schedule(mocker, client, mock_schedule_data):
    mock_response = mocker.Mock()
    mock_response.json.return_value = mock_schedule_data
    mock_response.raise_for_status.return_value = None
    mock_get = mocker.patch(
        "ncaa.casablanca_client.requests.get", return_value=mock_response
    )

    result = client.get_schedule("basketball-men", "d1", "2024/03/15")

    assert isinstance(result, ScheduleResponse)
    assert len(result.games) == 1
    assert result.games[0].game.venue == "Michigan Stadium"
    mock_get.assert_called_once()


def test_fetch_json_error(mocker, client):
    mocker.patch(
        "ncaa.casablanca_client.requests.get",
        side_effect=requests.RequestException("Network error"),
    )

    with pytest.raises(CasablancaClientError):
        client.get_scoreboard("men", "d1", "2024/03/15")


def test_no_caching_in_base_client(mocker, client, mock_scoreboard_data):
    mock_response = mocker.Mock()
    mock_response.json.return_value = mock_scoreboard_data
    mock_response.raise_for_status.return_value = None
    mock_get = mocker.patch(
        "ncaa.casablanca_client.requests.get", return_value=mock_response
    )

    result1 = client.get_scoreboard("men", "d1", "2024/03/15")
    result2 = client.get_scoreboard("men", "d1", "2024/03/15")

    assert mock_get.call_count == 2
    assert (
        result1.games[0].game.home.names.short == result2.games[0].game.home.names.short
    )


def test_clear_cache_is_noop(client):
    client.clear_cache()


def test_set_cache_duration_is_noop(client):
    client.set_cache_duration(600)


def test_get_todays_scoreboard(mocker, client, mock_scoreboard_data):
    mock_response = mocker.Mock()
    mock_response.json.return_value = mock_scoreboard_data
    mock_response.raise_for_status.return_value = None
    mock_get = mocker.patch(
        "ncaa.casablanca_client.requests.get", return_value=mock_response
    )

    result = client.get_todays_scoreboard("men", "d1")

    assert isinstance(result, ScoreboardResponse)
    mock_get.assert_called_once()


def test_get_upcoming_schedules(mocker, client, mock_schedule_data):
    mock_response = mocker.Mock()
    mock_response.json.return_value = mock_schedule_data
    mock_response.raise_for_status.return_value = None
    mock_get = mocker.patch(
        "ncaa.casablanca_client.requests.get", return_value=mock_response
    )

    results = client.get_upcoming_schedules("basketball-men", "d1", 3)

    assert len(results) == 3
    assert all(isinstance(r, ScheduleResponse) for r in results)
    assert mock_get.call_count == 3
