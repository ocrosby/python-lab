from ...core.constants import DEFAULT_DIVISION
from ...core.interfaces import ICasablancaClient, IScheduleHelper
from ..models import GameWrapper, ScheduleResponse
from ..sport_name_builder import SportNameBuilder


class ScheduleService:
    def __init__(
        self,
        client: ICasablancaClient,
        schedule_helper: IScheduleHelper,
    ):
        self.client = client
        self.schedule_helper = schedule_helper

    def get_schedule(
        self, sport: str, date: str, division: str = DEFAULT_DIVISION.value
    ) -> ScheduleResponse:
        return self.client.get_schedule(sport, division, date)

    def get_todays_schedule(
        self, sport: str, division: str = DEFAULT_DIVISION.value
    ) -> ScheduleResponse:
        return self.client.get_todays_schedule(sport, division)

    def get_upcoming_schedules(
        self, sport: str, division: str = DEFAULT_DIVISION.value, days: int = 7
    ) -> list[ScheduleResponse]:
        return self.client.get_upcoming_schedules(sport, division, days)

    def get_upcoming_games(
        self, sport: str, division: str = DEFAULT_DIVISION.value, days: int = 7
    ) -> list[GameWrapper]:
        schedules = self.get_upcoming_schedules(sport, division, days)
        return self.schedule_helper.collect_games_from_schedules(schedules)

    def get_football_schedule(
        self, date: str, division: str = DEFAULT_DIVISION.value
    ) -> ScheduleResponse:
        return self.get_schedule(SportNameBuilder.build_football(), date, division)

    def get_soccer_schedule(
        self, gender: str, date: str, division: str = DEFAULT_DIVISION.value
    ) -> ScheduleResponse:
        sport = SportNameBuilder.build_soccer(gender)
        return self.get_schedule(sport, date, division)

    def clear_cache(self) -> None:
        self.client.clear_cache()
