from abc import ABC, abstractmethod

from .models import Gender


class GenderResolver(ABC):
    @abstractmethod
    def resolve(self, sport_name: str, text_gender: Gender) -> Gender:
        pass


class DefaultGenderResolver(GenderResolver):
    def __init__(self):
        self._defaults: dict[str, Gender] = {
            "softball": Gender.WOMEN,
            "baseball": Gender.MEN,
            "field hockey": Gender.WOMEN,
            "rowing": Gender.WOMEN,
            "bowling": Gender.WOMEN,
            "beach volleyball": Gender.WOMEN,
            "rifle": Gender.COED,
            "skiing": Gender.COED,
            "football": Gender.MEN,
            "fencing": Gender.COED,
        }

    def resolve(self, sport_name: str, text_gender: Gender) -> Gender:
        if text_gender is not Gender.UNSPECIFIED:
            return text_gender

        key = sport_name.strip().lower()
        return self._defaults.get(key, text_gender)

    def register_default(self, sport_name: str, gender: Gender) -> None:
        key = sport_name.strip().lower()
        self._defaults[key] = gender
