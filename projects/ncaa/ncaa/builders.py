from .casablanca_models import ScheduleResponse, ScoreboardResponse
from .config import get_today_date_string
from .constants import DEFAULT_DIVISION
from .interfaces import ICasablancaClient


class ScheduleQueryBuilder:
    def __init__(self, client: ICasablancaClient):
        self._client = client
        self._sport: str | None = None
        self._gender: str | None = None
        self._division: str = DEFAULT_DIVISION.value
        self._date: str | None = None
        self._days: int = 1

    def for_sport(self, sport: str) -> "ScheduleQueryBuilder":
        self._sport = sport
        return self

    def for_gender(self, gender: str) -> "ScheduleQueryBuilder":
        self._gender = gender
        return self

    def in_division(self, division: str) -> "ScheduleQueryBuilder":
        self._division = division
        return self

    def on_date(self, date: str) -> "ScheduleQueryBuilder":
        self._date = date
        return self

    def for_days(self, days: int) -> "ScheduleQueryBuilder":
        if days < 1:
            raise ValueError("Days must be at least 1")
        self._days = days
        return self

    def execute(self) -> list[ScheduleResponse]:
        if not self._sport:
            raise ValueError("Sport is required. Use for_sport() to set it.")

        if self._days > 1:
            return self._client.get_upcoming_schedules(
                self._sport, self._division, self._days
            )

        date = self._date or get_today_date_string()
        return [self._client.get_schedule(self._sport, self._division, date)]


class ScoreboardQueryBuilder:
    def __init__(self, client: ICasablancaClient):
        self._client = client
        self._gender: str | None = None
        self._division: str = DEFAULT_DIVISION.value
        self._date: str | None = None

    def for_gender(self, gender: str) -> "ScoreboardQueryBuilder":
        self._gender = gender
        return self

    def in_division(self, division: str) -> "ScoreboardQueryBuilder":
        self._division = division
        return self

    def on_date(self, date: str) -> "ScoreboardQueryBuilder":
        self._date = date
        return self

    def execute(self) -> ScoreboardResponse:
        if not self._gender:
            raise ValueError("Gender is required. Use for_gender() to set it.")

        if self._date:
            return self._client.get_scoreboard(self._gender, self._division, self._date)

        return self._client.get_todays_scoreboard(self._gender, self._division)
