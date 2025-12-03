from dependency_injector import containers, providers

from ..api.client import CasablancaClient
from ..api.filters import CompletedGameFilter, LiveGameFilter, ScheduledGameFilter
from ..api.helpers import ScheduleHelper
from ..api.services.basketball import BasketballService
from ..api.services.schedule import ScheduleService
from ..core.config import (
    CASABLANCA_SCHEDULE_BASE_URL,
    CASABLANCA_SCOREBOARD_BASE_URL,
)
from ..core.constants import DEFAULT_TIMEOUT
from ..infrastructure.decorators import CachedCasablancaClient
from ..infrastructure.factories import ClientFactory, FilterFactory
from ..scraper.fetcher import RequestsHtmlFetcher
from ..scraper.gender_resolver import DefaultGenderResolver
from ..scraper.service import NcaaSportsService


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    base_casablanca_client = providers.Singleton(
        CasablancaClient,
        scoreboard_base_url=CASABLANCA_SCOREBOARD_BASE_URL,
        schedule_base_url=CASABLANCA_SCHEDULE_BASE_URL,
        timeout=DEFAULT_TIMEOUT,
    )

    casablanca_client = providers.Singleton(
        CachedCasablancaClient,
        client=base_casablanca_client,
    )

    client_factory = providers.Factory(ClientFactory)

    filter_factory = providers.Factory(FilterFactory)

    schedule_helper = providers.Factory(ScheduleHelper)

    basketball_service = providers.Factory(
        BasketballService,
        client=casablanca_client,
        schedule_helper=schedule_helper,
    )

    schedule_service = providers.Factory(
        ScheduleService,
        client=casablanca_client,
        schedule_helper=schedule_helper,
    )

    live_game_filter = providers.Factory(LiveGameFilter)

    completed_game_filter = providers.Factory(CompletedGameFilter)

    scheduled_game_filter = providers.Factory(ScheduledGameFilter)

    gender_resolver = providers.Factory(DefaultGenderResolver)

    html_fetcher = providers.Factory(RequestsHtmlFetcher, timeout=DEFAULT_TIMEOUT)

    ncaa_sports_service = providers.Factory(
        NcaaSportsService,
        html_fetcher=html_fetcher,
        gender_resolver=gender_resolver,
    )
