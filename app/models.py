from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    Text,
)
from .db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    tx_hash = Column(String(80), unique=True, index=True, nullable=False)

    monitored_address = Column(String(64), index=True, nullable=False)
    from_address = Column(String(64), index=True, nullable=False)
    to_address = Column(String(64), index=True)

    value_eth = Column(Float, nullable=False, default=0.0)
    timestamp = Column(DateTime, index=True, nullable=False, default=datetime.utcnow)
    method = Column(String(120))
    gas_used = Column(Integer)
    is_error = Column(Boolean, default=False)

    risk_score = Column(Integer, default=0)
    risk_label = Column(String(16), index=True, default="LOW")  # LOW / MEDIUM / HIGH
    risk_reasons = Column(Text)
