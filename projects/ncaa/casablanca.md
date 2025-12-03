# NCAA Casablanca Schedule API Documentation

## Overview

The NCAA Casablanca Schedule API provides access to NCAA basketball game schedules, scores, and related information. This API is used by the NCAA's official website and provides real-time data for Division I men's and women's basketball games.

## Base URL

```
https://data.ncaa.com/casablanca/scoreboard/
```

## API Endpoints

### Basketball Schedule Endpoint

**Endpoint:** `/basketball-{gender}/d1/{date}/scoreboard.json`

**Method:** `GET`

**Description:** Retrieves the schedule of basketball games for a specific date and gender.

## Input Parameters

### Path Parameters

| Parameter | Type | Required | Description | Possible Values |
|-----------|------|----------|-------------|-----------------|
| `gender` | string | Yes | Specifies the gender of the basketball games | `men`, `women` |
| `date` | string | Yes | The date for which to retrieve the schedule | Format: `YYYY/MM/DD` |

### Parameter Details

#### Gender Parameter
- **`men`**: Retrieves men's Division I basketball games
- **`women`**: Retrieves women's Division I basketball games

#### Date Parameter
- **Format**: `YYYY/MM/DD`
- **Example**: `2024/03/15` for March 15, 2024
- **Timezone**: All times are in Eastern Time (ET)

## Example API Calls

### Men's Basketball Schedule
```bash
curl "https://data.ncaa.com/casablanca/scoreboard/basketball-men/d1/2024/03/15/scoreboard.json"
```

### Women's Basketball Schedule
```bash
curl "https://data.ncaa.com/casablanca/scoreboard/basketball-women/d1/2024/03/15/scoreboard.json"
```

### JavaScript Example
```javascript
const fetchNCAAgames = async (gender, date) => {
  const url = `https://data.ncaa.com/casablanca/scoreboard/basketball-${gender}/d1/${date}/scoreboard.json`;
  
  try {
    const response = await fetch(url);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching NCAA games:', error);
    throw error;
  }
};

// Usage
const games = await fetchNCAAgames('men', '2024/03/15');
```

### Python Example
```python
import requests
from datetime import datetime

def fetch_ncaa_games(gender, date):
    """
    Fetch NCAA basketball games for a specific date and gender
    
    Args:
        gender (str): 'men' or 'women'
        date (str): Date in YYYY/MM/DD format
    
    Returns:
        dict: API response containing games data
    """
    url = f"https://data.ncaa.com/casablanca/scoreboard/basketball-{gender}/d1/{date}/scoreboard.json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching NCAA games: {e}")
        raise

