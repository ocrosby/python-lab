# NCAA Casablanca API Integration

This document describes how to use the NCAA Casablanca API integration for accessing live scores, schedules, and game data.

## Overview

The Casablanca API provides access to:
- **Scoreboard API**: Live scores and game status for basketball
- **Schedule API**: Comprehensive schedule information for multiple sports including venue, weather, and video streaming details

## Installation

```bash
uv sync
```

## Quick Start

### Using the Service Layer (Recommended)

```python
from ncaa import get_casablanca_service

service = get_casablanca_service()

# Get today's men's basketball games
scoreboard = service.get_todays_mens_basketball_games()
for game_wrapper in scoreboard.games:
    game = game_wrapper.game
    print(f"{game.away.names.short} @ {game.home.names.short}: {game.away.score}-{game.home.score}")

# Get women's basketball schedule
schedule = service.get_basketball_schedule("women", "2024/03/15")
for game_wrapper in schedule.games:
    game = game_wrapper.game
    print(f"{game.away.names.short} vs {game.home.names.short} at {game.venue}")
```

### Using the Client Directly

```python
from ncaa import CasablancaClient

client = CasablancaClient()

# Get scoreboard
scoreboard = client.get_scoreboard("men", "d1", "2024/03/15")

# Get schedule
schedule = client.get_schedule("basketball-men", "d1", "2024/03/15")
```

## API Features

### Scoreboard API

Fetches live scores and game status for basketball games.

**Supported Sports**: Basketball (men's and women's)

#### Methods

```python
# Get men's basketball scoreboard for a specific date
scoreboard = service.get_mens_basketball_scoreboard("2024/03/15")

# Get women's basketball scoreboard
scoreboard = service.get_womens_basketball_scoreboard("2024/03/15")

# Get today's games
scoreboard = service.get_todays_mens_basketball_games()
scoreboard = service.get_todays_womens_basketball_games()

# Get live games
live_games = service.get_live_games("men")
```

### Schedule API

Fetches comprehensive schedule information including venue, weather, and streaming details.

**Supported Sports**: 
- Basketball (men's and women's)
- Football
- Soccer (men's and women's)
- Baseball
- Softball

#### Methods

```python
# Get basketball schedule
schedule = service.get_basketball_schedule("men", "2024/03/15")

# Get football schedule
schedule = service.get_football_schedule("2024/09/15")

# Get soccer schedule
schedule = service.get_soccer_schedule("women", "2024/11/24")

# Get today's schedule
schedule = service.get_todays_schedule("basketball-men")

# Get upcoming schedules (next 7 days)
schedules = service.get_upcoming_schedules("basketball-men", days=7)

# Get all upcoming games
games = service.get_upcoming_games("basketball-men", days=7)
```

## Data Models

### Game State

```python
from ncaa import GameState

# Possible values
GameState.PRE         # Pre-game
GameState.IN          # In progress
GameState.POST        # Completed
GameState.SCHEDULED   # Scheduled
GameState.INPROGRESS  # In progress (schedule API)
GameState.FINAL       # Final
GameState.POSTPONED   # Postponed
GameState.CANCELLED   # Cancelled
```

### Game Object

```python
game = game_wrapper.game

# Basic info
game.url              # Game URL
game.gameState        # GameState enum
game.startTimeEpoch   # Unix timestamp
game.network          # Broadcast network

# Score info
game.home.score       # Home team score
game.away.score       # Away team score
game.currentPeriod    # Current period/quarter

# Team info
game.home.names.short     # Short team name
game.home.names.full      # Full team name
game.home.rank            # National ranking
game.home.seed            # Tournament seed
game.home.record          # Season record

# Schedule-specific info
game.venue            # Venue name
game.location         # City, state
game.weather          # Weather object (for outdoor sports)
game.attendance       # Attendance number
game.liveVideoEnabled # Video streaming available
```

## Caching

The client automatically caches responses for 5 minutes to reduce API calls.

```python
# Clear cache manually
service.clear_cache()

# Set custom cache duration (in seconds)
client = CasablancaClient()
client.set_cache_duration(600)  # 10 minutes
```

## Division Levels

- `d1`: Division I (default)
- `d2`: Division II
- `d3`: Division III

