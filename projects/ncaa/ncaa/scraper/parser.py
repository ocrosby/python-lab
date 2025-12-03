from __future__ import annotations

from collections import defaultdict
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from ..core.config import NCAA_BASE_URL
from ..core.constants import CssSelector
from ..scraper.models import Gender, Season, Sport
from ..scraper.parser_helpers import (
    extract_gender,
    extract_season_name,
    map_season,
    normalize_sport_name,
)


class ParsedSportData:
    def __init__(self, name: str, gender: Gender, url: str | None):
        self.name = name
        self.gender = gender
        self.url = url


def _find_sports_nav(soup: BeautifulSoup) -> Tag:
    sports_nav = soup.select_one(CssSelector.SPORTS_NAV.value)
    if sports_nav is None:
        raise ValueError(
            f"Could not find '{CssSelector.SPORTS_NAV.value}' in the provided HTML"
        )
    return sports_nav


def _parse_sport_tag(tag: Tag, base_url: str, gender_resolver) -> ParsedSportData:
    raw_name = tag.get_text(strip=True)

    gender = extract_gender(raw_name)
    name = normalize_sport_name(raw_name, gender)
    gender = gender_resolver.resolve(name, gender)

    href = tag.get("href")
    url = urljoin(base_url, str(href)) if href else None

    return ParsedSportData(name, gender, url)


def _extract_sports_data(
    season_block: Tag, base_url: str, gender_resolver
) -> list[ParsedSportData]:
    sports_data = []
    for tag in season_block.select(CssSelector.SPORT_LINK.value):
        raw_name = tag.get_text(strip=True)
        if not raw_name:
            continue
        sports_data.append(_parse_sport_tag(tag, base_url, gender_resolver))
    return sports_data


def _group_sports_by_name(
    sports_data: list[ParsedSportData],
) -> dict[str, list[tuple[Gender, str | None]]]:
    grouped: dict[str, list[tuple[Gender, str | None]]] = defaultdict(list)
    for entry in sports_data:
        grouped[entry.name].append((entry.gender, entry.url))
    return grouped


def _should_skip_unspecified_entry(
    gender: Gender, genders_in_group: set[Gender]
) -> bool:
    return gender is Gender.UNSPECIFIED and (
        Gender.MEN in genders_in_group or Gender.WOMEN in genders_in_group
    )


def _create_sports_from_group(
    name: str,
    entries: list[tuple[Gender, str | None]],
    season: Season,
) -> list[Sport]:
    sports = []
    genders_in_group = {g for g, _ in entries}

    for gender, url in entries:
        if _should_skip_unspecified_entry(gender, genders_in_group):
            continue

        sports.append(
            Sport(
                name=name,
                season=season,
                gender=gender,
                url=url,
            )
        )

    return sports


def _parse_season_block(
    season_block: Tag, base_url: str, gender_resolver
) -> list[Sport]:
    raw_season_name = extract_season_name(season_block)
    if raw_season_name is None:
        return []

    season = map_season(raw_season_name)
    sports_data = _extract_sports_data(season_block, base_url, gender_resolver)
    grouped = _group_sports_by_name(sports_data)

    sports = []
    for name, entries in grouped.items():
        sports.extend(_create_sports_from_group(name, entries, season))

    return sports


def parse_sports(
    html: str, *, base_url: str = NCAA_BASE_URL, gender_resolver=None
) -> list[Sport]:
    """
    Parse the NCAA sports navigation HTML into a list of Sport models.

    Args:
        html: The HTML content to parse
        base_url: Base URL for resolving relative links
        gender_resolver: Optional GenderResolver for customizing gender assignment

    Rules:
      - Remove ' - Men' / ' - Women' suffix from names.
      - Infer gender from text if present.
      - Apply domain defaults via gender_resolver
      - For each (season, sport name):
          * If only UNSPECIFIED exists -> keep it
          * If Men/Women exist -> do NOT include the UNSPECIFIED parent entry
    """
    if gender_resolver is None:
        from ..scraper.gender_resolver import DefaultGenderResolver

        gender_resolver = DefaultGenderResolver()

    soup = BeautifulSoup(html, "html.parser")
    sports_nav = _find_sports_nav(soup)

    sports: list[Sport] = []
    for season_block in sports_nav.select(CssSelector.SEASON.value):
        sports.extend(_parse_season_block(season_block, base_url, gender_resolver))

    return sports
