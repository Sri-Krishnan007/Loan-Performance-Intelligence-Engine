from pydantic import BaseModel
from typing import List, Any

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    limit: int
    offset: int
