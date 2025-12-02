# ncaa_sports/parser_helpers.py

from __future__ import annotations

from typing import Optional

from .models import Season, Gender


def extract_gender(raw_name: str) -> Gender:
    """
    Infer gender from a raw sport name string.

    Examples:
        "Soccer - Men"   -> MEN
        "Soccer - Women" -> WOMEN
        "Soccer"         -> UNSPECIFIED
    """
    lower = raw_name.lower()

    if "women" in lower:
        return Gender.WOMEN
    if "men" in lower:
        return Gender.MEN

    return Gender.UNSPECIFIED


def normalize_sport_name(raw_name: str, gender: Gender) -> str:
    """
    Strip ' - Men' or ' - Women' from the end of the name when gender is known.

    Examples:
        "Soccer - Men"   + MEN   -> "Soccer"
        "Soccer - Women" + WOMEN -> "Soccer"
        "Softball"       + UNSPECIFIED -> "Softball"
    """
    if gender is Gender.UNSPECIFIED:
        return raw_name

    suffix = f" - {gender.value}"
    if raw_name.endswith(suffix):
        return raw_name[: -len(suffix)].rstrip()

    # Defensive: case-insensitive variant
    suffix_lower = suffix.lower()
    lower = raw_name.lower()
    if lower.endswith(suffix_lower):
        idx = lower.rfind(suffix_lower)
        return raw_name[:idx].rstrip()

    return raw_name


# --- NEW: domain-specific default genders -------------------------------

_DEFAULT_GENDER_BY_SPORT: dict[str, Gender] = {
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
    # add more as needed
}


def apply_default_gender(sport_name: str, gender: Gender) -> Gender:
    """
    If gender is UNSPECIFIED, apply domain-specific defaults
    (e.g., Softball -> Women, Baseball -> Men).

    If gender is already Men/Women from the text, we keep it.
    """
    if gender is not Gender.UNSPECIFIED:
        return gender

    key = sport_name.strip().lower()
    default = _DEFAULT_GENDER_BY_SPORT.get(key)
    return default or gender


# --- Season helpers (unchanged) ----------------------------------------


def extract_season_name(season_block) -> Optional[str]:
    header = season_block.select_one(".season-header")
    if header is None:
        return None
    text = header.get_text(strip=True)
    return " ".join(text.split()) or None


def map_season(season_name: str) -> Season:
    lower = season_name.lower()
    if "fall" in lower:
        return Season.FALL
    if "winter" in lower:
        return Season.WINTER
    if "spring" in lower:
        return Season.SPRING
    raise ValueError(f"Unknown season name: {season_name!r}")
