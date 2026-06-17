from sqlalchemy import text
from sqlalchemy.orm import Session

from llm import generate_sql
from validator import validate_sql


def execute_validated_sql(db: Session, sql: str) -> tuple[list[dict], list[str], str | None]:
    is_valid, error = validate_sql(sql)
    if not is_valid:
        return [], [], error

    try:
        result = db.execute(text(sql))
        rows = result.fetchall()
        columns = list(result.keys()) if result.keys() else []
        data = [dict(zip(columns, row)) for row in rows]
        for row in data:
            for key, value in row.items():
                if hasattr(value, "isoformat"):
                    row[key] = value.isoformat()
                elif isinstance(value, bool):
                    row[key] = value
                elif value is None:
                    row[key] = None
                else:
                    try:
                        if isinstance(value, float) and value == int(value):
                            row[key] = int(value) if abs(value - int(value)) < 1e-9 else value
                    except (ValueError, OverflowError):
                        pass
        return data, columns, None
    except Exception as exc:
        return [], [], f"SQL execution error: {exc}"


def process_natural_language_query(
    db: Session,
    question: str,
    conversation_history: list[dict] | None = None,
) -> tuple[str, list[dict], list[str], str | None]:
    sql = generate_sql(question, conversation_history)
    data, columns, error = execute_validated_sql(db, sql)
    return sql, data, columns, error
