#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER ncaa WITH PASSWORD 'ncaa';
    CREATE DATABASE ncaa;
    GRANT ALL PRIVILEGES ON DATABASE ncaa TO ncaa;
EOSQL
