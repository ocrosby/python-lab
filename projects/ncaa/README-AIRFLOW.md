# NCAA Sports Airflow Setup

## Quick Start

### 1. Initialize Airflow
```bash
docker-compose up airflow-init
```

### 2. Start Airflow
```bash
docker-compose up
```

The setup automatically:
- Creates PostgreSQL databases (airflow and ncaa)
- Initializes Airflow metadata
- Configures the `ncaa_db` connection
- Starts webserver and scheduler

### 3. Access Services
- **Airflow UI**: http://localhost:8080
  - Username: `airflow`
  - Password: `airflow`
- **PostgreSQL**: localhost:5432
  - Airflow DB: `airflow` / `airflow` / `airflow`
  - NCAA DB: `ncaa` / `ncaa` / `ncaa`

The DAGs are ready to run immediately - no manual connection configuration required!

### 4. Stop Airflow
```bash
docker-compose down
```

### 5. Clean Everything (WARNING: deletes local data)
```bash
docker-compose down --volumes --rmi all
rm -rf postgres_data/ logs/ data/
```

## Data Storage

All data is persisted locally in:
- `postgres_data/` - PostgreSQL database files (both Airflow metadata and NCAA data)
- `data/` - Any file-based storage from DAGs
- `logs/` - Airflow task logs

The NCAA database is automatically created with:
- Database: `ncaa`
- User: `ncaa`
- Password: `ncaa`
- Connection string: `postgresql+psycopg2://ncaa:ncaa@postgres/ncaa`

Available as environment variable `NCAA_DB_CONN` in all Airflow containers.

## Structure

```
.
├── Dockerfile              # Custom Airflow image with ncaa package
├── docker-compose.yml      # Airflow services (webserver, scheduler, db)
├── init-db.sh              # Creates ncaa database on first run
├── dags/                   # Your DAG definitions
│   └── ncaa_sports_dag.py  # Sample DAG
├── ncaa/                   # Your core library (imported by DAGs)
├── postgres_data/          # Persistent PostgreSQL data (gitignored)
├── data/                   # Persistent file storage (gitignored)
├── logs/                   # Airflow logs (gitignored)
└── .env                    # Environment variables
```

## Connecting to PostgreSQL

### From DAGs
```python
import os
conn_string = os.environ['NCAA_DB_CONN']
```

### From your machine
```bash
psql postgresql://ncaa:ncaa@localhost:5432/ncaa
```

### From other tools
- Host: `localhost`
- Port: `5432`
- Database: `ncaa`
- User: `ncaa`
- Password: `ncaa`

## Sample DAG

The included `ncaa_sports_dag.py` demonstrates:
- Daily schedule
- Using your `ncaa` package
- Fetching and logging NCAA sports data

## Next Steps

1. Modify `dags/ncaa_sports_dag.py` to store data in PostgreSQL
2. Add data validation tasks
3. Add SQLAlchemy models for your NCAA tables
4. Configure alerts and monitoring
