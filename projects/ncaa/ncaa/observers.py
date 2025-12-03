from abc import ABC, abstractmethod
from typing import Any

from .casablanca_models import ScheduleResponse, ScoreboardResponse
from .constants import DEFAULT_DIVISION
from .interfaces import ICasablancaClient


class DataObserver(ABC):
    @abstractmethod
    def on_data_update(self, data_type: str, data: Any) -> None:
        pass


class ObservableCasablancaClient(ICasablancaClient):
    def __init__(self, client: ICasablancaClient):
        self._client = client
        self._observers: list[DataObserver] = []

    def attach(self, observer: DataObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: DataObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify(self, data_type: str, data: Any) -> None:
        for observer in self._observers:
            observer.on_data_update(data_type, data)

    def get_scoreboard(
        self, gender: str, division: str, date: str
    ) -> ScoreboardResponse:
        result = self._client.get_scoreboard(gender, division, date)
        self._notify("scoreboard", result)
        return result

    def get_schedule(self, sport: str, division: str, date: str) -> ScheduleResponse:
        result = self._client.get_schedule(sport, division, date)
        self._notify("schedule", result)
        return result

    def get_todays_scoreboard(
        self, gender: str, division: str = DEFAULT_DIVISION.value
    ) -> ScoreboardResponse:
        result = self._client.get_todays_scoreboard(gender, division)
        self._notify("scoreboard_today", result)
        return result

    def get_todays_schedule(
        self, sport: str, division: str = DEFAULT_DIVISION.value
    ) -> ScheduleResponse:
        result = self._client.get_todays_schedule(sport, division)
        self._notify("schedule_today", result)
        return result

    def get_upcoming_schedules(
        self, sport: str, division: str = DEFAULT_DIVISION.value, days: int = 7
    ) -> list[ScheduleResponse]:
        result = self._client.get_upcoming_schedules(sport, division, days)
        self._notify("schedules_upcoming", result)
        return result

    def clear_cache(self) -> None:
        self._client.clear_cache()
        self._notify("cache_cleared", None)

    def set_cache_duration(self, seconds: int) -> None:
        self._client.set_cache_duration(seconds)
        self._notify("cache_duration_changed", seconds)


class LoggingObserver(DataObserver):
    def __init__(self, logger: Any = None):
        self._logger = logger

    def on_data_update(self, data_type: str, data: Any) -> None:
        if self._logger:
            self._logger.info(f"Data update: {data_type}")
        else:
            print(f"[OBSERVER] Data update: {data_type}")


class CacheMetricsObserver(DataObserver):
    def __init__(self):
        self.requests: dict[str, int] = {}

    def on_data_update(self, data_type: str, data: Any) -> None:
        self.requests[data_type] = self.requests.get(data_type, 0) + 1

    def get_metrics(self) -> dict[str, int]:
        return self.requests.copy()

    def reset_metrics(self) -> None:
        self.requests.clear()
