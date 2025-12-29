#!/usr/bin/env python
"""
Export all tables from the configured database to JSON files in `backend/db_exports/`.
Usage:
  python scripts/export_db.py
"""
import os
import sys
import json
from pathlib import Path
# ensure backend directory is importable when script run from workspace root
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app, db
from sqlalchemy import text

OUT_DIR = Path(__file__).resolve().parents[1] / "db_exports"
OUT_DIR.mkdir(parents=True, exist_ok=True)

app = create_app()

with app.app_context():
    conn = db.engine.connect()
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()

    print(f"Found {len(tables)} tables: {tables}")

    for table in tables:
        print(f"Exporting table: {table} ...")
        try:
            result = conn.execute(text(f"SELECT * FROM `{table}`"))
            rows = [dict(row._mapping) for row in result]
            out_file = OUT_DIR / f"{table}.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(rows, f, default=str, indent=2)
            print(f"  -> Wrote {len(rows)} rows to {out_file}")
        except Exception as e:
            print(f"  ✗ Error exporting {table}: {e}")

    conn.close()

print("Export complete.")
