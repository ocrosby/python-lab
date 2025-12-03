from .basketball_service import BasketballService
from .casablanca_models import (
    ScoreboardResponse,
)
from .constants import DEFAULT_DIVISION
from .interfaces import ICasablancaClient
from .schedule_helpers import ScheduleHelper
from .schedule_service import ScheduleService


class CasablancaService:
    def __init__(self, client: ICasablancaClient):
        schedule_helper = ScheduleHelper()
        self.basketball = BasketballService(client, schedule_helper)
        self.schedule = ScheduleService(client, schedule_helper)

    def get_basketball_scoreboard(
        self, gender: str, date: str, division: str = DEFAULT_DIVISION.value
    ) -> ScoreboardResponse:
        return self.basketball.get_scoreboard(gender, date, division)

    def get_todays_basketball_games(
        self, gender: str, division: str = DEFAULT_DIVISION.value
    ) -> ScoreboardResponse:
        return self.basketball.get_todays_scoreboard(gender, division)

    def clear_cache(self) -> None:
        if hasattr(self.basketball, "client") and hasattr(
            self.basketball.client, "clear_cache"
        ):
            self.basketball.client.clear_cache()


def get_casablanca_service(
    client: ICasablancaClient | None = None,
) -> CasablancaService:
    if client is None:
        from .casablanca_client import CasablancaClient

        client = CasablancaClient()
    return CasablancaService(client)