# Usage
games = fetch_ncaa_games('men', '2024/03/15')
```

## Response Structure

The API returns a JSON object with the following structure:

### Top-Level Response

```json
{
  "games": [
    {
      "game": {
        // Game details object
      }
    }
  ]
}
```

### Game Object Structure

```json
{
  "game": {
    "url": "/game/1234567",
    "startTimeEpoch": 1710518400,
    "gameState": "pre",
    "network": "ESPN",
    "bracketRound": "1",
    "bracketId": "123",
    "bracketRegion": "East",
    "currentPeriod": 0,
    "contestClock": null,
    "away": {
      "names": {
        "char6": "UNC",
        "short": "North Carolina",
        "seo": "north-carolina",
        "full": "University of North Carolina"
      },
      "score": 0,
      "rank": 5,
      "seed": 2,
      "conferences": [
        {
          "conferenceName": "Atlantic Coast"
        }
      ]
    },
    "home": {
      "names": {
        "char6": "DUKE",
        "short": "Duke",
        "seo": "duke",
        "full": "Duke University"
      },
      "score": 0,
      "rank": 10,
      "seed": 3,
      "conferences": [
        {
          "conferenceName": "Atlantic Coast"
        }
      ]
    }
  }
}
```

## Field Descriptions

### Root Level Fields

| Field | Type | Description |
|-------|------|-------------|
| `games` | array | Array of game objects for the specified date |

### Game Object Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `url` | string | Relative URL to the game's detailed page | `/game/1234567` |
| `startTimeEpoch` | integer | Start time of the game in Unix epoch time | `1710518400` |
| `gameState` | string | Current state of the game | `"pre"`, `"in"`, `"post"` |
| `network` | string | Broadcast network for the game | `"ESPN"`, `"CBS"`, `"TBS"` |
| `bracketRound` | string | Tournament round (if applicable) | `"1"`, `"2"`, `"Sweet 16"` |
| `bracketId` | string | Tournament bracket identifier | `"123"` |
| `bracketRegion` | string | Tournament region | `"East"`, `"West"`, `"South"`, `"Midwest"` |
| `currentPeriod` | integer | Current period/quarter of the game | `0`, `1`, `2`, `3`, `4` |
| `contestClock` | string/null | Current game clock time | `"15:30"`, `"2:45"`, `null` |

### Team Object Fields (away/home)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `names` | object | Various representations of team name | See names object below |
| `score` | integer | Current team score | `85`, `0` |
| `rank` | integer/null | National ranking (if available) | `5`, `null` |
| `seed` | integer/null | Tournament seed (if applicable) | `2`, `null` |
| `conferences` | array | Array of conference objects | See conference object below |

### Team Names Object

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `char6` | string | Six-character team abbreviation | `"UNC"`, `"DUKE"` |
| `short` | string | Short team name | `"North Carolina"`, `"Duke"` |
| `seo` | string | SEO-friendly team name | `"north-carolina"`, `"duke"` |
| `full` | string | Full university name | `"University of North Carolina"`, `"Duke University"` |

### Conference Object

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `conferenceName` | string | Name of the conference | `"Atlantic Coast"`, `"Big Ten"` |

## Game States

| State | Description |
|-------|-------------|
| `"pre"` | Pre-game (game hasn't started) |
| `"in"` | In progress |
| `"post"` | Post-game (game completed) |

## Common Conference Names

| Conference | Common Abbreviation |
|------------|-------------------|
| Atlantic Coast | ACC |
| Big Ten | B1G |
| Big 12 | B12 |
| Southeastern | SEC |
| Pac-12 | PAC |
| Big East | BE |
| American Athletic | AAC |
| Mountain West | MWC |
| Atlantic 10 | A10 |
| West Coast | WCC |

## Error Handling

### Common HTTP Status Codes

| Status Code | Description | Solution |
|-------------|-------------|----------|
| `200` | Success | Data retrieved successfully |
| `404` | Not Found | Invalid date or no games scheduled |
| `500` | Server Error | NCAA server issue, retry later |

### Error Response Example

```json
{
  "error": "No games found for the specified date"
}
```

## Rate Limiting

- **No official rate limiting** documented
- **Recommendation**: Implement reasonable delays between requests (1-2 seconds)
- **Best Practice**: Cache responses when possible to reduce API calls

## Data Freshness

- **Real-time updates**: Game scores and states update in real-time during games
- **Schedule updates**: Game schedules may change, so cache with appropriate TTL
- **Tournament data**: Bracket information available during March Madness

## Caching Recommendations

### Cache Strategy
```javascript
const CACHE_DURATION = {
  PRE_GAME: 60 * 60 * 1000, // 1 hour for pre-game data
  IN_PROGRESS: 30 * 1000,   // 30 seconds for live games
  POST_GAME: 24 * 60 * 60 * 1000 // 24 hours for completed games
};

function getCacheDuration(gameState) {
  switch (gameState) {
    case 'pre': return CACHE_DURATION.PRE_GAME;
    case 'in': return CACHE_DURATION.IN_PROGRESS;
    case 'post': return CACHE_DURATION.POST_GAME;
    default: return CACHE_DURATION.PRE_GAME;
  }
}
```

## Integration Examples

### React Hook Example
```javascript
import { useState, useEffect } from 'react';

const useNCAAgames = (gender, date) => {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchGames = async () => {
      try {
        setLoading(true);
        const response = await fetch(
          `https://data.ncaa.com/casablanca/scoreboard/basketball-${gender}/d1/${date}/scoreboard.json`
        );
        const data = await response.json();
        setGames(data.games || []);
      } catch (err) {
        setError(err);
      } finally {
        setLoading(false);
      }
    };

    fetchGames();
  }, [gender, date]);

  return { games, loading, error };
};
```

### Node.js Service Example
```javascript
class NCAAAPIService {
  constructor() {
    this.baseURL = 'https://data.ncaa.com/casablanca/scoreboard';
    this.cache = new Map();
  }

