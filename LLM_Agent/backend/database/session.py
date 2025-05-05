import psycopg2
from psycopg2.extras import RealDictCursor
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import Config

class Database:
    def __init__(self):
        self.dsn = Config.DB_CONFIG

    def __enter__(self):
        self.conn = psycopg2.connect(**self.dsn)
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
        return self

    def execute(self, query, params=None, commit=False):
        try:
            self.cur.execute(query, params)
            if commit:
                self.conn.commit()
            return self.cur
        except Exception as e:
            self.conn.rollback()
            raise e

    def __exit__(self, exc_type, exc_value, traceback):
        self.cur.close()
        self.conn.close()
