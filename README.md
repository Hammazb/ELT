# ELT Pipeline with Airbyte, Airflow, dbt & Docker

A fully containerized ELT (Extract, Load, Transform) pipeline that moves data from a PostgreSQL source database to a destination database, orchestrated by Apache Airflow, synced via Airbyte, and transformed using dbt.

---

## Architecture Overview

```
Source PostgreSQL (port 5433)
        |
        |  [Airbyte Sync]
        v
Destination PostgreSQL (port 5434)
        |
        |  [dbt Transformations]
        v
Transformed Tables (views/materialized)
        |
        ^ (entire pipeline orchestrated by Apache Airflow)
```

---

## Tech Stack

| Tool | Role |
|------|------|
| **Docker & Docker Compose** | Containerizes all services |
| **Airbyte** | Extracts and loads data from source to destination Postgres |
| **Apache Airflow** | Orchestrates and schedules the ELT pipeline |
| **dbt** | Transforms raw data in the destination database |
| **PostgreSQL** | Source and destination databases |

---

## Project Structure

```
elt/
├── airflow/
│   └── dags/
│       └── elt_dag.py          # Airflow DAG: triggers Airbyte sync then dbt run
├── custom_postgres/             # dbt project
│   ├── models/
│   ├── dbt_project.yml
│   └── ...
├── elt/
│   └── elt_script.py           # Standalone ELT script (pg_dump / psql)
├── source_db_init/
│   └── init.sql                # Seeds source DB with users, films, actors data
├── airbyte/                    # Airbyte platform files
├── Dockerfile                  # Custom Airflow image with Airbyte & Docker providers
├── docker-compose.yaml         # All services: Postgres, Airflow, Airbyte
├── profiles.yml                # dbt connection profile
├── start.sh                    # Startup script
└── stop.sh                     # Shutdown script
```

---

## How It Works

### 1. Docker
All services are defined in `docker-compose.yaml` and run on a shared `elt_network`:
- **source_postgres** — source database seeded with `users`, `films`, `film_category`, `film_actors`, and `actors` tables
- **destination_postgres** — destination database where data lands after the Airbyte sync
- **Airflow** (webserver, scheduler, dag-processor, init) — orchestration layer
- **Airbyte** — spun up separately via `start.sh`

### 2. Airbyte
Airbyte handles the **Extract & Load** step. It connects to `source_postgres` and syncs data into `destination_postgres`. The connection is configured through the Airbyte UI (accessible at `http://localhost:8000` after startup).

The Airflow DAG triggers the Airbyte sync using the `AirbyteTriggerSyncOperator`, which waits for the sync to complete before proceeding.

### 3. Apache Airflow
The DAG (`elt_and_dbt`) in `airflow/dags/elt_dag.py` defines two tasks:

```
t1 (Airbyte Sync) >> t2 (dbt Run)
```

- **t1** — triggers the Airbyte connection to sync data from source to destination Postgres
- **t2** — runs dbt inside a Docker container to apply transformations on the loaded data

Airflow is accessible at `http://localhost:8080` (username: `airflow`, password: `password`).

### 4. dbt
dbt handles the **Transform** step. It connects to `destination_postgres` and runs SQL models defined in `custom_postgres/models/`. Models are materialized as tables and run with `--full-refresh` on each pipeline execution.

The dbt profile (`profiles.yml`) targets the destination database:
- Host: `destination_postgres`
- Database: `destination_db`
- Schema: `public`

---

## Source Data

The source database (`source_db`) is seeded with movie-related data:

- `users` — 14 users with name, email, and date of birth
- `films` — 20 films with title, release date, price, rating, and user rating
- `film_category` — genre categories per film
- `actors` — 20 actors
- `film_actors` — join table linking films to actors

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- dbt profile configured at `~/.dbt/profiles.yml`

### Start the Pipeline

```bash
./start.sh
```

This will:
1. Initialize the Airflow database and create an admin user
2. Start all Docker Compose services (Airflow, Postgres)
3. Start Airbyte

### Access the UIs

| Service | URL | Credentials |
|---------|-----|-------------|
| Airflow | http://localhost:8080 | airflow / password |
| Airbyte | http://localhost:8000 | (set on first login) |

### Stop the Pipeline

```bash
./stop.sh
```

---

## Airflow DAG

The `elt_and_dbt` DAG runs the full pipeline:

1. **airbyte_postgres_postgres** — triggers the configured Airbyte sync connection
2. **dbt_run** — runs dbt models inside a Docker container against the destination database

To activate, set the Airbyte `connection_id` in `airflow/dags/elt_dag.py` and enable the DAG in the Airflow UI.
