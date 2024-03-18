import sqlite3
import time


class AuditLog:
    db: sqlite3.Connection

    def __init__(self, path: str = "logs.db"):
        self.db = sqlite3.connect(path)
        with self.db:
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS mail_log (
                    id INTEGER PRIMARY KEY,
                    ts INTEGER NOT NULL,
                    shift_id INTEGER NOT NULL,
                    content_id TEXT NOT NULL,
                    email TEXT NOT NULL,
                    msg_id TEXT NOT NULL
                );
                """)

    def close(self):
        self.db.close()

    def log_mail(self, shift_id: int, content_id: str, email: str, msg_id: str):
        with self.db:
            self.db.execute(
                "INSERT INTO mail_log (ts, shift_id, content_id, email, msg_id) VALUES (?, ?, ?, ?, ?)",
                (time.time(), shift_id, content_id, email, msg_id),
            )

    def was_mail_send(self, shift_id: int, content_id: str, email: str) -> bool:
        cursor = self.db.execute(
            "SELECT ts FROM mail_LOG WHERE shift_id=? AND content_id=? AND email=?",
            (shift_id, content_id, email),
        )
        return cursor.fetchone() is not None
