from datetime import datetime, timedelta
from pathlib import Path
import json
import os

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from ncaa import get_ncaa_sports, Sport


def extract_ncaa_sports(**context):
    try:
        sports = get_ncaa_sports()
        sports_data = [
            {
                'name': sport.name,
                'season': sport.season.value,
                'gender': sport.gender.value,
                'url': str(sport.url) if sport.url else None
            }
            for sport in sports
        ]
        
        data_dir = Path('/opt/airflow/data')
        data_dir.mkdir(exist_ok=True)
        
        output_file = data_dir / f"ncaa_sports_{context['ds']}.json"
        with open(output_file, 'w') as f:
            json.dump(sports_data, f, indent=2)
        
        context['task_instance'].xcom_push(key='sports_count', value=len(sports_data))
        context['task_instance'].xcom_push(key='output_file', value=str(output_file))
        
        return len(sports_data)
    
    except Exception as exc:
        raise RuntimeError(f"Failed to extract NCAA sports: {exc}") from exc


def transform_and_load(**context):
    try:
        sports_count = context['task_instance'].xcom_pull(
            task_ids='extract_sports',
            key='sports_count'
        )
        output_file = context['task_instance'].xcom_pull(
            task_ids='extract_sports',
            key='output_file'
        )
        
        if not output_file or not Path(output_file).exists():
            raise FileNotFoundError(f"Output file not found: {output_file}")
        
        with open(output_file, 'r') as f:
            sports_data = json.load(f)
        
        hook = PostgresHook(postgres_conn_id='ncaa_db')
        
        insert_query = """
            INSERT INTO ncaa_sports (name, season, gender, url, extracted_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (name, season, gender) 
            DO UPDATE SET 
                url = EXCLUDED.url,
                extracted_at = EXCLUDED.extracted_at;
        """
        
        extracted_at = context['ds']
        conn = hook.get_conn()
        
        try:
            with conn.cursor() as cursor:
                for sport in sports_data:
                    cursor.execute(
                        insert_query,
                        (
                            sport['name'],
                            sport['season'],
                            sport['gender'],
                            sport['url'],
                            extracted_at
                        )
                    )
                conn.commit()
        except Exception as db_error:
            conn.rollback()
            raise RuntimeError(f"Database transaction failed: {db_error}") from db_error
        finally:
            conn.close()
        
        return sports_count
    
    except FileNotFoundError as fnf_error:
        raise RuntimeError(f"File error in transform_and_load: {fnf_error}") from fnf_error
    except json.JSONDecodeError as json_error:
        raise RuntimeError(f"JSON parsing error: {json_error}") from json_error
    except Exception as exc:
        raise RuntimeError(f"Unexpected error in transform_and_load: {exc}") from exc


def validate_data(**context):
    try:
        hook = PostgresHook(postgres_conn_id='ncaa_db')
        
        result = hook.get_first(
            "SELECT COUNT(*) FROM ncaa_sports WHERE extracted_at = %s",
            parameters=(context['ds'],)
        )
        
        count = result[0] if result else 0
        expected_count = context['task_instance'].xcom_pull(
            task_ids='extract_sports',
            key='sports_count'
        )
        
        if count != expected_count:
            raise ValueError(
                f"Validation failed: expected {expected_count} records, found {count}"
            )
        
        return count
    
    except ValueError:
        raise
    except Exception as exc:
        raise RuntimeError(f"Validation error: {exc}") from exc


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ncaa_sports_etl',
    default_args=default_args,
    description='Extract NCAA sports data, transform and load to PostgreSQL',
    schedule_interval='@daily',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['ncaa', 'sports', 'etl'],
) as dag:
    
    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='ncaa_db',
        sql="""
            CREATE TABLE IF NOT EXISTS ncaa_sports (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                season VARCHAR(50) NOT NULL,
                gender VARCHAR(50) NOT NULL,
                url TEXT,
                extracted_at DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, season, gender)
            );
            
            CREATE INDEX IF NOT EXISTS idx_ncaa_sports_season 
                ON ncaa_sports(season);
            CREATE INDEX IF NOT EXISTS idx_ncaa_sports_gender 
                ON ncaa_sports(gender);
            CREATE INDEX IF NOT EXISTS idx_ncaa_sports_extracted_at 
                ON ncaa_sports(extracted_at);
        """
    )
    
    extract_sports = PythonOperator(
        task_id='extract_sports',
        python_callable=extract_ncaa_sports,
    )
    
    load_sports = PythonOperator(
        task_id='load_sports',
        python_callable=transform_and_load,
    )
    
    validate = PythonOperator(
        task_id='validate_data',
        python_callable=validate_data,
    )
    
    create_table >> extract_sports >> load_sports >> validate
