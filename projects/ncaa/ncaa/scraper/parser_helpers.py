from __future__ import annotations

from ..scraper.models import Gender, Season


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


def _strip_suffix(text: str, suffix: str) -> str:
    if text.endswith(suffix):
        return text[: -len(suffix)].rstrip()
    return text


def _strip_suffix_case_insensitive(text: str, suffix: str) -> str:
    lower_text = text.lower()
    lower_suffix = suffix.lower()

    if lower_text.endswith(lower_suffix):
        idx = lower_text.rfind(lower_suffix)
        return text[:idx].rstrip()

    return text


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
    normalized = _strip_suffix(raw_name, suffix)

    if normalized == raw_name:
        normalized = _strip_suffix_case_insensitive(raw_name, suffix)

    return normalized


def apply_default_gender(sport_name: str, gender: Gender) -> Gender:
    """
    If gender is UNSPECIFIED, apply domain-specific defaults
    (e.g., Softball -> Women, Baseball -> Men).

    If gender is already Men/Women from the text, we keep it.

    Deprecated: Use DefaultGenderResolver directly instead.
    """
    try:
        from ..scraper.gender_resolver import DefaultGenderResolver
    except ImportError:
        from gender_resolver import DefaultGenderResolver

    resolver = DefaultGenderResolver()
    return resolver.resolve(sport_name, gender)


# --- Season helpers (unchanged) ----------------------------------------


def extract_season_name(season_block) -> str | None:
    from ..core.constants import CssSelector

    header = season_block.select_one(CssSelector.SEASON_HEADER.value)
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
