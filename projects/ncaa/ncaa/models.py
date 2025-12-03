from enum import Enum

from pydantic import BaseModel, HttpUrl


class Season(str, Enum):
    FALL = "Fall"
    WINTER = "Winter"
    SPRING = "Spring"


class Gender(str, Enum):
    MEN = "Men"
    WOMEN = "Women"
    COED = "Coed"
    UNSPECIFIED = "Unspecified"


class Sport(BaseModel):
    name: str
    season: Season
    gender: Gender
    url: HttpUrl | None = None
