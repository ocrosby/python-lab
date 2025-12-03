from ..core.config import NCAA_BASE_URL
from ..core.interfaces import IGenderResolver, IHtmlFetcher
from ..scraper.models import Sport
from ..scraper.parser import parse_sports


class NcaaSportsServiceError(RuntimeError):
    pass


class NcaaSportsService:
    def __init__(
        self,
        html_fetcher: IHtmlFetcher,
        gender_resolver: IGenderResolver | None = None,
    ):
        self.html_fetcher = html_fetcher
        self.gender_resolver = gender_resolver

    def get_sports(self) -> list[Sport]:
        try:
            html = self.html_fetcher.fetch(NCAA_BASE_URL)
            return parse_sports(html, gender_resolver=self.gender_resolver)
        except ValueError as exc:
            raise NcaaSportsServiceError(f"Failed to parse sports data: {exc}") from exc
        except RuntimeError as exc:
            raise NcaaSportsServiceError(f"Failed to fetch sports data: {exc}") from exc
        except Exception as exc:
            raise NcaaSportsServiceError(
                f"Unexpected error retrieving NCAA sports: {exc}"
            ) from exc


def get_ncaa_sports(fetcher: IHtmlFetcher | None = None) -> list[Sport]:
    from ..scraper.fetcher import RequestsHtmlFetcher

    if fetcher is None:
        fetcher = RequestsHtmlFetcher()

    service = NcaaSportsService(fetcher)
    return service.get_sports()
