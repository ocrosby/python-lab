#!/bin/bash
set -e

echo "Waiting for Airflow to be ready..."
sleep 10

echo "Creating NCAA database connection..."
airflow connections delete 'ncaa_db' 2>/dev/null || true

airflow connections add 'ncaa_db' \
    --conn-type 'postgres' \
    --conn-host 'postgres' \
    --conn-schema 'ncaa' \
    --conn-login 'ncaa' \
    --conn-password 'ncaa' \
    --conn-port 5432

echo "NCAA database connection configured successfully!"
