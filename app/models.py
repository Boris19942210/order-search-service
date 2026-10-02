from typing import List, Optional
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=200)
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    status: Optional[List[str]] = None
    limit: int = Field(50, ge=1, le=500)


class OrderItem(BaseModel):
    id: int
    order_number: str
    client_name: str
    created_at: str
    status: str
    amount: float


class SearchResponse(BaseModel):
    results: List[OrderItem]
    total: int
    took_ms: float