  async getGames(gender, date) {
    const cacheKey = `${gender}-${date}`;
    
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < 300000) { // 5 minutes
        return cached.data;
      }
    }

    try {
      const response = await fetch(
        `${this.baseURL}/basketball-${gender}/d1/${date}/scoreboard.json`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Cache the response
      this.cache.set(cacheKey, {
        data,
        timestamp: Date.now()
      });
      
      return data;
    } catch (error) {
      console.error('Error fetching NCAA games:', error);
      throw error;
    }
  }

  formatDate(date) {
    return date.toISOString().split('T')[0].replace(/-/g, '/');
  }

  async getTodaysGames(gender) {
    const today = this.formatDate(new Date());
    return await this.getGames(gender, today);
  }
}
```

## Best Practices

1. **Error Handling**: Always implement proper error handling for network requests
2. **Caching**: Implement caching to reduce API calls and improve performance
3. **Rate Limiting**: Add delays between requests to be respectful to the API
4. **Data Validation**: Validate response data before processing
5. **Timezone Handling**: Convert epoch times to appropriate timezones for display
6. **Fallback Data**: Have fallback data for when the API is unavailable

## Troubleshooting

### Common Issues

1. **No games returned**: Check if the date is during the basketball season
2. **Invalid date format**: Ensure date is in `YYYY/MM/DD` format
3. **Network timeouts**: Implement retry logic with exponential backoff
4. **CORS issues**: Use a proxy server for client-side requests

### Debugging Tips

```javascript
// Enable detailed logging
const debugAPI = async (gender, date) => {
  console.log(`Fetching games for ${gender} on ${date}`);
  
  try {
    const response = await fetch(
      `https://data.ncaa.com/casablanca/scoreboard/basketball-${gender}/d1/${date}/scoreboard.json`
    );
    
    console.log('Response status:', response.status);
    console.log('Response headers:', [...response.headers.entries()]);
    
    const data = await response.json();
    console.log('Response data:', data);
    
    return data;
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};
```

## NCAA Schedule API

### Overview

The NCAA provides separate schedule APIs that are distinct from the scoreboard APIs. These schedule endpoints are used by the NCAA.com website to display comprehensive schedule information for various sports. The schedule APIs provide more detailed information about upcoming games, team records, and scheduling details.

### Schedule API Endpoints

**Base URL:** `https://data.ncaa.com/casablanca/schedule/`

**Endpoint Pattern:** `/{sport}/{division}/{date}/schedule.json`

**Method:** `GET`

**Description:** Retrieves comprehensive schedule information for games on a specific date, including detailed team information, game times, venues, and scheduling metadata.

### Schedule API Parameters

| Parameter | Type | Required | Description | Possible Values |
|-----------|------|----------|-------------|-----------------|
| `sport` | string | Yes | The sport for which to retrieve the schedule | `basketball-men`, `basketball-women`, `soccer-women`, `soccer-men`, `football`, `baseball`, `softball`, etc. |
| `division` | string | Yes | The division level | `d1`, `d2`, `d3` |
| `date` | string | Yes | The date for which to retrieve the schedule | Format: `YYYY/MM/DD` |

### Schedule API Examples

#### Women's Soccer Schedule
```bash
curl "https://data.ncaa.com/casablanca/schedule/soccer-women/d1/2024/11/24/schedule.json"
```

#### Men's Basketball Schedule
```bash
curl "https://data.ncaa.com/casablanca/schedule/basketball-men/d1/2024/03/15/schedule.json"
```

#### Women's Basketball Schedule
```bash
curl "https://data.ncaa.com/casablanca/schedule/basketball-women/d1/2024/03/15/schedule.json"
```

#### Football Schedule
```bash
curl "https://data.ncaa.com/casablanca/schedule/football/d1/2024/09/15/schedule.json"
```

### Schedule API Response Structure

The schedule API returns a comprehensive JSON structure that includes detailed scheduling information, team records, and metadata:

```json
{
  "inputMD5Sum": "946b0d7ecce3877d6cd036a19daf95ed",
  "instanceId": "52aa051f77b7475da1baba2df45d5e98",
  "updated_at": "11-24-2024 15:30:45",
  "hideRank": false,
  "games": [
    {
      "game": {
        "gameID": "3146430",
        "startTime": "12:00PM ET",
        "startDate": "11-24-2024",
        "startTimeEpoch": "1700931600",
        "gameState": "scheduled",
        "url": "/game/3146430",
        "network": "ESPN+",
        "venue": "Michigan Stadium",
        "location": "Ann Arbor, MI",
        "attendance": null,
        "liveVideoEnabled": true,
        "videoState": "available",
        "home": {
          "names": {
            "full": "University of Michigan",
            "short": "Michigan",
            "seo": "michigan",
            "char6": "MICH"
          },
          "score": "0",
          "winner": false,
          "rank": "3",
          "seed": "2",
          "description": "(25-7)",
          "record": "25-7",
          "conferences": [
            {
              "conferenceName": "Big Ten",
              "conferenceSeo": "big-ten"
            }
          ]
        },
        "away": {
          "names": {
            "full": "The Ohio State University",
            "short": "Ohio St.",
            "seo": "ohio-st",
            "char6": "OHIOST"
          },
          "score": "0",
          "winner": false,
          "rank": "15",
          "seed": "7",
          "description": "(22-10)",
          "record": "22-10",
          "conferences": [
            {
              "conferenceName": "Big Ten",
              "conferenceSeo": "big-ten"
            }
          ]
        },
        "bracketRound": "1",
        "bracketId": "123",
        "bracketRegion": "East",
        "currentPeriod": 0,
        "contestClock": null,
        "title": "Michigan vs Ohio St.",
        "contestName": "Regular Season",
        "finalMessage": "",
        "weather": {
          "temperature": "45°F",
          "condition": "Partly Cloudy",
          "wind": "5 mph NW"
        }
      }
    }
  ]
}
```

### Key Differences: Schedule API vs Scoreboard API

| Feature | Scoreboard API | Schedule API |
|---------|----------------|--------------|
| **Primary Purpose** | Live scores and game status | Upcoming games and scheduling details |
| **Data Focus** | Real-time game data | Future scheduling and team records |
| **Venue Information** | Not included | Detailed venue and location data |
| **Weather Data** | Not included | Weather conditions for outdoor sports |
| **Attendance** | Not included | Current/final attendance numbers |
| **Video Streaming** | Basic video state | Detailed video availability and states |
| **Team Records** | Limited | Comprehensive season records |
| **Scheduling Metadata** | Basic | Detailed scheduling information |

### Schedule API Field Descriptions

#### Schedule-Specific Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `inputMD5Sum` | string | MD5 checksum of input parameters | `"946b0d7ecce3877d6cd036a19daf95ed"` |
| `instanceId` | string | Unique identifier for API response instance | `"52aa051f77b7475da1baba2df45d5e98"` |
| `updated_at` | string | Timestamp when data was last updated | `"11-24-2024 15:30:45"` |
| `hideRank` | boolean | Whether team rankings should be hidden | `false` |
| `venue` | string | Stadium/venue name where game is played | `"Michigan Stadium"` |
| `location` | string | City and state of venue | `"Ann Arbor, MI"` |
| `attendance` | integer/null | Current or final attendance number | `107601`, `null` |
| `liveVideoEnabled` | boolean | Whether live video streaming is available | `true`, `false` |
| `videoState` | string | Current state of video broadcast | `"available"`, `"unavailable"`, `"archived"` |
| `title` | string | Display title for the game matchup | `"Michigan vs Ohio St."` |
| `contestName` | string | Name of the contest or tournament | `"Regular Season"`, `"NCAA Tournament"` |
| `finalMessage` | string | Final status message | `"FINAL"`, `""`, `"POSTPONED"` |
| `weather` | object | Weather conditions for outdoor sports | See weather object below |
| `record` | string | Team's current season record | `"25-7"`, `"12-0"` |

#### Enhanced Team Information

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `seed` | string | Tournament seed (if applicable) | `"2"`, `"7"`, `null` |
| `conferences` | array | Array of conference objects | See conference structure below |

#### Conference Object Structure

```json
{
  "conferences": [
    {
      "conferenceName": "Big Ten",
      "conferenceSeo": "big-ten"
    },
    {
      "conferenceName": "Top 25",
      "conferenceSeo": "top-25"
    }
  ]
}
```

#### Weather Object Structure

```json
{
  "weather": {
    "temperature": "45°F",
    "condition": "Partly Cloudy",
    "wind": "5 mph NW",
    "humidity": "65%",
    "precipitation": "10%"
  }
}
```

#### Weather Object Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `temperature` | string | Current temperature at venue | `"45°F"`, `"72°F"` |
| `condition` | string | Weather condition description | `"Partly Cloudy"`, `"Sunny"`, `"Rain"` |
| `wind` | string | Wind speed and direction | `"5 mph NW"`, `"12 mph SW"` |
| `humidity` | string | Humidity percentage | `"65%"`, `"45%"` |
| `precipitation` | string | Chance of precipitation | `"10%"`, `"80%"` |

### Supported Sports

| Sport | API Value | Description |
|-------|-----------|-------------|
| Men's Basketball | `basketball-men` | Division I men's basketball |
| Women's Basketball | `basketball-women` | Division I women's basketball |
| Football | `football` | College football |
| Baseball | `baseball` | College baseball |
| Softball | `softball` | College softball |

### Supported Divisions

| Division | API Value | Description |
|----------|-----------|-------------|
| Division I | `d1` | Highest level of NCAA competition |
| Division II | `d2` | Second tier of NCAA competition |
| Division III | `d3` | Third tier of NCAA competition |

### Schedule Resource Game States

| State | Description |
|-------|-------------|
| `"scheduled"` | Game is scheduled but hasn't started |
| `"inprogress"` | Game is currently being played |
| `"final"` | Game has been completed |
| `"postponed"` | Game has been postponed |
| `"cancelled"` | Game has been cancelled |

### Schedule Resource Usage Examples

#### JavaScript Example with Error Handling
```javascript
const fetchNCAASchedule = async (sport, division, date) => {
  const url = `https://data.ncaa.com/casablanca/schedule/${sport}/${division}/${date}/schedule.json`;
  
  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.games || [];
  } catch (error) {
    console.error('Error fetching NCAA schedule:', error);
    throw error;
  }
};

