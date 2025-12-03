import requests

from .casablanca_models import ScheduleResponse, ScoreboardResponse
from .config import (
    CASABLANCA_SCHEDULE_BASE_URL,
    CASABLANCA_SCOREBOARD_BASE_URL,
    build_schedule_url,
    build_scoreboard_url,
    format_date_offset,
    get_today_date_string,
)
from .constants import DEFAULT_DIVISION, DEFAULT_TIMEOUT


class CasablancaClientError(RuntimeError):
    pass


class CasablancaClient:
    def __init__(
        self,
        scoreboard_base_url: str = CASABLANCA_SCOREBOARD_BASE_URL,
        schedule_base_url: str = CASABLANCA_SCHEDULE_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.scoreboard_base_url = scoreboard_base_url
        self.schedule_base_url = schedule_base_url
        self.timeout = timeout

    def _fetch_json(self, url: str) -> dict:
        try:
            resp = requests.get(url, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as exc:
            raise CasablancaClientError(f"Error fetching {url}: {exc}") from exc

    def get_scoreboard(
        self, gender: str, division: str, date: str
    ) -> ScoreboardResponse:
        url = build_scoreboard_url(self.scoreboard_base_url, gender, division, date)
        data = self._fetch_json(url)
        return ScoreboardResponse(**data)

    def get_schedule(self, sport: str, division: str, date: str) -> ScheduleResponse:
        url = build_schedule_url(self.schedule_base_url, sport, division, date)
        data = self._fetch_json(url)
        return ScheduleResponse(**data)

    def get_todays_scoreboard(
        self, gender: str, division: str = DEFAULT_DIVISION.value
    ) -> ScoreboardResponse:
        today = get_today_date_string()
        return self.get_scoreboard(gender, division, today)

    def get_todays_schedule(
        self, sport: str, division: str = DEFAULT_DIVISION.value
    ) -> ScheduleResponse:
        today = get_today_date_string()
        return self.get_schedule(sport, division, today)

    def get_upcoming_schedules(
        self, sport: str, division: str = DEFAULT_DIVISION.value, days: int = 7
    ) -> list[ScheduleResponse]:
        schedules = []
        for i in range(days):
            date = format_date_offset(i)
            try:
                schedule = self.get_schedule(sport, division, date)
                schedules.append(schedule)
            except CasablancaClientError:
                continue
        return schedules

    def clear_cache(self) -> None:
        pass

    def set_cache_duration(self, seconds: int) -> None:
        pass
