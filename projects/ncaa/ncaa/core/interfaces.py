from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from ..api.models import GameWrapper, ScheduleResponse, ScoreboardResponse


@runtime_checkable
class IDataFetcher(Protocol):
    def get_scoreboard(
        self, gender: str, division: str, date: str
    ) -> ScoreboardResponse: ...

    def get_schedule(
        self, sport: str, division: str, date: str
    ) -> ScheduleResponse: ...

    def get_todays_scoreboard(
        self, gender: str, division: str
    ) -> ScoreboardResponse: ...

    def get_todays_schedule(self, sport: str, division: str) -> ScheduleResponse: ...

    def get_upcoming_schedules(
        self, sport: str, division: str, days: int
    ) -> list[ScheduleResponse]: ...


@runtime_checkable
class ICacheManager(Protocol):
    def clear_cache(self) -> None: ...

    def set_cache_duration(self, seconds: int) -> None: ...


@runtime_checkable
class ICasablancaClient(IDataFetcher, ICacheManager, Protocol):
    pass


@runtime_checkable
class IScheduleHelper(Protocol):
    def collect_games_from_schedules(
        self, schedules: list[ScheduleResponse]
    ) -> list[GameWrapper]: ...


@runtime_checkable
class IGameFilter(Protocol):
    def filter(self, games: list[GameWrapper]) -> list[GameWrapper]: ...


@runtime_checkable
class IGenderResolver(Protocol):
    def resolve(self, sport_name: str, text_gender) -> ...: ...


@runtime_checkable
class IHtmlFetcher(Protocol):
    def fetch(self, url: str) -> str: ...


@runtime_checkable
class IBasketballService(Protocol):
    def get_scoreboard(
        self, gender: str, date: str, division: str
    ) -> ScoreboardResponse: ...

    def get_todays_scoreboard(
        self, gender: str, division: str
    ) -> ScoreboardResponse: ...

    def get_schedule(
        self, gender: str, date: str, division: str
    ) -> ScheduleResponse: ...

    def get_todays_schedule(self, gender: str, division: str) -> ScheduleResponse: ...

    def get_upcoming_schedules(
        self, gender: str, division: str, days: int
    ) -> list[ScheduleResponse]: ...

    def get_games_by_filter(
        self, gender: str, division: str, game_filter: IGameFilter
    ) -> list[GameWrapper]: ...

    def get_live_games(self, gender: str, division: str) -> list[GameWrapper]: ...

    def get_upcoming_games(
        self, gender: str, division: str, days: int
    ) -> list[GameWrapper]: ...

    def clear_cache(self) -> None: ...


@runtime_checkable
class IScheduleService(Protocol):
    def get_schedule(
        self, sport: str, date: str, division: str
    ) -> ScheduleResponse: ...

    def get_todays_schedule(self, sport: str, division: str) -> ScheduleResponse: ...

    def get_upcoming_schedules(
        self, sport: str, division: str, days: int
    ) -> list[ScheduleResponse]: ...

    def get_upcoming_games(
        self, sport: str, division: str, days: int
    ) -> list[GameWrapper]: ...

    def get_football_schedule(self, date: str, division: str) -> ScheduleResponse: ...

    def get_soccer_schedule(
        self, gender: str, date: str, division: str
    ) -> ScheduleResponse: ...

    def clear_cache(self) -> None: ...
