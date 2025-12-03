# NCAA Sports Data Pipeline

A Python library and Apache Airflow pipeline for extracting, transforming, and loading NCAA sports data.

## Features

- **CLI Tool**: Command-line interface for querying NCAA sports
- **Python Library**: Reusable modules for HTTP fetching, parsing, and data modeling
- **Airflow DAG**: Automated ETL pipeline with PostgreSQL storage
- **Docker Setup**: Containerized Airflow environment with local data persistence

## Project Structure

```
ncaa/
├── ncaa/                       # Core Python library
│   ├── __init__.py
│   ├── config.py              # Configuration (NCAA_BASE_URL)
│   ├── http_client.py         # HTTP fetching with error handling
│   ├── models.py              # Pydantic models (Sport, Season, Gender)
│   ├── parser.py              # HTML parsing logic
│   ├── parser_helpers.py      # Parser utilities
│   └── service.py             # Main service (get_ncaa_sports)
├── dags/                       # Airflow DAGs
│   ├── ncaa_sports_dag.py     # Simple example DAG
│   └── ncaa_sports_etl_dag.py # Full ETL pipeline
├── tests/                      # Test suite
├── data/                       # Local data storage (gitignored)
├── postgres_data/              # PostgreSQL data (gitignored)
├── logs/                       # Airflow logs (gitignored)
├── Dockerfile                  # Custom Airflow image
├── docker-compose.yml          # Airflow stack
├── init-db.sh                  # Database initialization
├── main.py                     # CLI entry point
└── pyproject.toml             # Python dependencies
```

## Quick Start

### Using the CLI

```bash
# Install dependencies
uv sync

# List all NCAA sports
python main.py sports

# Filter by season
python main.py sports --season Fall

# Filter by gender
python main.py sports --gender Women
```

### Using the Library

```python
from ncaa import get_ncaa_sports, Season, Gender

sports = get_ncaa_sports()

for sport in sports:
    print(f"{sport.season.value} | {sport.gender.value} | {sport.name}")
```

## Airflow Setup

### 1. Initialize and Start

```bash
# First time only
docker-compose up airflow-init

# Start Airflow
docker-compose up
```

### 2. Access Airflow UI

- URL: http://localhost:8080
- Username: `airflow`
- Password: `airflow`

### 3. Enable and Run DAG

The `ncaa_db` PostgreSQL connection is automatically configured on startup.

In the Airflow UI, toggle the `ncaa_sports_etl` DAG to enable it. It will run daily automatically, or click "Trigger DAG" to run immediately.

## DAGs

### `ncaa_sports_etl`

Full ETL pipeline that:
1. Creates PostgreSQL table with indexes
2. Extracts NCAA sports data from website
3. Saves raw JSON to `./data/` directory
4. Loads data into PostgreSQL (UPSERT)
5. Validates record count

**Schedule**: Daily  
**Documentation**: See [README-DAG.md](README-DAG.md)

### `ncaa_sports_dag`

Simple example that fetches and logs sports data.

## Data Storage

### PostgreSQL

**Connection from host machine**:
```bash
psql postgresql://ncaa:ncaa@localhost:5432/ncaa
```

**Query data**:
```sql
-- View all sports
SELECT * FROM ncaa_sports ORDER BY season, name;

-- Count by season
SELECT season, COUNT(*) FROM ncaa_sports GROUP BY season;

-- Count by gender
SELECT gender, COUNT(*) FROM ncaa_sports GROUP BY gender;
```

**Data location**: `./postgres_data/` (persisted locally)

### File Storage

Raw JSON files: `./data/ncaa_sports_YYYY-MM-DD.json`

## Development

### Running Tests

```bash
pytest tests/
```

### Project Dependencies

- **bs4**: HTML parsing
- **click**: CLI framework
- **pydantic**: Data validation and models
- **requests**: HTTP client
- **apache-airflow**: Workflow orchestration
- **apache-airflow-providers-postgres**: PostgreSQL integration

## Documentation

- [README-AIRFLOW.md](README-AIRFLOW.md) - Airflow setup and configuration
- [README-DAG.md](README-DAG.md) - ETL DAG documentation

## Cleanup

### Stop Airflow
```bash
docker-compose down
```

### Remove all data (WARNING: deletes everything)
```bash
docker-compose down --volumes --rmi all
rm -rf postgres_data/ logs/ data/
```

## License

[Add your license here]
