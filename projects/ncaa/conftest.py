import pytest
from ncaa.container import Container


@pytest.fixture(scope="session")
def container():
    container = Container()
    return container


@pytest.fixture
def basketball_service(container):
    return container.basketball_service()


@pytest.fixture
def schedule_service(container):
    return container.schedule_service()


@pytest.fixture
def casablanca_client(container):
    return container.casablanca_client()


@pytest.fixture
def schedule_helper(container):
    return container.schedule_helper()


@pytest.fixture
def live_game_filter(container):
    return container.live_game_filter()


@pytest.fixture
def gender_resolver(container):
    return container.gender_resolver()


@pytest.fixture
def html_fetcher(container):
    return container.html_fetcher()


@pytest.fixture
def ncaa_sports_service(container):
    return container.ncaa_sports_service()
