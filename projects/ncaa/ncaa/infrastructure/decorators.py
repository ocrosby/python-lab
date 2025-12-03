from datetime import datetime
from typing import Any

from ..api.models import ScheduleResponse, ScoreboardResponse
from ..core.constants import DEFAULT_CACHE_DURATION, DEFAULT_DIVISION
from ..core.interfaces import ICasablancaClient


class CachedCasablancaClient(ICasablancaClient):
    def __init__(
        self, client: ICasablancaClient, cache_duration: int = DEFAULT_CACHE_DURATION
    ):
        self._client = client
        self._cache: dict[str, tuple[dict[str, Any], float]] = {}
        self._cache_duration = cache_duration

    def _get_cache_key(self, endpoint_type: str, *args: Any) -> str:
        return f"{endpoint_type}_{'_'.join(str(arg) for arg in args)}"

    def _get_cached(self, cache_key: str) -> dict[str, Any] | None:
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if datetime.now().timestamp() - timestamp < self._cache_duration:
                return data
            del self._cache[cache_key]
        return None

    def _set_cache(self, cache_key: str, data: dict[str, Any]) -> None:
        self._cache[cache_key] = (data, datetime.now().timestamp())

    def get_scoreboard(
        self, gender: str, division: str, date: str
    ) -> ScoreboardResponse:
        cache_key = self._get_cache_key("scoreboard", gender, division, date)
        cached = self._get_cached(cache_key)
        if cached:
            return ScoreboardResponse(**cached)

        result = self._client.get_scoreboard(gender, division, date)
        self._set_cache(cache_key, result.model_dump())
        return result

    def get_schedule(self, sport: str, division: str, date: str) -> ScheduleResponse:
        cache_key = self._get_cache_key("schedule", sport, division, date)
        cached = self._get_cached(cache_key)
        if cached:
            return ScheduleResponse(**cached)

        result = self._client.get_schedule(sport, division, date)
        self._set_cache(cache_key, result.model_dump())
        return result

    def get_todays_scoreboard(
        self, gender: str, division: str = DEFAULT_DIVISION.value
    ) -> ScoreboardResponse:
        return self._client.get_todays_scoreboard(gender, division)

    def get_todays_schedule(
        self, sport: str, division: str = DEFAULT_DIVISION.value
    ) -> ScheduleResponse:
        return self._client.get_todays_schedule(sport, division)

    def get_upcoming_schedules(
        self, sport: str, division: str = DEFAULT_DIVISION.value, days: int = 7
    ) -> list[ScheduleResponse]:
        return self._client.get_upcoming_schedules(sport, division, days)

    def clear_cache(self) -> None:
        self._cache.clear()
        self._client.clear_cache()

    def set_cache_duration(self, seconds: int) -> None:
        self._cache_duration = seconds


class LoggingCasablancaClient(ICasablancaClient):
    def __init__(self, client: ICasablancaClient, logger: Any = None):
        self._client = client
        self._logger = logger

    def _log(self, message: str) -> None:
        if self._logger:
            self._logger.info(message)
        else:
            print(f"[LOG] {message}")

    def get_scoreboard(
        self, gender: str, division: str, date: str
    ) -> ScoreboardResponse:
        self._log(f"Fetching scoreboard: {gender}/{division}/{date}")
        result = self._client.get_scoreboard(gender, division, date)
        self._log(f"Fetched scoreboard with {len(result.games)} games")
        return result

    def get_schedule(self, sport: str, division: str, date: str) -> ScheduleResponse:
        self._log(f"Fetching schedule: {sport}/{division}/{date}")
        result = self._client.get_schedule(sport, division, date)
        self._log(f"Fetched schedule with {len(result.games)} games")
        return result

    def get_todays_scoreboard(
        self, gender: str, division: str = DEFAULT_DIVISION.value
    ) -> ScoreboardResponse:
        self._log(f"Fetching today's scoreboard: {gender}/{division}")
        return self._client.get_todays_scoreboard(gender, division)

    def get_todays_schedule(
        self, sport: str, division: str = DEFAULT_DIVISION.value
    ) -> ScheduleResponse:
        self._log(f"Fetching today's schedule: {sport}/{division}")
        return self._client.get_todays_schedule(sport, division)

    def get_upcoming_schedules(
        self, sport: str, division: str = DEFAULT_DIVISION.value, days: int = 7
    ) -> list[ScheduleResponse]:
        self._log(f"Fetching upcoming schedules: {sport}/{division} for {days} days")
        result = self._client.get_upcoming_schedules(sport, division, days)
        self._log(f"Fetched {len(result)} schedules")
        return result

    def clear_cache(self) -> None:
        self._log("Clearing cache")
        self._client.clear_cache()

    def set_cache_duration(self, seconds: int) -> None:
        self._log(f"Setting cache duration to {seconds} seconds")
        self._client.set_cache_duration(seconds)
