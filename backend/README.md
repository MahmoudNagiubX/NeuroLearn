# Backend Runtime (Minimal)

## 1) Start PostgreSQL

```bash
docker compose -f backend/docker-compose.yml up -d
```

## 2) Install dependencies

```bash
cd backend
pip install -r requirements.txt
```

## 3) Configure environment

```bash
cd backend
cp .env.example .env
```

## 4) Run API locally

```bash
cd backend
uvicorn app.main:app --reload
```

## 5) Health check

Open `http://127.0.0.1:8000/health`.