// Usage examples
const womensSoccer = await fetchNCAASchedule('soccer-women', 'd1', '2024/11/24');
const mensBasketball = await fetchNCAASchedule('basketball-men', 'd1', '2024/03/15');
const womensBasketball = await fetchNCAASchedule('basketball-women', 'd1', '2024/03/15');
const football = await fetchNCAASchedule('football', 'd1', '2024/09/15');
```

#### Python Example with Caching
```python
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class NCAAScheduleAPI:
    def __init__(self):
        self.base_url = "https://data.ncaa.com/casablanca/schedule"
        self.cache = {}
        self.cache_duration = 300  # 5 minutes
    
    def get_schedule(self, sport: str, division: str, date: str) -> List[Dict]:
        """
        Get schedule for a specific sport, division, and date
        
        Args:
            sport: Sport type (e.g., 'soccer-women', 'basketball-men')
            division: Division level (e.g., 'd1')
            date: Date in YYYY/MM/DD format
        
        Returns:
            List of game objects
        """
        cache_key = f"{sport}_{division}_{date}"
        
        # Check cache
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            if datetime.now().timestamp() - timestamp < self.cache_duration:
                return cached_data
        
        url = f"{self.base_url}/{sport}/{division}/{date}/schedule.json"
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            games = data.get('games', [])
            
            # Cache the result
            self.cache[cache_key] = (games, datetime.now().timestamp())
            
            return games
        except requests.RequestException as e:
            print(f"Error fetching NCAA schedule: {e}")
            raise
    
    def get_todays_games(self, sport: str, division: str = 'd1') -> List[Dict]:
        """Get today's games for a specific sport"""
        today = datetime.now().strftime('%Y/%m/%d')
        return self.get_schedule(sport, division, today)
    
    def get_upcoming_games(self, sport: str, division: str = 'd1', days: int = 7) -> List[Dict]:
        """Get upcoming games for the next N days"""
        all_games = []
        
        for i in range(days):
            date = (datetime.now() + timedelta(days=i)).strftime('%Y/%m/%d')
            try:
                games = self.get_schedule(sport, division, date)
                all_games.extend(games)
            except Exception as e:
                print(f"Error fetching games for {date}: {e}")
                continue
        
        return all_games

    def get_weather_for_game(self, game: Dict) -> Optional[Dict]:
        """Extract weather information from a game object"""
        return game.get('game', {}).get('weather')

