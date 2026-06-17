import os
from pathlib import Path

import pandas as pd
from sqlalchemy.orm import Session

from models import SalesTransaction


def _resolve_csv_path() -> Path:
    env_path = os.getenv("CSV_PATH")
    if env_path:
        path = Path(env_path)
        if not path.is_absolute():
            path = Path(__file__).parent / path
        return path.resolve()
    return (Path(__file__).parent.parent / "data" / "fmcg_conversational_ai_dataset.csv").resolve()


def load_csv_to_db(db: Session) -> int:
    csv_path = _resolve_csv_path()
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found at {csv_path}")

    existing = db.query(SalesTransaction).count()
    if existing > 0:
        return existing

    df = pd.read_csv(csv_path)

    if "unit_price" not in df.columns:
        df["unit_price"] = (df["revenue"] / df["units_sold"].replace(0, 1)).round(2)

    df["promotion_flag"] = df["promotion_flag"].map(
        lambda x: str(x).lower() in ("true", "1", "yes")
    )
    df["stockout_flag"] = df["stockout_flag"].map(
        lambda x: str(x).lower() in ("true", "1", "yes")
    )

    column_order = [
        "transaction_id", "date", "product_id", "product_name", "category", "brand",
        "unit_price", "store_id", "region", "city", "units_sold", "revenue",
        "promotion_flag", "stock_level", "stockout_flag",
    ]
    for col in column_order:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    records = []
    for _, row in df.iterrows():
        records.append(
            SalesTransaction(
                transaction_id=str(row["transaction_id"]),
                date=str(row["date"]),
                product_id=str(row["product_id"]),
                product_name=str(row["product_name"]),
                category=str(row["category"]),
                brand=str(row["brand"]),
                unit_price=float(row["unit_price"]),
                store_id=str(row["store_id"]),
                region=str(row["region"]),
                city=str(row["city"]),
                units_sold=int(row["units_sold"]),
                revenue=float(row["revenue"]),
                promotion_flag=bool(row["promotion_flag"]),
                stock_level=int(row["stock_level"]),
                stockout_flag=bool(row["stockout_flag"]),
            )
        )

    db.bulk_save_objects(records)
    db.commit()
    return len(records)
