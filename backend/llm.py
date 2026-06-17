import os
import re

from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

MODEL_NAME = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-2.0-flash"


def _get_api_key() -> str | None:
    return os.getenv("GEMINI_API_KEY")


def is_gemini_configured() -> bool:
    key = _get_api_key()
    return bool(key and key.strip() and key != "your_gemini_api_key_here")


def _get_model():
    api_key = _get_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured.")
    genai.configure(api_key=api_key)
    try:
        return genai.GenerativeModel(MODEL_NAME)
    except Exception:
        return genai.GenerativeModel(FALLBACK_MODEL)


def _extract_sql(text: str) -> str:
    match = re.search(r"```sql\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"```\s*(SELECT.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    cleaned = text.strip()
    if cleaned.upper().startswith(("SELECT", "WITH")):
        return cleaned.rstrip(";")
    return cleaned


SQL_SCHEMA_CONTEXT = """
Database: SQLite
Table: sales_transactions

Columns:
- id (INTEGER, primary key)
- transaction_id (TEXT) - unique transaction identifier
- date (TEXT) - format YYYY-MM-DD
- product_id (TEXT)
- product_name (TEXT)
- category (TEXT) - e.g. Beverage, Snacks, Bakery
- brand (TEXT)
- unit_price (REAL) - price per unit
- store_id (TEXT) - e.g. S001, S002
- region (TEXT) - North, South, East, West
- city (TEXT) - Mumbai, Delhi, Hyderabad, Kolkata, Bengaluru
- units_sold (INTEGER)
- revenue (REAL)
- promotion_flag (BOOLEAN) - 0 or 1 in SQLite
- stock_level (INTEGER)
- stockout_flag (BOOLEAN) - 0 or 1 in SQLite

Rules:
- Always query from sales_transactions table only.
- Use SQLite syntax.
- Boolean columns: use promotion_flag = 1 or stockout_flag = 1 for true.
- Return ONLY the SQL query wrapped in ```sql ... ``` code block.
- No explanations outside the code block.
"""


def generate_sql(question: str, conversation_history: list[dict] | None = None) -> str:
    model = _get_model()
    history_text = ""
    if conversation_history:
        recent = conversation_history[-6:]
        history_text = "\n".join(
            f"{msg['role'].upper()}: {msg['content']}" for msg in recent
        )

    prompt = f"""{SQL_SCHEMA_CONTEXT}

Previous conversation:
{history_text or "None"}

User question: {question}

Generate a single SQLite SELECT query to answer this question. Output only:
```sql
<query here>
```
"""
    response = model.generate_content(prompt)
    return _extract_sql(response.text)


def generate_executive_summary(
    question: str,
    sql: str,
    results: list[dict],
    columns: list[str],
) -> str:
    model = _get_model()
    preview_rows = results[:10]
    prompt = f"""You are a FMCG business analyst. Provide a concise executive summary (3-5 sentences) for a business user.

Question: {question}
SQL executed: {sql}
Columns: {', '.join(columns)}
Row count: {len(results)}
Sample data (first rows): {preview_rows}

Write a clear, actionable summary highlighting key insights, trends, and numbers. Use plain business language. No SQL in the response.
"""
    response = model.generate_content(prompt)
    return response.text.strip()
