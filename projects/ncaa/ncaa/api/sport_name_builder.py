from ..core.config import build_sport_name
from ..core.constants import SportName


class SportNameBuilder:
    @staticmethod
    def build_basketball(gender: str) -> str:
        return build_sport_name(SportName.BASKETBALL.value, gender)

    @staticmethod
    def build_soccer(gender: str) -> str:
        return build_sport_name(SportName.SOCCER.value, gender)

    @staticmethod
    def build_football() -> str:
        return SportName.FOOTBALL.value

    @staticmethod
    def build(sport: str, gender: str | None = None) -> str:
        if gender:
            return build_sport_name(sport, gender)
        return sport
