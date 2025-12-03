from .casablanca_models import GameState, GameWrapper


class LiveGameFilter:
    def filter(self, games: list[GameWrapper]) -> list[GameWrapper]:
        return [
            game
            for game in games
            if game.game.gameState in [GameState.IN, GameState.INPROGRESS]
        ]


class CompletedGameFilter:
    def filter(self, games: list[GameWrapper]) -> list[GameWrapper]:
        return [
            game
            for game in games
            if game.game.gameState in [GameState.POST, GameState.FINAL]
        ]


class ScheduledGameFilter:
    def filter(self, games: list[GameWrapper]) -> list[GameWrapper]:
        return [
            game
            for game in games
            if game.game.gameState in [GameState.PRE, GameState.SCHEDULED]
        ]


class TeamFilter:
    def __init__(self, team_name: str):
        self.team_name = team_name.lower()

    def filter(self, games: list[GameWrapper]) -> list[GameWrapper]:
        return [
            game
            for game in games
            if self.team_name in game.game.home.names.full.lower()
            or self.team_name in game.game.away.names.full.lower()
        ]


class ConferenceFilter:
    def __init__(self, conference: str):
        self.conference = conference

    def filter(self, games: list[GameWrapper]) -> list[GameWrapper]:
        return [
            game
            for game in games
            if any(
                c.conferenceName == self.conference for c in game.game.home.conferences
            )
            or any(
                c.conferenceName == self.conference for c in game.game.away.conferences
            )
        ]


class FilterChain:
    def __init__(self):
        self._filters: list = []

    def add_filter(self, game_filter) -> "FilterChain":
        self._filters.append(game_filter)
        return self

    def filter(self, games: list[GameWrapper]) -> list[GameWrapper]:
        result = games
        for f in self._filters:
            result = f.filter(result)
        return result
