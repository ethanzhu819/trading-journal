import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "trading_journal.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                title TEXT NOT NULL,
                category TEXT,
                subcategory TEXT,
                content TEXT,
                tags TEXT,
                related_event_id INTEGER REFERENCES market_events(id) ON DELETE SET NULL,
                related_trade_id INTEGER REFERENCES trades(id) ON DELETE SET NULL,
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS learning_images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER NOT NULL REFERENCES learning_notes(id) ON DELETE CASCADE,
                image_path TEXT NOT NULL,
                caption TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS market_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT,
                event_title TEXT NOT NULL,
                source_notes TEXT,
                asset_class TEXT,
                market_reaction TEXT,
                my_interpretation TEXT,
                importance INTEGER,
                tags TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                related_event_id INTEGER REFERENCES market_events(id) ON DELETE SET NULL,
                asset TEXT NOT NULL,
                asset_class TEXT,
                direction TEXT,
                time_horizon TEXT,
                thesis TEXT,
                catalyst TEXT,
                entry REAL,
                target REAL,
                stop REAL,
                confidence INTEGER,
                risk_factors TEXT,
                status TEXT DEFAULT 'Open',
                actual_exit REAL,
                pnl REAL,
                post_trade_review TEXT
            )
        """)


# ── Market Events ─────────────────────────────────────────────────────────────

def add_event(data: dict) -> int:
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO market_events
                (date, category, event_title, source_notes, asset_class,
                 market_reaction, my_interpretation, importance, tags)
            VALUES
                (:date, :category, :event_title, :source_notes, :asset_class,
                 :market_reaction, :my_interpretation, :importance, :tags)
        """, data)
        return cur.lastrowid


def get_events(filters: dict | None = None):
    query = "SELECT * FROM market_events WHERE 1=1"
    params = []
    if filters:
        if filters.get("category"):
            query += " AND category = ?"
            params.append(filters["category"])
        if filters.get("asset_class"):
            query += " AND asset_class = ?"
            params.append(filters["asset_class"])
        if filters.get("date_from"):
            query += " AND date >= ?"
            params.append(filters["date_from"])
        if filters.get("date_to"):
            query += " AND date <= ?"
            params.append(filters["date_to"])
    query += " ORDER BY date DESC"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(query, params).fetchall()]


def update_event(event_id: int, data: dict):
    with get_conn() as conn:
        conn.execute("""
            UPDATE market_events SET
                date=:date, category=:category, event_title=:event_title,
                source_notes=:source_notes, asset_class=:asset_class,
                market_reaction=:market_reaction, my_interpretation=:my_interpretation,
                importance=:importance, tags=:tags
            WHERE id=:id
        """, {**data, "id": event_id})


def delete_event(event_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM market_events WHERE id=?", (event_id,))


# ── Trades ────────────────────────────────────────────────────────────────────

def add_trade(data: dict) -> int:
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO trades
                (date, related_event_id, asset, asset_class, direction,
                 time_horizon, thesis, catalyst, entry, target, stop,
                 confidence, risk_factors, status, actual_exit, pnl, post_trade_review)
            VALUES
                (:date, :related_event_id, :asset, :asset_class, :direction,
                 :time_horizon, :thesis, :catalyst, :entry, :target, :stop,
                 :confidence, :risk_factors, :status, :actual_exit, :pnl, :post_trade_review)
        """, data)
        return cur.lastrowid


def get_trades(filters: dict | None = None):
    query = """
        SELECT t.*, e.event_title as related_event_title
        FROM trades t
        LEFT JOIN market_events e ON t.related_event_id = e.id
        WHERE 1=1
    """
    params = []
    if filters:
        if filters.get("status"):
            query += " AND t.status = ?"
            params.append(filters["status"])
        if filters.get("asset_class"):
            query += " AND t.asset_class = ?"
            params.append(filters["asset_class"])
        if filters.get("direction"):
            query += " AND t.direction = ?"
            params.append(filters["direction"])
    query += " ORDER BY t.date DESC"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(query, params).fetchall()]


def update_trade(trade_id: int, data: dict):
    with get_conn() as conn:
        conn.execute("""
            UPDATE trades SET
                date=:date, related_event_id=:related_event_id, asset=:asset,
                asset_class=:asset_class, direction=:direction, time_horizon=:time_horizon,
                thesis=:thesis, catalyst=:catalyst, entry=:entry, target=:target,
                stop=:stop, confidence=:confidence, risk_factors=:risk_factors,
                status=:status, actual_exit=:actual_exit, pnl=:pnl,
                post_trade_review=:post_trade_review
            WHERE id=:id
        """, {**data, "id": trade_id})


def delete_trade(trade_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM trades WHERE id=?", (trade_id,))


# ── Learning Notes ────────────────────────────────────────────────────────────

def add_note(data: dict) -> int:
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO learning_notes
                (date, title, category, subcategory, content, tags,
                 related_event_id, related_trade_id)
            VALUES
                (:date, :title, :category, :subcategory, :content, :tags,
                 :related_event_id, :related_trade_id)
        """, data)
        return cur.lastrowid


def get_notes(filters: dict | None = None):
    query = "SELECT * FROM learning_notes WHERE 1=1"
    params = []
    if filters:
        if filters.get("category"):
            query += " AND category = ?"
            params.append(filters["category"])
        if filters.get("subcategory"):
            query += " AND subcategory LIKE ?"
            params.append(f"%{filters['subcategory']}%")
        if filters.get("tags"):
            query += " AND tags LIKE ?"
            params.append(f"%{filters['tags']}%")
    query += " ORDER BY date DESC, created_at DESC"
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(query, params).fetchall()]


def update_note(note_id: int, data: dict):
    with get_conn() as conn:
        conn.execute("""
            UPDATE learning_notes SET
                date=:date, title=:title, category=:category, subcategory=:subcategory,
                content=:content, tags=:tags, related_event_id=:related_event_id,
                related_trade_id=:related_trade_id,
                updated_at=datetime('now')
            WHERE id=:id
        """, {**data, "id": note_id})


def delete_note(note_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM learning_notes WHERE id=?", (note_id,))


def add_image(note_id: int, image_path: str, caption: str = "") -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO learning_images (note_id, image_path, caption) VALUES (?, ?, ?)",
            (note_id, image_path, caption),
        )
        return cur.lastrowid


def get_images_for_note(note_id: int):
    with get_conn() as conn:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM learning_images WHERE note_id=? ORDER BY created_at",
            (note_id,),
        ).fetchall()]


def delete_image(image_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM learning_images WHERE id=?", (image_id,))


def get_summary():
    with get_conn() as conn:
        total_events = conn.execute("SELECT COUNT(*) FROM market_events").fetchone()[0]
        total_trades = conn.execute("SELECT COUNT(*) FROM trades").fetchone()[0]
        open_trades = conn.execute("SELECT COUNT(*) FROM trades WHERE status='Open'").fetchone()[0]
        closed_pnl = conn.execute(
            "SELECT COALESCE(SUM(pnl), 0) FROM trades WHERE status='Closed'"
        ).fetchone()[0]
    return {
        "total_events": total_events,
        "total_trades": total_trades,
        "open_trades": open_trades,
        "closed_pnl": closed_pnl,
    }
