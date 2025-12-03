import pytest

from ncaa.api.builders import ScheduleQueryBuilder, ScoreboardQueryBuilder
from ncaa.api.models import ScheduleResponse, ScoreboardResponse


@pytest.fixture
def mock_client(mocker):
    from ncaa.api.client import CasablancaClient

    return mocker.Mock(spec=CasablancaClient)


@pytest.fixture
def sample_schedule():
    return ScheduleResponse(games=[])


@pytest.fixture
def sample_scoreboard():
    return ScoreboardResponse(games=[])


def test_schedule_query_builder_single_day(mock_client, sample_schedule):
    mock_client.get_schedule.return_value = sample_schedule
    builder = ScheduleQueryBuilder(mock_client)

    result = (
        builder.for_sport("basketball-men")
        .in_division("d1")
        .on_date("2024/03/15")
        .execute()
    )

    assert len(result) == 1
    assert result[0] == sample_schedule
    mock_client.get_schedule.assert_called_once_with(
        "basketball-men", "d1", "2024/03/15"
    )


def test_schedule_query_builder_multiple_days(mock_client, sample_schedule):
    mock_client.get_upcoming_schedules.return_value = [
        sample_schedule,
        sample_schedule,
        sample_schedule,
    ]
    builder = ScheduleQueryBuilder(mock_client)

    result = builder.for_sport("basketball-men").in_division("d1").for_days(3).execute()

    assert len(result) == 3
    mock_client.get_upcoming_schedules.assert_called_once_with(
        "basketball-men", "d1", 3
    )


def test_schedule_query_builder_requires_sport(mock_client):
    builder = ScheduleQueryBuilder(mock_client)

    with pytest.raises(ValueError, match="Sport is required"):
        builder.in_division("d1").execute()


def test_schedule_query_builder_validates_days(mock_client):
    builder = ScheduleQueryBuilder(mock_client)

    with pytest.raises(ValueError, match="Days must be at least 1"):
        builder.for_sport("basketball-men").for_days(0)


def test_scoreboard_query_builder_with_date(mock_client, sample_scoreboard):
    mock_client.get_scoreboard.return_value = sample_scoreboard
    builder = ScoreboardQueryBuilder(mock_client)

    result = builder.for_gender("men").in_division("d1").on_date("2024/03/15").execute()

    assert result == sample_scoreboard
    mock_client.get_scoreboard.assert_called_once_with("men", "d1", "2024/03/15")


def test_scoreboard_query_builder_today(mock_client, sample_scoreboard):
    mock_client.get_todays_scoreboard.return_value = sample_scoreboard
    builder = ScoreboardQueryBuilder(mock_client)

    result = builder.for_gender("men").in_division("d1").execute()

    assert result == sample_scoreboard
    mock_client.get_todays_scoreboard.assert_called_once_with("men", "d1")


def test_scoreboard_query_builder_requires_gender(mock_client):
    builder = ScoreboardQueryBuilder(mock_client)

    with pytest.raises(ValueError, match="Gender is required"):
        builder.in_division("d1").execute()
