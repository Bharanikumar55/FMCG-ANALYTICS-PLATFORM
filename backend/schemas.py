from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(..., min_length=1, max_length=100)


class ChatResponse(BaseModel):
    session_id: str
    question: str
    generated_sql: Optional[str] = None
    results: list[dict[str, Any]] = []
    columns: list[str] = []
    row_count: int = 0
    executive_summary: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None
    history_id: Optional[int] = None


class HistoryItem(BaseModel):
    id: int
    session_id: str
    user_question: str
    generated_sql: Optional[str] = None
    executive_summary: Optional[str] = None
    row_count: int = 0
    success: bool = True
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class HealthResponse(BaseModel):
    status: str
    database: str
    record_count: int
    gemini_configured: bool


class ExportResponse(BaseModel):
    download_url: str
    filename: str
    row_count: int
