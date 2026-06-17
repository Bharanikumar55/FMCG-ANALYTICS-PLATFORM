from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text

from database import Base


class SalesTransaction(Base):
    __tablename__ = "sales_transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_id = Column(String, index=True)
    date = Column(String, index=True)
    product_id = Column(String, index=True)
    product_name = Column(String)
    category = Column(String, index=True)
    brand = Column(String, index=True)
    unit_price = Column(Float)
    store_id = Column(String, index=True)
    region = Column(String, index=True)
    city = Column(String, index=True)
    units_sold = Column(Integer)
    revenue = Column(Float)
    promotion_flag = Column(Boolean)
    stock_level = Column(Integer)
    stockout_flag = Column(Boolean)


class QueryHistory(Base):
    __tablename__ = "query_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, index=True)
    user_question = Column(Text, nullable=False)
    generated_sql = Column(Text)
    executive_summary = Column(Text)
    row_count = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class ConversationMessage(Base):
    __tablename__ = "conversation_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String, index=True)
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
