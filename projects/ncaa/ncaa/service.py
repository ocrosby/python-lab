from .http_client import fetch_html
from .parser import parse_sports
from .config import NCAA_BASE_URL
from .models import Sport


def get_ncaa_sports() -> list[Sport]:
    html = fetch_html(NCAA_BASE_URL)
    return parse_sports(html)
