import sqlite3
import time


class AuditLog:
    db: sqlite3.Connection

    def __init__(self, path: str = "logs.db"):
        self.db = sqlite3.connect(path)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS mail_log (
                id INTEGER PRIMARY KEY,
                ts INTEGER NOT NULL,
                content_id TEXT NOT NULL,
                email TEXT NOT NULL,
                msg_id TEXT NOT NULL
            );
            """)

    def log_mail(self, content_id: str, email: str, msg_id: str):
        self.db.execute(
            "INSERT INTO mail_log (ts, content_id, email, msg_id) VALUES (?, ?, ?, ?)",
            (time.time(), content_id, email, msg_id),
        )

    def was_mail_send(self, content_id: str, email: str) -> bool:
        cursor = self.db.execute(
            "SELECT ts FROM mail_LOG WHERE content_id=? AND email=?",
            (content_id, email),
        )
        return cursor.fetchone() is not None
