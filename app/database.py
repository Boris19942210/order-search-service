import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", "data/orders.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=30, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA mmap_size=268435456")  # 256 MB
    conn.execute("PRAGMA cache_size=-64000")    # 64 MB
    return conn


def init_db() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_connection()
    cur = conn.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY,
            order_number TEXT NOT NULL,
            client_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            status TEXT NOT NULL,
            amount REAL NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
        CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
        CREATE INDEX IF NOT EXISTS idx_orders_created_status
            ON orders(created_at, status);

        CREATE VIRTUAL TABLE IF NOT EXISTS orders_fts USING fts5(
            order_number,
            client_name,
            content='orders',
            content_rowid='id',
            tokenize='unicode61'
        );

        CREATE TRIGGER IF NOT EXISTS orders_ai AFTER INSERT ON orders BEGIN
            INSERT INTO orders_fts(rowid, order_number, client_name)
            VALUES (new.id, new.order_number, new.client_name);
        END;

        CREATE TRIGGER IF NOT EXISTS orders_ad AFTER DELETE ON orders BEGIN
            INSERT INTO orders_fts(orders_fts, rowid, order_number, client_name)
            VALUES ('delete', old.id, old.order_number, old.client_name);
        END;

        CREATE TRIGGER IF NOT EXISTS orders_au AFTER UPDATE ON orders BEGIN
            INSERT INTO orders_fts(orders_fts, rowid, order_number, client_name)
            VALUES ('delete', old.id, old.order_number, old.client_name);
            INSERT INTO orders_fts(rowid, order_number, client_name)
            VALUES (new.id, new.order_number, new.client_name);
        END;
    """)

    conn.commit()
    conn.close()