from .constants import DEFAULT_TIMEOUT


class RequestsHtmlFetcher:
    def __init__(self, timeout: int = DEFAULT_TIMEOUT):
        self.timeout = timeout

    def fetch(self, url: str) -> str:
        import requests

        try:
            resp = requests.get(
                url,
                timeout=self.timeout,
                headers={"User-Agent": "Mozilla/5.0 (compatible; ncaa-scraper/1.0)"},
            )
            resp.raise_for_status()
            return resp.text
        except requests.RequestException as exc:
            raise RuntimeError(f"Error fetching {url}: {exc}") from exc
