# NCAA Sports ETL DAG

## Overview

The `ncaa_sports_etl` DAG extracts NCAA sports data from the NCAA website, transforms it, and loads it into PostgreSQL.

## DAG Tasks

```
create_table → extract_sports → load_sports → validate_data
```

### 1. create_table
Creates the `ncaa_sports` table if it doesn't exist with indexes on:
- season
- gender
- extracted_at

### 2. extract_sports
- Fetches sports data using `get_ncaa_sports()` from the ncaa library
- Saves raw JSON to `/opt/airflow/data/ncaa_sports_{date}.json`
- Pushes sports count to XCom for validation

### 3. load_sports
- Reads extracted JSON file
- Inserts/updates records in PostgreSQL
- Uses UPSERT to handle duplicates (by name, season, gender)

### 4. validate_data
- Verifies record count matches extraction
- Fails the DAG if counts don't match

## Schedule

- **Frequency**: Daily (`@daily`)
- **Start Date**: 2025-01-01
- **Catchup**: False

## Database Schema

```sql
CREATE TABLE ncaa_sports (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    season VARCHAR(50) NOT NULL,
    gender VARCHAR(50) NOT NULL,
    url TEXT,
    extracted_at DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name, season, gender)
);
```

## Configuration

The PostgreSQL connection (`ncaa_db`) is automatically configured when you run `docker-compose up`. No manual setup required!

## Querying the Data

```sql
-- Connect to database
psql postgresql://ncaa:ncaa@localhost:5432/ncaa

-- View all sports
SELECT * FROM ncaa_sports ORDER BY season, name;

-- Count by season
SELECT season, COUNT(*) FROM ncaa_sports GROUP BY season;

-- Latest extraction
SELECT MAX(extracted_at) FROM ncaa_sports;
```

## Monitoring

- **Task Logs**: Check individual task logs in Airflow UI
- **Data Files**: Located in `./data/ncaa_sports_YYYY-MM-DD.json`
- **Validation**: Automatically checks record counts after load

## Error Handling

- **Retries**: 2 retries with 5-minute delay
- **Validation**: Fails DAG if record count mismatch
- **Idempotent**: Safe to re-run (uses UPSERT)
