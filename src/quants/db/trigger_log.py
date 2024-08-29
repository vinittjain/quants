import sqlite3
from datetime import datetime

from ..utils import get_logger

logger = get_logger(__name__)


class TriggerLog:
    def __init__(self, db_path: str = "trigger_log.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()
        logger.info(f"Trigger log database initialized at {db_path}")

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS triggers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                symbol TEXT,
                interval TEXT,
                strategy TEXT,
                signal TEXT,
                chart_path TEXT
            )
        """
        )
        self.conn.commit()
        logger.info("Trigger log table created or already exists")

    def log_trigger(
        self,
        timestamp: datetime,
        symbol: str,
        interval: str,
        strategy: str,
        signal: str,
        chart_path: str,
    ):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT INTO triggers (timestamp, symbol, interval, strategy, signal, chart_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (timestamp, symbol, interval, strategy, signal, chart_path),
        )
        self.conn.commit()
        logger.info(f"Trigger logged: {symbol} {interval} {strategy} {signal}")

    def get_triggers(self, limit: int = 100):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM triggers ORDER BY timestamp DESC LIMIT ?", (limit,))
        return cursor.fetchall()

    def close(self):
        self.conn.close()
