import sqlite3
from datetime import datetime
from typing import Dict, List

class ApplicationDatabase:
    def __init__(self, db_path="applications.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    summary TEXT,
                    applied_date DATE NOT NULL,
                    updated_date DATE NOT NULL
                )
            ''')
            conn.commit()

    def add_application(self, company, status, applied_date, summary=None):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO applications (company_name, status, summary, applied_date, updated_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (company, status, summary, applied_date.date(), applied_date.date()))
            conn.commit()

    def update_application(self, company, status, update_date, summary=None):
        if update_date is None:
            update_date = datetime.now()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT applied_date FROM applications WHERE company_name = ?
            ''', (company,))

            existing_application = cursor.fetchone()

            if existing_application:
                cursor.execute('''
                    UPDATE applications
                    SET status = ?, updated_date = ?, summary = ?
                    WHERE company_name = ?
                ''', (status, update_date.date(), summary, company))
            else:
                cursor.execute('''
                    INSERT INTO applications (company_name, status, summary, applied_date, updated_date)
                    VALUES (?, ?, ?, ?, ?)
                ''', (company, status, summary, update_date.date(), update_date.date()))

            conn.commit()

    def get_stats(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get total applications
            cursor.execute('SELECT COUNT(*) FROM applications')
            total = cursor.fetchone()[0]

            # Get recent updates
            cursor.execute('''
                SELECT company_name, status, summary, updated_date
                FROM applications
                ORDER BY updated_date DESC
                LIMIT 5
            ''')
            recent_updates = [
                {
                    "company": row[0],
                    "status": row[1],
                    "summary": row[2],
                    "updated": row[3]
                }
                for row in cursor.fetchall()
            ]

            return {
                "total_applications": total,
                "recent_updates": recent_updates
            }

    def get_all_applications(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT company_name, status, summary, applied_date, updated_date
                FROM applications
                ORDER BY updated_date DESC
            ''')
            return [
                {
                    "company": row[0],
                    "status": row[1],
                    "summary": row[2],
                    "applied_date": row[3],
                    "updated_date": row[4]
                }
                for row in cursor.fetchall()
            ]
