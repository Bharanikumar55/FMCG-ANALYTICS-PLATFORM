import csv
import io
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from csv_loader import load_csv_to_db
from database import Base, engine, get_db
from llm import generate_executive_summary, is_gemini_configured
from models import ConversationMessage, QueryHistory, SalesTransaction
from schemas import ChatRequest, ChatResponse, HealthResponse, HistoryItem
from sql_generator import execute_validated_sql, process_natural_language_query
from validator import validate_sql

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        count = load_csv_to_db(db)
        print(f"Database ready with {count} sales records.")
    finally:
        db.close()
    yield


app = FastAPI(
    title="FMCG Conversational Analytics API",
    description="Natural language analytics for FMCG sales data",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _get_conversation_history(db: Session, session_id: str, limit: int = 10) -> list[dict]:
    messages = (
        db.query(ConversationMessage)
        .filter(ConversationMessage.session_id == session_id)
        .order_by(ConversationMessage.created_at.desc())
        .limit(limit)
        .all()
    )
    messages.reverse()
    return [{"role": m.role, "content": m.content} for m in messages]


def _save_conversation(db: Session, session_id: str, role: str, content: str):
    db.add(ConversationMessage(session_id=session_id, role=role, content=content))
    db.commit()


@app.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    try:
        count = db.query(SalesTransaction).count()
        db_status = "connected"
    except Exception:
        count = 0
        db_status = "error"
    return HealthResponse(
        status="ok" if db_status == "connected" else "degraded",
        database=db_status,
        record_count=count,
        gemini_configured=is_gemini_configured(),
    )


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    if not is_gemini_configured():
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY is not configured. Set it in backend/.env",
        )

    session_id = request.session_id or str(uuid.uuid4())
    question = request.question.strip()

    _save_conversation(db, session_id, "user", question)
    history = _get_conversation_history(db, session_id)

    try:
        sql, results, columns, exec_error = process_natural_language_query(
            db, question, history
        )

        if exec_error:
            history_entry = QueryHistory(
                session_id=session_id,
                user_question=question,
                generated_sql=sql,
                success=False,
                error_message=exec_error,
                row_count=0,
            )
            db.add(history_entry)
            db.commit()
            db.refresh(history_entry)

            _save_conversation(db, session_id, "assistant", f"Error: {exec_error}")

            return ChatResponse(
                session_id=session_id,
                question=question,
                generated_sql=sql,
                results=[],
                columns=[],
                row_count=0,
                success=False,
                error_message=exec_error,
                history_id=history_entry.id,
            )

        summary = ""
        try:
            summary = generate_executive_summary(question, sql, results, columns)
        except Exception as summary_err:
            summary = f"Query returned {len(results)} rows. (Summary unavailable: {summary_err})"

        history_entry = QueryHistory(
            session_id=session_id,
            user_question=question,
            generated_sql=sql,
            executive_summary=summary,
            row_count=len(results),
            success=True,
        )
        db.add(history_entry)
        db.commit()
        db.refresh(history_entry)

        _save_conversation(db, session_id, "assistant", summary)

        return ChatResponse(
            session_id=session_id,
            question=question,
            generated_sql=sql,
            results=results,
            columns=columns,
            row_count=len(results),
            executive_summary=summary,
            success=True,
            history_id=history_entry.id,
        )

    except Exception as exc:
        history_entry = QueryHistory(
            session_id=session_id,
            user_question=question,
            success=False,
            error_message=str(exc),
            row_count=0,
        )
        db.add(history_entry)
        db.commit()
        db.refresh(history_entry)

        return ChatResponse(
            session_id=session_id,
            question=question,
            success=False,
            error_message=str(exc),
            history_id=history_entry.id,
        )


@app.get("/history", response_model=list[HistoryItem])
def get_history(
    session_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(QueryHistory).order_by(QueryHistory.created_at.desc())
    if session_id:
        query = query.filter(QueryHistory.session_id == session_id)
    return query.limit(limit).all()


@app.get("/export")
def export_results(
    sql: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    is_valid, error = validate_sql(sql)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    results, columns, exec_error = execute_validated_sql(db, sql)
    if exec_error:
        raise HTTPException(status_code=400, detail=exec_error)

    output = io.StringIO()
    if results:
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        writer.writerows(results)
    else:
        output.write("No data\n")

    filename = f"fmcg_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/")
def root():
    return {
        "service": "FMCG Conversational Analytics API",
        "docs": "/docs",
        "health": "/health",
    }
