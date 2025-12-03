from enum import Enum

from pydantic import BaseModel


class GameState(str, Enum):
    PRE = "pre"
    IN = "in"
    POST = "post"
    SCHEDULED = "scheduled"
    INPROGRESS = "inprogress"
    FINAL = "final"
    POSTPONED = "postponed"
    CANCELLED = "cancelled"


class VideoState(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ARCHIVED = "archived"


class TeamNames(BaseModel):
    char6: str
    short: str
    seo: str
    full: str


class Conference(BaseModel):
    conferenceName: str
    conferenceSeo: str | None = None


class Team(BaseModel):
    names: TeamNames
    score: int
    winner: bool | None = None
    rank: int | None = None
    seed: int | None = None
    description: str | None = None
    record: str | None = None
    conferences: list[Conference] = []


class Weather(BaseModel):
    temperature: str | None = None
    condition: str | None = None
    wind: str | None = None
    humidity: str | None = None
    precipitation: str | None = None


class Game(BaseModel):
    gameID: str | None = None
    url: str
    startTimeEpoch: int
    startTime: str | None = None
    startDate: str | None = None
    gameState: GameState
    network: str | None = None
    venue: str | None = None
    location: str | None = None
    attendance: int | None = None
    liveVideoEnabled: bool | None = None
    videoState: VideoState | None = None
    bracketRound: str | None = None
    bracketId: str | None = None
    bracketRegion: str | None = None
    currentPeriod: int = 0
    contestClock: str | None = None
    title: str | None = None
    contestName: str | None = None
    finalMessage: str | None = None
    weather: Weather | None = None
    home: Team
    away: Team


class GameWrapper(BaseModel):
    game: Game


class ScoreboardResponse(BaseModel):
    games: list[GameWrapper] = []


class ScheduleResponse(BaseModel):
    inputMD5Sum: str | None = None
    instanceId: str | None = None
    updated_at: str | None = None
    hideRank: bool | None = None
    games: list[GameWrapper] = []
