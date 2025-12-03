import pytest

from ncaa.basketball_service import BasketballService
from ncaa.container import Container
from ncaa.decorators import CachedCasablancaClient
from ncaa.game_filters import CompletedGameFilter, LiveGameFilter, ScheduledGameFilter
from ncaa.gender_resolver import DefaultGenderResolver
from ncaa.html_fetcher import RequestsHtmlFetcher
from ncaa.interfaces import ICasablancaClient
from ncaa.schedule_helpers import ScheduleHelper
from ncaa.schedule_service import ScheduleService
from ncaa.service import NcaaSportsService


@pytest.fixture
def container():
    return Container()


def test_container_provides_casablanca_client(container):
    client = container.casablanca_client()

    assert isinstance(client, CachedCasablancaClient)
    assert isinstance(client, ICasablancaClient)


def test_container_casablanca_client_is_singleton(container):
    client1 = container.casablanca_client()
    client2 = container.casablanca_client()

    assert client1 is client2


def test_container_provides_schedule_helper(container):
    helper = container.schedule_helper()

    assert isinstance(helper, ScheduleHelper)


def test_container_schedule_helper_is_factory(container):
    helper1 = container.schedule_helper()
    helper2 = container.schedule_helper()

    assert helper1 is not helper2


def test_container_provides_basketball_service(container):
    service = container.basketball_service()

    assert isinstance(service, BasketballService)


def test_container_basketball_service_uses_shared_client(container):
    service1 = container.basketball_service()
    service2 = container.basketball_service()

    assert service1.client is service2.client


def test_container_basketball_service_is_factory(container):
    service1 = container.basketball_service()
    service2 = container.basketball_service()

    assert service1 is not service2


def test_container_provides_schedule_service(container):
    service = container.schedule_service()

    assert isinstance(service, ScheduleService)


def test_container_schedule_service_uses_shared_client(container):
    service1 = container.schedule_service()
    service2 = container.schedule_service()

    assert service1.client is service2.client


def test_container_schedule_service_is_factory(container):
    service1 = container.schedule_service()
    service2 = container.schedule_service()

    assert service1 is not service2


def test_container_provides_live_game_filter(container):
    game_filter = container.live_game_filter()

    assert isinstance(game_filter, LiveGameFilter)


def test_container_provides_completed_game_filter(container):
    game_filter = container.completed_game_filter()

    assert isinstance(game_filter, CompletedGameFilter)


def test_container_provides_scheduled_game_filter(container):
    game_filter = container.scheduled_game_filter()

    assert isinstance(game_filter, ScheduledGameFilter)


def test_container_provides_gender_resolver(container):
    resolver = container.gender_resolver()

    assert isinstance(resolver, DefaultGenderResolver)


def test_container_gender_resolver_is_factory(container):
    resolver1 = container.gender_resolver()
    resolver2 = container.gender_resolver()

    assert resolver1 is not resolver2


def test_container_provides_html_fetcher(container):
    fetcher = container.html_fetcher()

    assert isinstance(fetcher, RequestsHtmlFetcher)


def test_container_html_fetcher_is_factory(container):
    fetcher1 = container.html_fetcher()
    fetcher2 = container.html_fetcher()

    assert fetcher1 is not fetcher2


def test_container_provides_ncaa_sports_service(container):
    service = container.ncaa_sports_service()

    assert isinstance(service, NcaaSportsService)


def test_container_ncaa_sports_service_is_factory(container):
    service1 = container.ncaa_sports_service()
    service2 = container.ncaa_sports_service()

    assert service1 is not service2
