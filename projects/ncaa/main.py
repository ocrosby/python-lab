# main.py

from __future__ import annotations

import sys
from typing import Optional

import click

from ncaa import get_ncaa_sports, Season, Gender


def _print_sports_table(sports, *, show_gender: bool) -> None:
    """Pretty-print a table of sports to stdout."""
    if show_gender:
        header = f"{'Season':8} | {'Gender':11} | {'Sport':35} | URL"
    else:
        header = f"{'Season':8} | {'Sport':35} | URL"

    sep = "-" * len(header)
    click.echo(header)
    click.echo(sep)

    for sport in sports:
        season = sport.season.value
        name = sport.name
        url = sport.url or "-"

        if show_gender:
            gender = sport.gender.value
            click.echo(f"{season:8} | {gender:11} | {name:35} | {url}")
        else:
            click.echo(f"{season:8} | {name:35} | {url}")


@click.group()
def cli() -> None:
    """CLI tools for working with NCAA sports."""
    pass


@cli.command()
@click.option(
    "--season",
    "-s",
    type=click.Choice([s.value for s in Season], case_sensitive=False),
    help="Filter sports by season (Fall, Winter, Spring).",
)
@click.option(
    "--gender",
    "-g",
    type=click.Choice(["Men", "Women", "Coed"], case_sensitive=False),
    help="Filter sports by gender (Men, Women, Coed).",
)
def sports(season: Optional[str], gender: Optional[str]) -> None:
    """
    Display a table of NCAA sports.

    If --gender is supplied (Men, Women, Coed):
      - Only sports with that gender are shown.
      - The Gender column is omitted.

    If --gender is not supplied:
      - All sports are shown.
      - The Gender column is included.
    """
    try:
        all_sports = get_ncaa_sports()
    except Exception as exc:
        click.echo(f"Error fetching NCAA sports: {exc}", err=True)
        sys.exit(1)

    # Season filter (if provided)
    if season is not None:
        all_sports = [s for s in all_sports if s.season.value.lower() == season.lower()]

    # Gender filter (if provided)
    show_gender_column = gender is None

    if gender is not None:
        # Map CLI gender string to Gender enum
        gender_map = {
            "men": Gender.MEN,
            "women": Gender.WOMEN,
            "coed": Gender.COED,
        }
        target_gender = gender_map[gender.lower()]

        all_sports = [s for s in all_sports if s.gender is target_gender]

    # Sort for stable, readable output
    all_sports.sort(key=lambda s: (s.season.value, s.name, s.gender.value))

    if not all_sports:
        click.echo("No sports matched the given filters.")
        return

    _print_sports_table(all_sports, show_gender=show_gender_column)


if __name__ == "__main__":
    cli()
