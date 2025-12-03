from typing import Any

from .casablanca_client import CasablancaClient
from .config import CASABLANCA_SCHEDULE_BASE_URL, CASABLANCA_SCOREBOARD_BASE_URL
from .constants import DEFAULT_TIMEOUT
from .decorators import CachedCasablancaClient, LoggingCasablancaClient
from .game_filters import (
    CompletedGameFilter,
    ConferenceFilter,
    LiveGameFilter,
    ScheduledGameFilter,
    TeamFilter,
)
from .interfaces import ICasablancaClient


class ClientFactory:
    @staticmethod
    def create_base_client(
        scoreboard_base_url: str = CASABLANCA_SCOREBOARD_BASE_URL,
        schedule_base_url: str = CASABLANCA_SCHEDULE_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
    ) -> ICasablancaClient:
        return CasablancaClient(
            scoreboard_base_url=scoreboard_base_url,
            schedule_base_url=schedule_base_url,
            timeout=timeout,
        )

    @staticmethod
    def create_production_client(
        with_logging: bool = False, logger: Any = None
    ) -> ICasablancaClient:
        base = ClientFactory.create_base_client()
        cached = CachedCasablancaClient(base)

        if with_logging:
            return LoggingCasablancaClient(cached, logger=logger)

        return cached

    @staticmethod
    def create_test_client(
        scoreboard_url: str = "http://localhost:8000/scoreboard",
        schedule_url: str = "http://localhost:8000/schedule",
    ) -> ICasablancaClient:
        return CasablancaClient(
            scoreboard_base_url=scoreboard_url,
            schedule_base_url=schedule_url,
            timeout=1,
        )

    @staticmethod
    def create_cached_client(
        cache_duration: int = 300, with_logging: bool = False, logger: Any = None
    ) -> ICasablancaClient:
        base = ClientFactory.create_base_client()
        cached = CachedCasablancaClient(base, cache_duration=cache_duration)

        if with_logging:
            return LoggingCasablancaClient(cached, logger=logger)

        return cached


class FilterFactory:
    _filters: dict[str, type] = {
        "live": LiveGameFilter,
        "completed": CompletedGameFilter,
        "scheduled": ScheduledGameFilter,
    }

    @classmethod
    def create(cls, filter_type: str, **kwargs: Any):
        if filter_type == "team":
            team_name = kwargs.get("team_name")
            if not team_name:
                raise ValueError("team_name is required for TeamFilter")
            return TeamFilter(team_name)

        if filter_type == "conference":
            conference = kwargs.get("conference")
            if not conference:
                raise ValueError("conference is required for ConferenceFilter")
            return ConferenceFilter(conference)

        filter_class = cls._filters.get(filter_type)
        if not filter_class:
            raise ValueError(
                f"Unknown filter type: {filter_type}. "
                f"Available types: {', '.join(cls._filters.keys())}, team, conference"
            )
        return filter_class()

    @classmethod
    def register(cls, name: str, filter_class: type) -> None:
        cls._filters[name] = filter_class

    @classmethod
    def available_filters(cls) -> list[str]:
        return list(cls._filters.keys()) + ["team", "conference"]
