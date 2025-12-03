from datetime import datetime, timedelta

NCAA_BASE_URL = "https://www.ncaa.com"
CASABLANCA_SCOREBOARD_BASE_URL = "https://data.ncaa.com/casablanca/scoreboard"
CASABLANCA_SCHEDULE_BASE_URL = "https://data.ncaa.com/casablanca/schedule"

NCAA_DATE_FORMAT = "%Y/%m/%d"

SCOREBOARD_URL_TEMPLATE = (
    "{base_url}/basketball-{gender}/{division}/{date}/scoreboard.json"
)
SCHEDULE_URL_TEMPLATE = "{base_url}/{sport}/{division}/{date}/schedule.json"


def get_today_date_string() -> str:
    return datetime.now().strftime(NCAA_DATE_FORMAT)


def format_date_offset(days: int) -> str:
    return (datetime.now() + timedelta(days=days)).strftime(NCAA_DATE_FORMAT)


def build_sport_name(base_sport: str, gender: str) -> str:
    return f"{base_sport}-{gender}"


def build_scoreboard_url(base_url: str, gender: str, division: str, date: str) -> str:
    return SCOREBOARD_URL_TEMPLATE.format(
        base_url=base_url, gender=gender, division=division, date=date
    )


def build_schedule_url(base_url: str, sport: str, division: str, date: str) -> str:
    return SCHEDULE_URL_TEMPLATE.format(
        base_url=base_url, sport=sport, division=division, date=date
    )
