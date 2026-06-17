# Architecture

## System Overview

The FMCG Conversational Analytics Platform is a full-stack application that enables business users to query sales data using natural language.

```mermaid
graph TB
    subgraph Client
        UI[React Frontend<br/>Vite + Tailwind]
        Charts[Recharts Dashboard]
        Chat[Chat Interface]
    end

    subgraph Server
        API[FastAPI Backend]
        Validator[SQL Validator]
        Executor[SQL Executor]
        LLM[Gemini 2.5 Flash]
        Loader[CSV Loader]
    end

    subgraph Storage
        SQLite[(SQLite DB)]
        CSV[FMCG CSV Dataset]
        History[(Query History)]
        Memory[(Conversation Memory)]
    end

    Chat --> UI
    UI -->|/api proxy| API
    Charts --> UI
    API --> LLM
    API --> Validator
    Validator --> Executor
    Executor --> SQLite
    Loader --> CSV
    Loader --> SQLite
    API --> History
    API --> Memory
```

## Component Responsibilities

### Frontend (React + Vite)

| Component | Responsibility |
|-----------|----------------|
| `ChatWindow` | User input, message display, suggestions |
| `Sidebar` | Query history, new conversation |
| `SQLViewer` | Display generated SQL with copy |
| `ResultsTable` | Tabular query results |
| `DashboardCharts` | Auto-generated bar/line/pie charts |
| `ExecutiveSummary` | AI-generated business insights |
| `LoadingSpinner` | Loading states |

### Backend (FastAPI)

| Module | Responsibility |
|--------|----------------|
| `main.py` | REST endpoints, request orchestration |
| `llm.py` | Gemini SQL generation & summaries |
| `validator.py` | SELECT-only SQL enforcement |
| `sql_generator.py` | NL→SQL pipeline & execution |
| `csv_loader.py` | Auto-load CSV on startup |
| `models.py` | Sales, history, conversation ORM |

## Data Flow

```mermaid
flowchart LR
    A[User Question] --> B[Conversation Memory]
    B --> C[Gemini SQL Generation]
    C --> D[SQL Validator]
    D -->|Valid| E[Execute on SQLite]
    D -->|Invalid| F[Error Response]
    E --> G[Results]
    G --> H[Gemini Summary]
    H --> I[Store History]
    I --> J[JSON Response]
    J --> K[Frontend Render]
```

## Security

- **SQL Injection Prevention**: Only SELECT/WITH queries allowed
- **Blocked Keywords**: DROP, DELETE, UPDATE, INSERT, ALTER, TRUNCATE, CREATE, etc.
- **Single Statement**: Semicolons in query body rejected
- **API Key**: Gemini key stored in environment variables only

## Database Schema

```mermaid
erDiagram
    sales_transactions {
        int id PK
        string transaction_id
        string date
        string product_id
        string product_name
        string category
        string brand
        float unit_price
        string store_id
        string region
        string city
        int units_sold
        float revenue
        bool promotion_flag
        int stock_level
        bool stockout_flag
    }

    query_history {
        int id PK
        string session_id
        text user_question
        text generated_sql
        text executive_summary
        int row_count
        bool success
        text error_message
        datetime created_at
    }

    conversation_messages {
        int id PK
        string session_id
        string role
        text content
        datetime created_at
    }
```
