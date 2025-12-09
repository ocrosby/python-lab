# NCAA Casablanca API ETL DAG

## Overview

The `ncaa_casablanca_etl` DAG is a multi-stage pipeline that ingests live sports data from the NCAA Casablanca API every 15 minutes. It handles both scheduled games and live scores, making it ideal for real-time sports data analysis.

## Key Features

- **Multi-sport support**: Basketball (men's & women's), Football, Soccer
- **Real-time data**: Runs every 15 minutes to capture live game updates
- **Intelligent branching**: Only processes live scores when games are in progress
- **Data enrichment**: Adds computed fields like ranked matchups and conference games
- **Historical tracking**: Maintains live score history in separate table
- **Data quality validation**: Ensures data integrity after each run

## DAG Architecture

```
create_tables
    ├── extract_schedules ──→ transform_schedule_data ──→ load_schedules ──┐
    └── extract_live_scores ──→ check_live_games ──→                        ├──→ validate_data
                                   ├── load_live_scores ──────────────────┘
                                   └── skip_live_scores ───────────────────┘
```

## Task Descriptions

### 1. create_tables
Creates two main tables:
- **casablanca_games**: Scheduled games with venue, rankings, conference info
- **casablanca_live_scores**: Historical snapshots of live scores

### 2. extract_schedules
- Fetches upcoming schedules for the next 7 days
- Supports: Basketball (men/women), Football, Soccer
- Extracts: Teams, times, venues, rankings, conferences
- Saves raw data to: `/opt/airflow/data/schedules_{date}.json`

### 3. extract_live_scores
- Fetches current scoreboard for in-progress games
- Captures: Current scores, period, game clock
- Runs in parallel with schedule extraction
- Saves to: `/opt/airflow/data/live_scores_{date}.json`

### 4. check_live_games (Branch Operator)
- Checks if any live games exist
- **If live games exist** → `load_live_scores`
- **If no live games** → `skip_live_scores`

### 5. transform_schedule_data
Enriches schedule data with computed fields:
- `is_ranked_matchup`: Both teams ranked in top 25
- `is_conference_game`: Teams from same conference
- `game_date` / `game_time`: Parsed from Unix timestamp

### 6. load_schedules
- Inserts/updates games in PostgreSQL
- Uses UPSERT to handle duplicate games
- Updates scores and game state for existing games

### 7. load_live_scores
- Inserts live score snapshots
- Creates historical record of score changes
- Only runs when live games detected

### 8. skip_live_scores
- Placeholder task when no live games
- Allows DAG to complete successfully

### 9. validate_data
- Verifies record counts match extraction
- Runs quality checks:
  - Missing team names
  - Missing start times
  - Invalid scores (negative values)
- Triggers regardless of which load path was taken

## Schedule

- **Frequency**: Every 15 minutes (`*/15 * * * *`)
- **Rationale**: Captures live game updates without overloading API
- **Start Date**: 2025-01-01
- **Catchup**: False (only process current data)

## Database Schema

### casablanca_games
```sql
CREATE TABLE casablanca_games (
    id SERIAL PRIMARY KEY,
    game_id VARCHAR(255) NOT NULL,
    sport VARCHAR(100) NOT NULL,
    gender VARCHAR(20),
    home_team VARCHAR(255) NOT NULL,
    away_team VARCHAR(255) NOT NULL,
    home_score INTEGER,
    away_score INTEGER,
    game_state VARCHAR(50),
    start_time_epoch BIGINT,
    venue VARCHAR(255),
    location VARCHAR(255),
    network VARCHAR(100),
    home_rank INTEGER,
    away_rank INTEGER,
    home_conference VARCHAR(100),
    away_conference VARCHAR(100),
    is_ranked_matchup BOOLEAN DEFAULT FALSE,
    is_conference_game BOOLEAN DEFAULT FALSE,
    game_date DATE,
    game_time TIME,
    extracted_at DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(game_id, extracted_at)
);
```

**Indexes:**
- `sport` - Filter by sport type
- `game_state` - Find live/scheduled/completed games
- `game_date` - Query games by date
- `extracted_at` - Track data freshness
- `is_ranked_matchup` - Find top 25 matchups

### casablanca_live_scores
```sql
CREATE TABLE casablanca_live_scores (
    id SERIAL PRIMARY KEY,
    game_id VARCHAR(255) NOT NULL,
    sport VARCHAR(100) NOT NULL,
    home_team VARCHAR(255) NOT NULL,
    away_team VARCHAR(255) NOT NULL,
    home_score INTEGER NOT NULL,
    away_score INTEGER NOT NULL,
    game_state VARCHAR(50) NOT NULL,
    current_period INTEGER,
    contest_clock VARCHAR(20),
    start_time_epoch BIGINT,
    network VARCHAR(100),
    extracted_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Indexes:**
- `game_id` - Track score changes for specific games
- `extracted_at` - Time-series analysis

## Example Queries

### Find today's ranked matchups
```sql
SELECT 
    home_team,
    home_rank,
    away_team,
    away_rank,
    game_time,
    network
