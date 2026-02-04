import os
import sqlite3
import logging
from typing import Set

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Schema definition (canonical source of truth)
# ---------------------------------------------------------------------------
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    content TEXT NOT NULL,
    mood INTEGER NOT NULL,
    mood_factors TEXT,
    sentiment REAL,
    entry_type TEXT NOT NULL,
    ai_insight TEXT,
    weather_data TEXT
);
"""

# Expected column names – must match the CREATE_TABLE_SQL definition exactly
EXPECTED_COLUMNS: Set[str] = {
    "id",
    "date",
    "content",
    "mood",
    "mood_factors",
    "sentiment",
    "entry_type",
    "ai_insight",
    "weather_data",
}


def get_current_columns(db_path: str) -> Set[str]:
    """Return a set of column names for the 'entries' table.

    If the table does not exist the returned set will be empty.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("PRAGMA table_info(entries)")
        cols = {row[1] for row in cur.fetchall()}
    finally:
        conn.close()
    return cols


def create_database(db_path: str) -> None:
    """Create a fresh reflections.db file with the full schema.

    The function uses ``executescript`` so that the CREATE statement is run as‑is.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.executescript(CREATE_TABLE_SQL)
        conn.commit()
        logger.info("Database file created with full schema.")
    finally:
        conn.close()


def ensure_database() -> str:
    """Ensure a usable reflections.db exists.

    Returns a human‑readable status message that the CLI can print.
    """
    # Allow an environment variable to override the location – useful for testing
    db_path = os.getenv("REFLECTIONS_DB_PATH") or os.path.join(os.getcwd(), "reflections.db")

    if not os.path.exists(db_path):
        logger.info("Database file not found – creating new DB at %s", db_path)
        create_database(db_path)
        return "Database created."

    # DB file exists – inspect schema
    current_columns = get_current_columns(db_path)
    if not current_columns:
        # The file exists but the 'entries' table is missing – treat as a fresh init
        logger.warning("Database file exists but 'entries' table missing – recreating tables.")
        create_database(db_path)
        return "Database created (missing table detected)."

    if current_columns == EXPECTED_COLUMNS:
        logger.info("Database already contains the expected schema.")
        return "Database already up‑to‑date."

    # Some columns are missing – run migrations
    missing = EXPECTED_COLUMNS - current_columns
    logger.info("Database missing columns %s – invoking migration.", missing)
    # Import migrate_db lazily to avoid circular import / unnecessary load
    import importlib
    migrate_mod = importlib.import_module("migrate_db")
    # The migration script expects to locate the DB itself, so just call it
    migrate_mod.migrate_database()
    return f"Migration applied – added columns: {', '.join(sorted(missing))}."


if __name__ == "__main__":
    try:
        message = ensure_database()
        print(message)
    except Exception as exc:  # pragma: no cover – unexpected errors are re‑raised after logging
        logger.error("Failed to initialise database: %s", exc)
        raise
