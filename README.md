# FMCG Conversational Analytics Platform

A production-ready analytics platform that lets business users ask natural language questions about FMCG sales, inventory, products, regions, stores, and promotions. The system converts questions to SQL, validates and executes queries, and returns AI-generated executive summaries with interactive charts.

## Project Overview

- **Frontend**: React (Vite), Tailwind CSS, Recharts, Axios
- **Backend**: FastAPI, SQLAlchemy, Pandas, Pydantic
- **Database**: SQLite (auto-loaded from CSV on startup)
- **AI**: Google Gemini 2.5 Flash (falls back to 2.0 Flash)

### Core Features

1. Natural Language → SQL generation
2. SQL validation (SELECT-only; blocks destructive statements)
3. SQL execution against SQLite
4. AI executive summaries
5. Generated SQL viewer
6. Results table with pagination preview
7. Auto-generated dashboard charts
8. Query history sidebar
9. Conversation memory per session
10. CSV export
11. Loading states and error handling
12. Responsive mobile UI
13. Health check endpoint

## Architecture

```
┌─────────────┐     HTTP/REST      ┌─────────────┐     SQL      ┌──────────────┐
│   React UI  │ ◄──────────────► │   FastAPI   │ ◄──────────► │   SQLite DB  │
│  (Vite:5173)│   /api proxy     │  (port 8000)│              │ sales_trans. │
└─────────────┘                  └──────┬──────┘              └──────────────┘
                                        │
                                        ▼
                                 ┌─────────────┐
                                 │   Gemini    │
                                 │  2.5 Flash  │
                                 └─────────────┘
```

See [docs/architecture.md](docs/architecture.md) for detailed diagrams.

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- Google Gemini API key ([Google AI Studio](https://aistudio.google.com/apikey))

### 1. Backend Setup

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Edit `backend/.env` and set your API key:

```
GEMINI_API_KEY=your_actual_api_key
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

### 3. Dataset

The CSV dataset is located at `data/fmcg_conversational_ai_dataset.csv`. It is automatically loaded into SQLite on first backend startup.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | — | Google Gemini API key (required for chat) |
| `DATABASE_URL` | `sqlite:///./fmcg_analytics.db` | SQLAlchemy database URL |
| `CSV_PATH` | `../data/fmcg_conversational_ai_dataset.csv` | Path to FMCG dataset |

## Run Commands

**Terminal 1 — Backend:**

```bash
cd backend
uvicorn main:app --reload --port 8000
```

**Terminal 2 — Frontend:**

```bash
cd frontend
npm run dev
```

Open [http://localhost:5173](http://localhost:5173)

## API Documentation

Interactive docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health, record count, Gemini status |
| `POST` | `/chat` | Natural language query → SQL + results + summary |
| `GET` | `/history` | Query history (optional `session_id` filter) |
| `GET` | `/export` | Export query results as CSV (`sql` query param) |

### POST /chat

**Request:**
```json
{
  "question": "What is total revenue by region?",
  "session_id": "session_abc123"
}
```

**Response:**
```json
{
  "session_id": "session_abc123",
  "question": "What is total revenue by region?",
  "generated_sql": "SELECT region, SUM(revenue) ...",
  "results": [{"region": "North", "total_revenue": 150000}],
  "columns": ["region", "total_revenue"],
  "row_count": 4,
  "executive_summary": "North region leads with...",
  "success": true,
  "history_id": 1
}
```

## Deployment Guide

See [docs/deployment.md](docs/deployment.md) for production deployment with Docker, Nginx, and environment configuration.

## Project Structure

```
FMCG-Analytics-Platform/
├── backend/
│   ├── main.py              # FastAPI app & endpoints
│   ├── database.py            # SQLAlchemy setup
│   ├── models.py              # ORM models
│   ├── schemas.py             # Pydantic schemas
│   ├── llm.py                 # Gemini integration
│   ├── sql_generator.py       # NL→SQL pipeline
│   ├── validator.py           # SQL safety checks
│   ├── csv_loader.py          # CSV → SQLite loader
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── pages/HomePage.jsx
│   │   └── components/
│   └── package.json
├── data/
│   └── fmcg_conversational_ai_dataset.csv
└── docs/
```

## License

MIT
