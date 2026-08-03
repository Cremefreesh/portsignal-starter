# PortSignal

A portfolio intelligence and personalised financial-news platform.

## Starter features

- FastAPI backend
- React + TypeScript frontend
- Portfolio and position models
- Annualised return and volatility
- Beta and CAPM-implied return
- Sharpe ratio
- Maximum drawdown
- Historical Value at Risk
- Concentration analysis
- Explainable market fear-and-greed scaffold
- Supabase-ready PostgreSQL schema
- News and notification schema
- Demo dashboard

## Start the backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Swagger: http://localhost:8000/docs

## Start the frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend: http://localhost:5173

## Supabase

Create a Supabase project and run:

```text
supabase/migrations/001_initial_schema.sql
```

in the Supabase SQL editor.

The initial app deliberately uses demo data. The next milestone is replacing
that data with persisted transactions and live adjusted closing prices.
