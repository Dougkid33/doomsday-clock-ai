import sqlite3
from datetime import datetime
from typing import Iterable, List, Optional, Tuple

from  domain.models import NewsItem, ThreatScore

SCHEMA = """
CREATE TABLE IF NOT EXISTS news (
  url TEXT PRIMARY KEY,
  source TEXT NOT NULL,
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  category TEXT NOT NULL DEFAULT 'Geral',
  published_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scores (
  url TEXT PRIMARY KEY,
  sentiment REAL NOT NULL,
  keywords REAL NOT NULL,
  source_weight REAL NOT NULL,
  recency REAL NOT NULL,
  final REAL NOT NULL,
  label TEXT NOT NULL,
  calculated_at TEXT NOT NULL,
  FOREIGN KEY(url) REFERENCES news(url)
);
"""

class SQLiteRepo:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _init(self):
        with self._conn() as con:
            con.executescript(SCHEMA)

    def upsert_news(self, items: Iterable[NewsItem]) -> int:
        rows = 0
        with self._conn() as con:
            for it in items:
                if not it.url:
                    continue
                con.execute(
                    """INSERT OR REPLACE INTO news(url, source, title, summary, category, published_at)
                       VALUES(?,?,?,?,?,?)""",
                    (it.url, it.source, it.title, it.summary, it.category, it.published_at.isoformat())
                )
                rows += 1
        return rows

    def upsert_scores(self, scores: Iterable[ThreatScore]) -> int:
        rows = 0
        now = datetime.utcnow().isoformat()
        with self._conn() as con:
            for sc in scores:
                con.execute(
                    """INSERT OR REPLACE INTO scores(url, sentiment, keywords, source_weight, recency, final, label, calculated_at)
                       VALUES(?,?,?,?,?,?,?,?)""",
                    (sc.item_url, sc.sentiment, sc.keywords, sc.source_weight, sc.recency, sc.final, sc.label, now)
                )
                rows += 1
        return rows

    def fetch_latest(self, limit: int = 40) -> List[Tuple]:
        with self._conn() as con:
            cur = con.execute(
                """SELECT n.source, n.category,n.title, n.url, n.published_at,
                          s.final, s.label, n.summary
                   FROM news n
                   LEFT JOIN scores s ON s.url = n.url
                   ORDER BY n.published_at DESC
                   LIMIT ?""",
                (limit,)
            )
            return cur.fetchall()

    def fetch_global_risk(self) -> float:
        # risco global = média ponderada dos top N scores (mais recentes)
        with self._conn() as con:
            cur = con.execute(
                """SELECT final FROM scores
                   ORDER BY calculated_at DESC
                   LIMIT 60"""
            )
            vals = [r[0] for r in cur.fetchall() if r[0] is not None]
        if not vals:
            return 0.35
        return sum(vals) / len(vals)
    
    def fetch_risk_history(self, limit: int = 500):

        with self._conn() as con:
            cur = con.execute("""
                SELECT substr(calculated_at, 1, 16) as ts_minute,
                       AVG(final) as risk_avg
                FROM scores
                GROUP BY ts_minute
                ORDER BY ts_minute ASC
                LIMIT ?
            """, (limit,))
            return cur.fetchall()    
    
