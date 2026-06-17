import re

FORBIDDEN_KEYWORDS = [
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "CREATE",
    "REPLACE",
    "ATTACH",
    "DETACH",
    "PRAGMA",
    "VACUUM",
    "REINDEX",
]

FORBIDDEN_PATTERN = re.compile(
    r"\b(" + "|".join(FORBIDDEN_KEYWORDS) + r")\b",
    re.IGNORECASE,
)


def validate_sql(sql: str) -> tuple[bool, str]:
    if not sql or not sql.strip():
        return False, "SQL query is empty."

    cleaned = sql.strip().rstrip(";")

    if FORBIDDEN_PATTERN.search(cleaned):
        return False, "Only SELECT queries are allowed. Destructive or modifying statements are blocked."

    # Must start with SELECT or WITH (for CTEs)
    upper = cleaned.upper().lstrip()
    if not (upper.startswith("SELECT") or upper.startswith("WITH")):
        return False, "Only SELECT queries (including CTEs with WITH) are permitted."

    if ";" in cleaned:
        return False, "Multiple SQL statements are not allowed."

    return True, ""
