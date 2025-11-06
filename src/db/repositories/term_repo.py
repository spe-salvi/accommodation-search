import sqlite3
import logging

logger = logging.getLogger(__name__)

class TermRepository:
    def __init__(self, db_path='data.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS term_store (
                term_id TEXT PRIMARY KEY,
                name TEXT
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS term_courses (
                term_id TEXT,
                course_id TEXT,
                PRIMARY KEY (term_id, course_id)
            )
        """)
        self.conn.commit()

    def upsert(self, term_id: str, name: str):
        try:
            self.conn.execute("""
                INSERT INTO term_store (term_id, name)
                VALUES (?, ?)
                ON CONFLICT(term_id) DO UPDATE SET name = excluded.name
            """, (term_id, name))
            self.conn.commit()
            logger.info(f"Upserted term: {term_id} - {name}")
        except Exception as e:
            logger.error(f"Error upserting term {term_id}: {e}")

    def link_course(self, term_id: str, course_id: str):
        """Link a course to a term."""
        try:
            self.conn.execute("""
                INSERT OR IGNORE INTO term_courses (term_id, course_id)
                VALUES (?, ?)
            """, (term_id, course_id))
            self.conn.commit()
        except Exception as e:
            logger.error(f"Error linking course {course_id} to term {term_id}: {e}")

    def get_term(self, term_id: str):
        cur = self.conn.execute("SELECT * FROM term_store WHERE term_id = ?", (term_id,))
        return cur.fetchone()

    def get_courses_for_term(self, term_id: str):
        cur = self.conn.execute("SELECT course_id FROM term_courses WHERE term_id = ?", (term_id,))
        return [row['course_id'] for row in cur.fetchall()]

    def list_terms(self):
        cur = self.conn.execute("SELECT term_id, name FROM term_store ORDER BY name")
        return [dict(row) for row in cur.fetchall()]
