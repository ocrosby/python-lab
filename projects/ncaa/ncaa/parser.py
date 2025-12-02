# ncaa_sports/parser.py

from __future__ import annotations

from typing import List, Dict, Tuple
from collections import defaultdict

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from .config import NCAA_BASE_URL
from .models import Sport, Gender
from .parser_helpers import (
    extract_gender,
    normalize_sport_name,
    apply_default_gender,  # <-- NEW
    extract_season_name,
    map_season,
)


def parse_sports(html: str, *, base_url: str = NCAA_BASE_URL) -> List[Sport]:
    """
    Parse the NCAA sports navigation HTML into a list of Sport models.

    Rules:
      - Remove ' - Men' / ' - Women' suffix from names.
      - Infer gender from text if present.
      - Apply domain defaults:
          * Softball -> Women
          * Baseball -> Men
          * Field Hockey -> Women
      - For each (season, sport name):
          * If only UNSPECIFIED exists -> keep it
          * If Men/Women exist -> do NOT include the UNSPECIFIED parent entry
    """
    soup = BeautifulSoup(html, "html.parser")

    sports_nav = soup.select_one(".sports-nav")
    if sports_nav is None:
        raise ValueError("Could not find '.sports-nav' in the provided HTML")

    sports: List[Sport] = []

    for season_block in sports_nav.select(".season"):
        raw_season_name = extract_season_name(season_block)
        if raw_season_name is None:
            continue

        season = map_season(raw_season_name)

        # name -> list[(gender, url)]
        grouped: Dict[str, List[Tuple[Gender, str | None]]] = defaultdict(list)

        for tag in season_block.select("a.sport-link, span.sport-txt"):
            raw_name = tag.get_text(strip=True)
            if not raw_name:
                continue

            # 1) Text-driven gender
            gender = extract_gender(raw_name)

            # 2) Normalize sport name by stripping " - Men/Women"
            name = normalize_sport_name(raw_name, gender)

            # 3) Apply domain default gender if still UNSPECIFIED
            gender = apply_default_gender(name, gender)

            # 4) Resolve URL (only <a> tags have href)
            href = tag.get("href")
            url = urljoin(base_url, href) if href else None

            grouped[name].append((gender, url))

        # Now create Sport objects, applying the "no parent UNSPECIFIED" rule
        for name, entries in grouped.items():
            genders_in_group = {g for g, _ in entries}

            for gender, url in entries:
                if gender is Gender.UNSPECIFIED and (
                    Gender.MEN in genders_in_group or Gender.WOMEN in genders_in_group
                ):
                    # Drop parent UNSPECIFIED when gendered variants exist
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