FROM casablanca_games
WHERE game_date = CURRENT_DATE
  AND is_ranked_matchup = true
ORDER BY game_time;
```

### Track live score changes for a game
```sql
SELECT 
    extracted_at,
    home_score,
    away_score,
    current_period,
    contest_clock
FROM casablanca_live_scores
WHERE game_id = 'basketball-men-1710518400'
ORDER BY extracted_at DESC;
```

### Find conference games by ranking
```sql
SELECT 
    home_team,
    away_team,
    home_conference,
    home_score,
    away_score
FROM casablanca_games
WHERE is_conference_game = true
  AND (home_rank IS NOT NULL OR away_rank IS NOT NULL)
  AND game_state = 'final'
ORDER BY game_date DESC
LIMIT 20;
```

### Live games summary
```sql
SELECT 
    sport,
    COUNT(*) as live_games,
    AVG(home_score + away_score) as avg_total_score
FROM casablanca_games
WHERE game_state IN ('in', 'inprogress')
  AND extracted_at = CURRENT_DATE
GROUP BY sport;
```

## Configuration

### Sports Configuration
Edit `extract_schedules()` to add/remove sports:

```python
sports_config = [
    {'sport': 'basketball-men', 'gender': 'men', 'days': 7},
    {'sport': 'basketball-women', 'gender': 'women', 'days': 7},
    {'sport': 'football', 'gender': None, 'days': 7},
    {'sport': 'soccer-men', 'gender': 'men', 'days': 7},      # Add this
    {'sport': 'soccer-women', 'gender': 'women', 'days': 7},  # Add this
]
```

### Adjust Schedule Frequency
To change from every 15 minutes:

```python
schedule_interval='*/30 * * * *',  # Every 30 minutes
# OR
schedule_interval='0 * * * *',      # Every hour
# OR
schedule_interval='@hourly',        # Every hour (alternative)
```

## Monitoring

### Key Metrics to Watch
- **Schedule extraction count**: Should increase as new games are scheduled
- **Live games count**: Varies by time of day (peak during game times)
- **Validation failures**: Should be 0 (investigate if > 0)
- **Task duration**: Should be < 2 minutes per run

### Alerts to Set Up
1. **Validation failures** → indicates data quality issues
2. **Extract tasks failing** → API might be down or rate limited
3. **No live games for 24+ hours** → might indicate extraction issues
4. **Duplicate game IDs** → check game_id generation logic

## Data Freshness

- **Schedules**: Updated every 15 minutes, captures new games as they're scheduled
- **Live scores**: 15-minute snapshots during games provide near real-time tracking
- **Game states**: Automatically updated when games start/finish

## Use Cases

### Real-Time Dashboards
Query `casablanca_games` for current game states and scores

### Score Change Analytics
Analyze `casablanca_live_scores` for momentum shifts and scoring patterns

### Schedule Planning
Query upcoming `game_date` and `game_time` for content planning

### Ranking Tracking
Monitor `home_rank` and `away_rank` changes over time

### Conference Analysis
Analyze `is_conference_game` for conference strength metrics

## Error Handling

- **Retries**: 3 attempts with 2-minute delays
- **Partial failures**: Continues processing other sports if one fails
- **Branch logic**: Gracefully handles zero live games
- **Idempotent**: Safe to re-run (UPSERT prevents duplicates)

## Troubleshooting

### No data in casablanca_games
1. Check `extract_schedules` task logs
2. Verify Casablanca API is accessible
3. Check date format in API calls (must be YYYY/MM/DD)

### Live scores not updating
1. Check `check_live_games` task output
2. Verify games are actually in progress
3. Check `extract_live_scores` task logs

### Validation failures
1. Check validation task logs for specific quality issues
2. Compare `schedules_count` XCom with database records
3. Look for extraction errors in earlier tasks

## Next Steps

### Enhancements to Consider
1. **Add more sports**: Baseball, softball, soccer (requires API changes)
2. **Player statistics**: Extract individual player data
3. **Weather data**: Store weather conditions for outdoor sports
4. **Video availability**: Track streaming links
5. **Bracket tracking**: Enhanced tournament round tracking
6. **Alert system**: Email/Slack notifications for ranked matchups
7. **Archive old data**: Partition historical data by season

## References

- [Casablanca API Documentation](README-CASABLANCA.md)
- [Airflow Setup](README-AIRFLOW.md)
- [Original NCAA DAG](README-DAG.md)
