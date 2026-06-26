from datetime import datetime
from airflow import DAG
from docker.types import Mount
from airflow.utils.dates import days_ago
from airflow.provider.airbyte.operatiors.airbyte import AirbyteTriggerSyncOperator

from airflow.providers.docker.operators.docker import DockerOperator
import subprocess


CONN_ID = ''


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
}




dag = DAG(
    'elt_and_dbt',
    default_args=default_args,
    description='An ELT workflow with dbt',
    start_date=datetime(2026, 6, 25),
    catchup=False,
)

t1 = AirbyteTriggerSyncOperator(
    task_id='airbyte_postgres_postgres',
    airbyte_conn_id='airbyte',
    connection_id = CONN_ID,
    asynchronous=False,
    timeout=3600,
    wait_seconds=3,
    dag=dag,
)

t2 = DockerOperator(
    task_id='dbt_run',
    image='ghcr.io/dbt-labs/dbt-postgres:1.4.7',
    command=[
        "run",
        "--profiles-dir",
        "/root",
        "--project-dir",
        "/dbt",
        "--full-refresh"
    ],
    auto_remove='success',
    mount_tmp_dir=False,
    docker_url="unix:///var/run/docker.sock",
    network_mode="elt_elt_network",
    mounts=[
        Mount(source='/Users/hammazbuksh/elt/custom_postgres',
              target='/dbt', type='bind'),
        Mount(source='/Users/hammazbuksh/.dbt', target='/root', type='bind'),
    ],
    dag=dag
)

t1 >> t2