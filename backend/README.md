# Backend Setup

## 1) Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

## 2) Configure environment

```bash
cd backend
cp .env.example .env
```

Default configuration is Docker-first and expects PostgreSQL on `127.0.0.1:55432`.

## 3) Start PostgreSQL (Docker)

```bash
cd backend
docker compose up -d
```

## 4) Validate DB connectivity

```bash
cd backend
python scripts/check_db.py
```

The script logs a sanitized DB target (`host`, `port`, `database`, `username`) and never prints the password.

## 5) Apply migrations

```bash
cd backend
python scripts/apply_migrations.py
```

## 6) Confirm required tables

```bash
cd backend
python scripts/check_db.py --require-tables users,user_settings,subjects,tasks
```

To validate event-tracking schema drift (for example `app_events` missing columns):

```bash
cd backend
python scripts/check_db.py --check-events-schema
```

## 7) Run API

```bash
cd backend
uvicorn app.main:app --reload
```

## 8) Health checks

- API health: `http://127.0.0.1:8000/health`
- DB health: `http://127.0.0.1:8000/health/db`

## Local PostgreSQL (optional)

If you prefer local PostgreSQL instead of Docker, make sure the configured role/database exist and match `.env` values.

Example SQL (run as a superuser in local PostgreSQL):

```sql
CREATE ROLE neurolearn WITH LOGIN PASSWORD 'neurolearn';
CREATE DATABASE neurolearn OWNER neurolearn;
GRANT ALL PRIVILEGES ON DATABASE neurolearn TO neurolearn;
```

## Diagnose port conflicts (`5432`)

This project intentionally maps Docker PostgreSQL to host port `55432` to avoid conflicts with local PostgreSQL services on `5432`.

```bash
# Check local listeners
netstat -ano | findstr :5432
netstat -ano | findstr :55432

# Check container state
docker ps --filter name=neurolearn-postgres
```
