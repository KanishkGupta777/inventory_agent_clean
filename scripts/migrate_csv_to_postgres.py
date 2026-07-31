"""
One-time script to load all CSV/TSV files from /data into Postgres.
Run with: uv run scripts/migrate_csv_to_postgres.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sqlalchemy import text
from src.db.connection import engine

DEFAULT_STORE_ID = "STORE_001"
DEFAULT_STORE_NAME = "Chipotle Downtown Mumbai"

# table_name -> (filename, separator)
FILES = {
    "campaigns": ("campaigns.csv", ","),
    "customer_feedback": ("customer_feedback.csv", ","),
    "customer_orders": ("customer_orders.csv", ","),
    "customers": ("customers.csv", ","),
    "festivals": ("festivals.csv", ","),
    "finance_summary": ("finance_summary.csv", ","),
    "inventory": ("inventory.csv", ","),
    "kitchen_orders": ("kitchen_orders.csv", ","),
    "local_news": ("local_news.csv", ","),
    "menu_prep_times": ("menu_prep_times.csv", ","),
    "menu_pricing": ("menu_pricing.csv", ","),
    "offers": ("offers.csv", ","),
    "orders": ("orders.tsv", "\t"),
    "packaging_inventory": ("packaging_inventory.csv", ","),
    "packaging_usage": ("packaging_usage.csv", ","),
    "recipes": ("recipes.csv", ","),
    "staff_performance": ("staff_performance.csv", ","),
    "staff_schedule": ("staff_schedule.csv", ","),
    "suppliers": ("suppliers.csv", ","),
    "waste_log": ("waste_log.csv", ","),
    "weather_log": ("weather_log.csv", ","),
}


def create_stores_and_reports_tables():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS stores (
                store_id TEXT PRIMARY KEY,
                store_name TEXT NOT NULL,
                city TEXT,
                state TEXT,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        conn.execute(text("""
            INSERT INTO stores (store_id, store_name, city, state)
            VALUES (:store_id, :store_name, 'Jaipur', 'Rajasthan')
            ON CONFLICT (store_id) DO NOTHING
        """), {"store_id": DEFAULT_STORE_ID, "store_name": DEFAULT_STORE_NAME})

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS agent_reports (
                id SERIAL PRIMARY KEY,
                store_id TEXT NOT NULL REFERENCES stores(store_id),
                agent_level TEXT NOT NULL,
                agent_name TEXT NOT NULL,
                report_json JSONB NOT NULL,
                requires_approval BOOLEAN DEFAULT FALSE,
                approved BOOLEAN,
                approved_by TEXT,
                approved_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
    print("stores + agent_reports tables ready")


def migrate():
    create_stores_and_reports_tables()

    for table_name, (filename, sep) in FILES.items():
        path = os.path.join("data", filename)
        if not os.path.exists(path):
            print(f"SKIP (not found): {path}")
            continue

        df = pd.read_csv(path, sep=sep)
        df["store_id"] = DEFAULT_STORE_ID

        df.to_sql(table_name, engine, if_exists="replace", index=False)
        print(f"Loaded {len(df)} rows into '{table_name}'")

    print("\nMigration complete.")


if __name__ == "__main__":
    migrate()