# Usage
api = NCAAScheduleAPI()
womens_soccer_schedule = api.get_schedule('soccer-women', 'd1', '2024/11/24')
todays_basketball = api.get_todays_games('basketball-men')
upcoming_football = api.get_upcoming_games('football', 'd1', 14)
```

#### React Hook for Schedule Data
```javascript
import { useState, useEffect } from 'react';

const useNCAASchedule = (sport, division, date) => {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSchedule = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(
          `https://data.ncaa.com/casablanca/schedule/${sport}/${division}/${date}/schedule.json`
        );
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setGames(data.games || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchSchedule();
  }, [sport, division, date]);

  return { games, loading, error };
};

// Usage in component
const SoccerSchedule = () => {
  const { games, loading, error } = useNCAASchedule('soccer-women', 'd1', '2024/11/24');

  if (loading) return <div>Loading schedule...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Women's Soccer Schedule</h2>
      {games.map((gameData, index) => (
        <div key={index} className="game-card">
          <h3>{gameData.game.away.names.short} vs {gameData.game.home.names.short}</h3>
          <p>Start Time: {gameData.game.startTime}</p>
          <p>Venue: {gameData.game.venue}, {gameData.game.location}</p>
          <p>Status: {gameData.game.gameState}</p>
          {gameData.game.network && <p>Network: {gameData.game.network}</p>}
          {gameData.game.weather && (
            <div className="weather-info">
              <p>Weather: {gameData.game.weather.condition} {gameData.game.weather.temperature}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
```

### Schedule Resource Caching Strategy

```javascript
class NCAAScheduleCache {
  constructor() {
    this.cache = new Map();
    this.defaultTTL = {
      scheduled: 60 * 60 * 1000,    // 1 hour for scheduled games
      inprogress: 30 * 1000,        // 30 seconds for live games
      final: 24 * 60 * 60 * 1000    // 24 hours for completed games
    };
  }

  getCacheKey(sport, division, date) {
    return `${sport}_${division}_${date}`;
  }

  get(sport, division, date) {
    const key = this.getCacheKey(sport, division, date);
    const cached = this.cache.get(key);
    
    if (!cached) return null;
    
    const { data, timestamp, gameState } = cached;
    const ttl = this.defaultTTL[gameState] || this.defaultTTL.scheduled;
    
    if (Date.now() - timestamp > ttl) {
      this.cache.delete(key);
      return null;
    }
    
    return data;
  }

  set(sport, division, date, data, gameState = 'scheduled') {
    const key = this.getCacheKey(sport, division, date);
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      gameState
    });
  }
}
```

### Schedule Resource Error Handling

```javascript
const handleScheduleAPIError = (error, sport, division, date) => {
  console.error(`Error fetching schedule for ${sport} ${division} on ${date}:`, error);
  
  // Implement retry logic
  if (error.status === 429) {
    // Rate limited - wait and retry
    setTimeout(() => {
      return fetchSchedule(sport, division, date);
    }, 5000);
  } else if (error.status >= 500) {
    // Server error - retry with exponential backoff
    const delay = Math.pow(2, retryCount) * 1000;
    setTimeout(() => {
      return fetchSchedule(sport, division, date);
    }, delay);
  }
  
  // Return fallback data or empty array
  return [];
};
```

## Related APIs

- **Game Details API**: `/game/{gameId}` - Detailed information about a specific game
- **Team Stats API**: `/team/{teamId}` - Team statistics and information
- **Player Stats API**: `/player/{playerId}` - Individual player statistics

## Support

For issues with the NCAA Casablanca API:
- Check the [NCAA official website](https://www.ncaa.com) for updates
- Monitor the API endpoint for changes
- Implement graceful degradation for API failures

---

**Last Updated**: September 25, 2024  
**API Version**: Current as of documentation date  
**Data Source**: NCAA Official API
