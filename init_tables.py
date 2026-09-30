import sqlite3
import psycopg2
from config import DATABASE_URL


CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS companies (
    ticker TEXT PRIMARY KEY
    name TEXT,
    investment_track TEXT,
);
"""

