# import sqlite3
# import json
# import time
# import threading
# from pathlib import Path

# DB_PATH = "api_cache.db"
# CACHE_EXPIRY_SECONDS = 604800  # 7 days
# cache_lock = threading.Lock()


# class SQLiteStoreManager:
#     def __init__(self, db_path=DB_PATH):
#         self.conn = sqlite3.connect(db_path, check_same_thread=False)
#         self.conn.row_factory = sqlite3.Row
#         self._create_tables()

#     def _create_tables(self):
#         schema_path = Path(__file__).parent / "schema.sql"
#         with open(schema_path, "r", encoding="utf-8") as f:
#             schema = f.read()
#         with self.conn:
#             self.conn.executescript(schema)

#     def upsert(self, table, data: dict):
#         keys = ", ".join(data.keys())
#         placeholders = ", ".join(["?"] * len(data))
#         updates = ", ".join([f"{k}=excluded.{k}" for k in data.keys()])
#         sql = f"INSERT INTO {table} ({keys}) VALUES ({placeholders}) ON CONFLICT DO UPDATE SET {updates}"
#         with self.conn:
#             self.conn.execute(sql, tuple(data.values()))

#     def fetch(self, table, where=None, params=()):
#         sql = f"SELECT * FROM {table}"
#         if where:
#             sql += f" WHERE {where}"
#         cur = self.conn.cursor()
#         cur.execute(sql, params)
#         return [dict(r) for r in cur.fetchall()]

#     def delete(self, table, where=None, params=()):
#         sql = f"DELETE FROM {table}"
#         if where:
#             sql += f" WHERE {where}"
#         with self.conn:
#             self.conn.execute(sql, params)

#     def save(self, store_name, key, data):
#         with cache_lock, self.conn:
#             self.conn.execute("""
#                 INSERT OR REPLACE INTO storage (store_name, key, data, timestamp)
#                 VALUES (?, ?, ?, ?)
#             """, (store_name, key, json.dumps(data), time.time()))

#     def clear_all(self):
#         with cache_lock, self.conn:
#             self.conn.execute("DELETE FROM storage")
#             print("All storage cleared.")
