from fastapi import FastAPI, HTTPException
from .database import init_db, get_connection
from .models import SearchRequest, SearchResponse
from .search import search_orders

app = FastAPI(title="Order Search Service", version="2.1")


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    try:
        return search_orders(
            query=req.query,
            date_from=req.date_from,
            date_to=req.date_to,
            statuses=req.status,
            limit=req.limit,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/stats")
def stats():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM orders")
    total = cur.fetchone()["c"]
    conn.close()
    return {"orders_count": total}