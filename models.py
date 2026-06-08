from sqlmodel import SQLModel, Field
from typing import Optional
import datetime

class PortfolioPosition(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    symbol: str
    shares: float
    avg_cost: float
    added_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
