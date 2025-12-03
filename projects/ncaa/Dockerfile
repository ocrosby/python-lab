FROM apache/airflow:2.10.4-python3.12

USER airflow

COPY pyproject.toml uv.lock ./
COPY ncaa/ ./ncaa/

RUN pip install --no-cache-dir \
    apache-airflow-providers-postgres==5.12.0 \
    beautifulsoup4==4.12.3 \
    click==8.3.1 \
    pydantic==2.12.5 \
    requests==2.32.5 \
    psycopg2-binary==2.9.9 \
    && pip install -e .

COPY dags/ /opt/airflow/dags/
