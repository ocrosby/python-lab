from .casablanca_models import GameWrapper, ScheduleResponse


class ScheduleHelper:
    @staticmethod
    def collect_games_from_schedules(
        schedules: list[ScheduleResponse],
    ) -> list[GameWrapper]:
        all_games = []
        for schedule in schedules:
            all_games.extend(schedule.games)
        return all_games
