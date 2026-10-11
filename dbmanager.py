
import aiosqlite
import asyncio
import sqlite3
import logging as log
from enum import Enum

from logFormat import getMainLogger
from constants import DB_FOLDER

log = getMainLogger()

class DBStatus(Enum):
    SUCCESS = 0
    FAILURE = 1
    EXECUTED_NO_FETCH = 2

def rows_to_dict(rows, columns):
    return [dict(zip(columns, row)) for row in rows]

def deep_get_as_type(data, classtype, *indices):
    try:
        for i in indices:
            data = data[i]
        return classtype(data)
    except (IndexError, KeyError, TypeError) as e:
        return None

def deep_get(data, *indices):
    try:
        for i in indices:
            data = data[i]
        return data
    except (IndexError, KeyError, TypeError) as e:
        # frame = inspect.stack()[1]

        # # since we use deep_get here in try except for safety, it swallows the error (until i figure out the api we're just gonna disable)
        # caller_info = f"{frame.filename}:{frame.lineno} in {frame.function}()"
        # log.warning("Failed to access element at [%s]: %d levels deep.\nerror: %s\nmethod call from: %s", data, i, e, caller_info)
        return None

# behaves as a high level wrapper for aiosqlite that allows you to cleanly grab column names, w/r, and get by type at any indice
class DBManager:
    def __init__(self, config):
        self.connection = None
        self.db_filename = config.db_filename
        self._lock = asyncio.Lock()

    async def initialize(self):
        try:
            # construct the filename with the database folder path according to config
            DB_FILE = DB_FOLDER / self.db_filename
            log.info(f"Initializing database... {DB_FILE}")
            self.connection = await aiosqlite.connect(DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES)
            self.connection.row_factory = aiosqlite.Row
            await self.connection.execute("PRAGMA foreign_keys = ON")
        except Exception:
            log.exception("Failed to initialize SQLite database")
            raise

    async def close(self):
        async with self._lock:
            if self.connection is not None:
                await self.connection.close()
                self.connection = None

    async def _get_connection(self):
        if self.connection is None:
            raise RuntimeError(
                "Database is not initialized. Call await db.initialize() first."
            )

        return self.connection

    async def executescript(self, script_str):
        async with self._lock:
            conn = await self._get_connection()

            try:
                await conn.executescript(script_str)
            except Exception as e:
                # executescript automatically rollsback on error
                log.exception(f"Execute script query failed: {e}")
                raise

    async def write(self, query_str, fetch=False, get_columns=False, params=None):
        async with self._lock:
            conn = await self._get_connection()

            try:
                async with conn.execute(
                    query_str,
                    params or (),
                ) as cur:
                    results = await cur.fetchall() if fetch else None
                    column_names = (
                        [col[0] for col in cur.description]
                        if get_columns and cur.description
                        else None
                    )

                await conn.commit()

                if fetch:
                    if get_columns:
                        return results, column_names
                    return results

                return DBStatus.SUCCESS

            except Exception as e:
                await conn.rollback()
                log.exception(f"Database write query failed: {e}")
                raise

    async def read(self, query_str, fetch=True, get_columns=False, params=None):
        async with self._lock:
            conn = await self._get_connection()

            try:
                async with conn.execute(query_str, params or ()) as cur:
                    if not fetch:
                        return DBStatus.EXECUTED_NO_FETCH

                    results = await cur.fetchall()

                    if get_columns:
                        column_names = (
                            [col[0] for col in cur.description]
                            if cur.description
                            else []
                        )
                        return results, column_names

                    return results

            except Exception as e:
                log.exception(f"Database read query failed: {e}")
                raise