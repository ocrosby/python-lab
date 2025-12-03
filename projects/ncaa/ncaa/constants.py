from enum import Enum


class Division(str, Enum):
    D1 = "d1"
    D2 = "d2"
    D3 = "d3"


class SportName(str, Enum):
    BASKETBALL = "basketball"
    FOOTBALL = "football"
    SOCCER = "soccer"
    BASEBALL = "baseball"
    SOFTBALL = "softball"
    VOLLEYBALL = "volleyball"


class GenderLabel(str, Enum):
    MEN = "men"
    WOMEN = "women"


class CssSelector(str, Enum):
    SPORTS_NAV = ".sports-nav"
    SEASON = ".season"
    SPORT_LINK = "a.sport-link, span.sport-txt"
    SEASON_HEADER = ".season-header"


DEFAULT_DIVISION = Division.D1
DEFAULT_TIMEOUT = 10
DEFAULT_CACHE_DURATION = 300
