import sqlite3
import time
from typing import List, Optional
from .database import get_connection


def build_fts_query(query: str) -> str:
    safe_query = query.replace('"', '""')
    words = [w for w in safe_query.split() if len(w) >= 2]
    if not words:
        return '""'
    if len(words) == 1:
        return f'"{words[0]}"*'
    return " AND ".join(f'"{w}"*' for w in words)


def search_orders(query: str, date_from: Optional[str] = None,
                  date_to: Optional[str] = None,
                  statuses: Optional[List[str]] = None,
                  limit: int = 50) -> dict:
    start = time.time()
    conn = get_connection()
    cur = conn.cursor()

    fts_query = build_fts_query(query)

    sql = """
        SELECT o.id, o.order_number, o.client_name,
               o.created_at, o.status, o.amount
        FROM orders_fts fts
        JOIN orders o ON o.id = fts.rowid
        WHERE orders_fts MATCH ?
    """
    params: list = [fts_query]

    if date_from:
        sql += " AND o.created_at >= ?"
        params.append(date_from)
    if date_to:
        sql += " AND o.created_at <= ?"
        params.append(date_to)
    if statuses:
        sql += f" AND o.status IN ({','.join('?' * len(statuses))})"
        params.extend(statuses)

    sql += " ORDER BY o.created_at DESC LIMIT ?"
    params.append(limit)
    cur.execute(sql, params)
    rows = cur.fetchall()

    results = [dict(r) for r in rows]

    count_sql = """
        SELECT COUNT(*) AS total
        FROM orders_fts fts
        JOIN orders o ON o.id = fts.rowid
        WHERE orders_fts MATCH ?
    """
    cparams: list = [fts_query]
    if date_from:
        count_sql += " AND o.created_at >= ?"
        cparams.append(date_from)
    if date_to:
        count_sql += " AND o.created_at <= ?"
        cparams.append(date_to)
    if statuses:
        count_sql += f" AND o.status IN ({','.join('?' * len(statuses))})"
        cparams.extend(statuses)

    cur.execute(count_sql, cparams)
    total = cur.fetchone()["total"]
    conn.close()

    return {
        "results": results,
        "total": total,
        "took_ms": round((time.time() - start) * 1000, 2),
    }