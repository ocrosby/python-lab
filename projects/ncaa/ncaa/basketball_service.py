from .casablanca_models import GameWrapper, ScheduleResponse, ScoreboardResponse
from .config import get_today_date_string
from .constants import DEFAULT_DIVISION
from .game_filters import LiveGameFilter
from .interfaces import ICasablancaClient, IGameFilter, IScheduleHelper
from .sport_name_builder import SportNameBuilder


class BasketballService:
    def __init__(
        self,
        client: ICasablancaClient,
        schedule_helper: IScheduleHelper,
    ):
        self.client = client
        self.schedule_helper = schedule_helper

    def get_scoreboard(
        self, gender: str, date: str, division: str = DEFAULT_DIVISION.value
    ) -> ScoreboardResponse:
        return self.client.get_scoreboard(gender, division, date)

    def get_todays_scoreboard(
        self, gender: str, division: str = DEFAULT_DIVISION.value
    ) -> ScoreboardResponse:
        return self.client.get_todays_scoreboard(gender, division)

    def get_schedule(
        self, gender: str, date: str, division: str = DEFAULT_DIVISION.value
    ) -> ScheduleResponse:
        sport = SportNameBuilder.build_basketball(gender)
        return self.client.get_schedule(sport, division, date)

    def get_todays_schedule(
        self, gender: str, division: str = DEFAULT_DIVISION.value
    ) -> ScheduleResponse:
        sport = SportNameBuilder.build_basketball(gender)
        return self.client.get_todays_schedule(sport, division)

    def get_upcoming_schedules(
        self, gender: str, division: str = DEFAULT_DIVISION.value, days: int = 7
    ) -> list[ScheduleResponse]:
        sport = SportNameBuilder.build_basketball(gender)
        return self.client.get_upcoming_schedules(sport, division, days)

    def get_games_by_filter(
        self, gender: str, division: str, game_filter: IGameFilter
    ) -> list[GameWrapper]:
        today = get_today_date_string()
        scoreboard = self.client.get_scoreboard(gender, division, today)
        return game_filter.filter(scoreboard.games)

    def get_live_games(
        self, gender: str, division: str = DEFAULT_DIVISION.value
    ) -> list[GameWrapper]:
        return self.get_games_by_filter(gender, division, LiveGameFilter())

    def get_upcoming_games(
        self, gender: str, division: str = DEFAULT_DIVISION.value, days: int = 7
    ) -> list[GameWrapper]:
        schedules = self.get_upcoming_schedules(gender, division, days)
        return self.schedule_helper.collect_games_from_schedules(schedules)

    def clear_cache(self) -> None:
        self.client.clear_cache()
