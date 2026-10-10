
from pathlib import Path

ROOT_FOLDER = Path(__file__).parent

DB_FOLDER = ROOT_FOLDER / "database"
COGS_FOLDER = ROOT_FOLDER / "cogs"

DB_FILE = DB_FOLDER / "database.db"
SCHEMA_FILE = DB_FOLDER / "schema.sql"