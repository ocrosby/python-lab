from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

from ncaa import get_ncaa_sports


def fetch_and_log_sports():
    sports = get_ncaa_sports()
    print(f"Fetched {len(sports)} NCAA sports")
    for sport in sports[:5]:
        print(f"  - {sport.season.value} | {sport.gender.value} | {sport.name}")
    return len(sports)


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ncaa_sports_etl',
    default_args=default_args,
    description='Fetch and process NCAA sports data',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['ncaa', 'sports'],
) as dag:
    
    fetch_sports_task = PythonOperator(
        task_id='fetch_ncaa_sports',
        python_callable=fetch_and_log_sports,
    )
    
    fetch_sports_task
