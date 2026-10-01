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

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS prices(
    ticker TEXT PRIMARY KEY
    date
    open
    high
    low
    close
    adjusted close
    volume 

);
"""