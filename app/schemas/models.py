from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class ResearchRequest(BaseModel):
    competitors: List[str] = Field(..., min_items=1, max_items=10)
    start_date: datetime
    end_date: datetime


class ResearchReport(BaseModel):
    period: str
    summary: str
    generated_at: datetime
