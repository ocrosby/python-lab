from .api import CasablancaService, get_casablanca_service
from .scraper import Gender, Season, Sport, get_ncaa_sports

__version__ = "0.1.0"

__all__ = [
    "CasablancaService",
    "get_casablanca_service",
    "get_ncaa_sports",
    "Sport",
    "Season",
    "Gender",
]


def __getattr__(name):
    """
    Lazy import for backward compatibility.
    Allows imports like: from ncaa import BasketballService
    """
    _MODULE_ALIASES = {  # noqa: N806
        "casablanca_client": "api.client",
        "casablanca_models": "api.models",
        "casablanca_service": "api.service",
        "basketball_service": "api.services.basketball",
        "schedule_service": "api.services.schedule",
        "builders": "api.builders",
        "game_filters": "api.filters",
        "schedule_helpers": "api.helpers",
        "sport_name_builder": "api.sport_name_builder",
        "service": "scraper.service",
        "parser": "scraper.parser",
        "parser_helpers": "scraper.parser_helpers",
        "html_fetcher": "scraper.fetcher",
        "gender_resolver": "scraper.gender_resolver",
        "models": "scraper.models",
        "decorators": "infrastructure.decorators",
        "observers": "infrastructure.observers",
        "factories": "infrastructure.factories",
        "container": "infrastructure.container",
        "config": "core.config",
        "constants": "core.constants",
        "interfaces": "core.interfaces",
    }

    _DEPRECATED_IMPORTS = {  # noqa: N806
        "BasketballService": ("api.services", "BasketballService"),
        "ScheduleService": ("api.services", "ScheduleService"),
        "CasablancaClient": ("api.client", "CasablancaClient"),
        "CasablancaClientError": ("api.client", "CasablancaClientError"),
        "Game": ("api.models", "Game"),
        "GameState": ("api.models", "GameState"),
        "GameWrapper": ("api.models", "GameWrapper"),
        "Team": ("api.models", "Team"),
        "TeamNames": ("api.models", "TeamNames"),
        "Conference": ("api.models", "Conference"),
        "Weather": ("api.models", "Weather"),
        "VideoState": ("api.models", "VideoState"),
        "ScheduleResponse": ("api.models", "ScheduleResponse"),
        "ScoreboardResponse": ("api.models", "ScoreboardResponse"),
        "LiveGameFilter": ("api.filters", "LiveGameFilter"),
        "CompletedGameFilter": ("api.filters", "CompletedGameFilter"),
        "ScheduledGameFilter": ("api.filters", "ScheduledGameFilter"),
        "TeamFilter": ("api.filters", "TeamFilter"),
        "ConferenceFilter": ("api.filters", "ConferenceFilter"),
        "FilterChain": ("api.filters", "FilterChain"),
        "ScheduleQueryBuilder": ("api.builders", "ScheduleQueryBuilder"),
        "ScoreboardQueryBuilder": ("api.builders", "ScoreboardQueryBuilder"),
        "ScheduleHelper": ("api.helpers", "ScheduleHelper"),
        "CachedCasablancaClient": (
            "infrastructure.decorators",
            "CachedCasablancaClient",
        ),
        "LoggingCasablancaClient": (
            "infrastructure.decorators",
            "LoggingCasablancaClient",
        ),
        "ClientFactory": ("infrastructure.factories", "ClientFactory"),
        "FilterFactory": ("infrastructure.factories", "FilterFactory"),
        "Container": ("infrastructure.container", "Container"),
        "DataObserver": ("infrastructure.observers", "DataObserver"),
        "LoggingObserver": ("infrastructure.observers", "LoggingObserver"),
        "CacheMetricsObserver": ("infrastructure.observers", "CacheMetricsObserver"),
        "ObservableCasablancaClient": (
            "infrastructure.observers",
            "ObservableCasablancaClient",
        ),
        "GenderResolver": ("scraper.gender_resolver", "GenderResolver"),
        "DefaultGenderResolver": ("scraper.gender_resolver", "DefaultGenderResolver"),
        "RequestsHtmlFetcher": ("scraper.fetcher", "RequestsHtmlFetcher"),
        "NcaaSportsService": ("scraper.service", "NcaaSportsService"),
    }

    if name in _MODULE_ALIASES:
        import importlib

        module_path = _MODULE_ALIASES[name]
        return importlib.import_module(f".{module_path}", package="ncaa")

    if name in _DEPRECATED_IMPORTS:
        import importlib
        import warnings

        module_path, attr_name = _DEPRECATED_IMPORTS[name]
        warnings.warn(
            f"Importing {name} from 'ncaa' is deprecated. "
            f"Use 'from ncaa.{module_path} import {attr_name}' instead.",
            DeprecationWarning,
            stacklevel=2,
        )

        module = importlib.import_module(f".{module_path}", package="ncaa")
        return getattr(module, attr_name)

    raise AttributeError(f"module 'ncaa' has no attribute '{name}'")