```python
# Get Division II men's basketball games
scoreboard = service.get_mens_basketball_scoreboard("2024/03/15", division="d2")
```

## Date Format

All dates must be in `YYYY/MM/DD` format:

```python
# Correct
service.get_mens_basketball_scoreboard("2024/03/15")

# Incorrect
service.get_mens_basketball_scoreboard("03/15/2024")  # Will fail
service.get_mens_basketball_scoreboard("2024-03-15")  # Will fail
```

## Error Handling

```python
from ncaa import CasablancaClientError

try:
    scoreboard = service.get_mens_basketball_scoreboard("2024/03/15")
except CasablancaClientError as e:
    print(f"API Error: {e}")
```

## Examples

### Get Live Basketball Scores

```python
from ncaa import get_casablanca_service

service = get_casablanca_service()

# Get live men's basketball games
live_games = service.get_live_games("men")

for game_wrapper in live_games:
    game = game_wrapper.game
    print(f"LIVE: {game.away.names.short} {game.away.score} @ {game.home.names.short} {game.home.score}")
    if game.contestClock:
        print(f"  Time: {game.contestClock} - Period {game.currentPeriod}")
```

### Get Upcoming Games with Details

```python
from ncaa import get_casablanca_service
from datetime import datetime

service = get_casablanca_service()

# Get next week of games
games = service.get_upcoming_games("basketball-men", days=7)

for game_wrapper in games:
    game = game_wrapper.game
    timestamp = datetime.fromtimestamp(game.startTimeEpoch)
    
    print(f"\n{game.away.names.short} @ {game.home.names.short}")
    print(f"  When: {timestamp.strftime('%A, %B %d at %I:%M %p')}")
    
    if game.venue:
        print(f"  Where: {game.venue}, {game.location}")
    
    if game.network:
        print(f"  TV: {game.network}")
    
    if game.away.rank or game.home.rank:
        away_rank = f"#{game.away.rank} " if game.away.rank else ""
        home_rank = f"#{game.home.rank} " if game.home.rank else ""
        print(f"  Matchup: {away_rank}{game.away.names.short} vs {home_rank}{game.home.names.short}")
```

### Get Football Games with Weather

```python
from ncaa import get_casablanca_service

service = get_casablanca_service()

schedule = service.get_football_schedule("2024/09/15")

for game_wrapper in schedule.games:
    game = game_wrapper.game
    
    print(f"\n{game.away.names.short} @ {game.home.names.short}")
    print(f"  Venue: {game.venue}")
    
    if game.weather:
        print(f"  Weather: {game.weather.condition}, {game.weather.temperature}")
        print(f"  Wind: {game.weather.wind}")
```

### Check Tournament Bracket Information

```python
from ncaa import get_casablanca_service

service = get_casablanca_service()

scoreboard = service.get_mens_basketball_scoreboard("2024/03/21")

for game_wrapper in scoreboard.games:
    game = game_wrapper.game
    
    if game.bracketRound:
        print(f"\n{game.away.names.short} (#{game.away.seed}) vs {game.home.names.short} (#{game.home.seed})")
        print(f"  Round: {game.bracketRound}")
        print(f"  Region: {game.bracketRegion}")
```

## Testing

```bash
# Run all Casablanca tests
pytest tests/test_casablanca_client.py tests/test_casablanca_service.py -v

# Run with coverage
pytest tests/test_casablanca_*.py --cov=ncaa.casablanca_client --cov=ncaa.casablanca_service
```

## API Reference

For detailed API documentation, see [casablanca.md](casablanca.md).

## Base URLs

- Scoreboard: `https://data.ncaa.com/casablanca/scoreboard`
- Schedule: `https://data.ncaa.com/casablanca/schedule`

## Rate Limiting

The NCAA Casablanca API does not have official rate limits, but it's recommended to:
- Implement caching (built-in with 5-minute default)
- Add reasonable delays between requests
- Avoid making excessive concurrent requests

## Support

For issues or questions:
1. Check the [casablanca.md](casablanca.md) documentation
2. Review the test files for examples
3. See the [examples/casablanca_demo.py](examples/casablanca_demo.py) for usage examples
