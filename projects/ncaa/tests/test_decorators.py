import pytest

from ncaa.casablanca_models import ScheduleResponse, ScoreboardResponse
from ncaa.decorators import CachedCasablancaClient, LoggingCasablancaClient


@pytest.fixture
def mock_client(mocker):
    from ncaa.casablanca_client import CasablancaClient

    return mocker.Mock(spec=CasablancaClient)


@pytest.fixture
def sample_scoreboard():
    return ScoreboardResponse(games=[])


@pytest.fixture
def sample_schedule():
    return ScheduleResponse(games=[])


def test_cached_client_caches_scoreboard(mock_client, sample_scoreboard):
    mock_client.get_scoreboard.return_value = sample_scoreboard
    cached_client = CachedCasablancaClient(mock_client)

    result1 = cached_client.get_scoreboard("men", "d1", "2024/03/15")
    result2 = cached_client.get_scoreboard("men", "d1", "2024/03/15")

    assert result1 == sample_scoreboard
    assert result2 == sample_scoreboard
    mock_client.get_scoreboard.assert_called_once()


def test_cached_client_caches_schedule(mock_client, sample_schedule):
    mock_client.get_schedule.return_value = sample_schedule
    cached_client = CachedCasablancaClient(mock_client)

    result1 = cached_client.get_schedule("basketball-men", "d1", "2024/03/15")
    result2 = cached_client.get_schedule("basketball-men", "d1", "2024/03/15")

    assert result1 == sample_schedule
    assert result2 == sample_schedule
    mock_client.get_schedule.assert_called_once()


def test_cached_client_different_keys_dont_share_cache(mock_client, sample_scoreboard):
    mock_client.get_scoreboard.return_value = sample_scoreboard
    cached_client = CachedCasablancaClient(mock_client)

    cached_client.get_scoreboard("men", "d1", "2024/03/15")
    cached_client.get_scoreboard("women", "d1", "2024/03/15")

    assert mock_client.get_scoreboard.call_count == 2


def test_cached_client_clear_cache(mock_client, sample_scoreboard):
    mock_client.get_scoreboard.return_value = sample_scoreboard
    cached_client = CachedCasablancaClient(mock_client)

    cached_client.get_scoreboard("men", "d1", "2024/03/15")
    cached_client.clear_cache()
    cached_client.get_scoreboard("men", "d1", "2024/03/15")

    assert mock_client.get_scoreboard.call_count == 2


def test_cached_client_delegates_to_wrapped_client(mock_client, sample_scoreboard):
    mock_client.get_todays_scoreboard.return_value = sample_scoreboard
    cached_client = CachedCasablancaClient(mock_client)

    result = cached_client.get_todays_scoreboard("men", "d1")

    assert result == sample_scoreboard
    mock_client.get_todays_scoreboard.assert_called_once_with("men", "d1")


def test_logging_client_logs_operations(mock_client, sample_scoreboard, capsys):
    mock_client.get_scoreboard.return_value = sample_scoreboard
    logging_client = LoggingCasablancaClient(mock_client)

    logging_client.get_scoreboard("men", "d1", "2024/03/15")

    captured = capsys.readouterr()
    assert "Fetching scoreboard" in captured.out
    assert "Fetched scoreboard with 0 games" in captured.out


def test_logging_client_delegates_to_wrapped_client(mock_client, sample_scoreboard):
    mock_client.get_scoreboard.return_value = sample_scoreboard
    logging_client = LoggingCasablancaClient(mock_client)

    result = logging_client.get_scoreboard("men", "d1", "2024/03/15")

    assert result == sample_scoreboard
    mock_client.get_scoreboard.assert_called_once_with("men", "d1", "2024/03/15")
