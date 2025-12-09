from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class TransactionBase(BaseModel):
    tx_hash: str
    monitored_address: str
    from_address: str
    to_address: Optional[str]
    value_eth: float
    timestamp: datetime
    method: Optional[str]
    gas_used: Optional[int]
    is_error: bool
    risk_score: int
    risk_label: str
    risk_reasons: Optional[str]


class TransactionRead(TransactionBase):
    id: int

    # Pydantic v2: allow constructing from SQLAlchemy objects
    model_config = ConfigDict(from_attributes=True)


class TransactionsResponse(BaseModel):
    items: List[TransactionRead]
    total: int
