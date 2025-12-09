from datetime import datetime, timedelta
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from .models import Transaction
from .risk import BURST_TX_THRESHOLD_COUNT  # just for window size config, optional


def get_transaction_by_hash(db: Session, tx_hash: str) -> Optional[Transaction]:
    return db.query(Transaction).filter(Transaction.tx_hash == tx_hash).first()


def create_transaction(
    db: Session,
    *,
    tx_hash: str,
    monitored_address: str,
    from_address: str,
    to_address: Optional[str],
    value_eth: float,
    timestamp: datetime,
    method: Optional[str],
    gas_used: Optional[int],
    is_error: bool,
    risk_score: int,
    risk_label: str,
    risk_reasons: str,
) -> Transaction:
    tx = Transaction(
        tx_hash=tx_hash,
        monitored_address=monitored_address,
        from_address=from_address,
        to_address=to_address,
        value_eth=value_eth,
        timestamp=timestamp,
        method=method,
        gas_used=gas_used,
        is_error=is_error,
        risk_score=risk_score,
        risk_label=risk_label,
        risk_reasons=risk_reasons,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def count_recent_outgoing(
    db: Session,
    *,
    monitored_address: str,
    from_address: str,
    window_minutes: int,
    until: datetime,
) -> int:
    window_start = until - timedelta(minutes=window_minutes)
    return (
        db.query(func.count(Transaction.id))
        .filter(Transaction.monitored_address == monitored_address)
        .filter(Transaction.from_address == from_address)
        .filter(Transaction.timestamp >= window_start)
        .filter(Transaction.timestamp <= until)
        .scalar()
        or 0
    )


def get_transactions(
    db: Session,
    *,
    monitored_address: Optional[str] = None,
    risk_label: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> Tuple[List[Transaction], int]:
    q = db.query(Transaction)

    if monitored_address:
        q = q.filter(Transaction.monitored_address == monitored_address)

    if risk_label:
        q = q.filter(Transaction.risk_label == risk_label)

    total = q.count()
    items = (
        q.order_by(Transaction.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return items, total


def get_alerts(
    db: Session,
    *,
    monitored_address: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> Tuple[List[Transaction], int]:
    q = db.query(Transaction)

    if monitored_address:
        q = q.filter(Transaction.monitored_address == monitored_address)

    q = q.filter(
        or_(Transaction.risk_label == "MEDIUM", Transaction.risk_label == "HIGH")
    )

    total = q.count()
    items = (
        q.order_by(Transaction.timestamp.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return items, total
