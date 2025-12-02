import requests


class HttpClientError(RuntimeError):
    pass


def fetch_html(url: str, *, timeout: int = 10) -> str:
    try:
        resp = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ncaa-scraper/1.0)"},
        )
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as exc:
        raise HttpClientError(f"Error fetching {url}: {exc}") from exc
