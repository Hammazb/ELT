import subprocess
import os
import time

def wait_for_postgres(host, max_retries=5, delay_seconds=5):
    retries = 0
    while retries < max_retries:
        try:
            result = subprocess.run(
                ["pg_isready", "-h", host], check = True, capture_output=True, text=True)
            if "accepting connections" in result.stdout:
                print ("Successfully connected to PostgreSQL.")
                return True
        except subprocess.CalledProcessError as e:
            print (f"Error connecting to Postgres: {e}")
            retries += 1
            print(f"Retrying in {delay_seconds} seconds... (Attempt {retries}/{max_retries})")
            time.sleep(delay_seconds)
    print ("Failed to connect to PostgreSQL after multiple attempts.")
    return False

if not wait_for_postgres(host="source_postgres"):
    exit(1)

print("Starting the ETL process...")

source_config = {
    'dbname':'source_db',
    'user': 'postgres',
    'password': 'secret',
    'host': 'source_postgres'
}


destination_config = {
    'dbname':'destination_db',
    'user': 'postgres',
    'password': 'secret',
    'host': 'destination_postgres'
}

dump_command = [
    'pg_dump',
    '-h', source_config['host'],
    '-U', source_config['user'],
    '-d', source_config['dbname'],
    '-f', 'data_dump.sql',
    '-w'
]

source_env = {**os.environ, 'PGPASSWORD': source_config['password']}

subprocess.run(dump_command, env=source_env, check=True)

load_command = [
    'psql',
    '-h', destination_config['host'],
    '-U', destination_config['user'],
    '-d', destination_config['dbname'],
    '-a', '-f', 'data_dump.sql',
]

destination_env = {**os.environ, 'PGPASSWORD': destination_config['password']}

subprocess.run(load_command, env=destination_env, check=True)

print("Ending ELT SCRIPT")

    
