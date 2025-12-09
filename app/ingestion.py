import time
from datetime import datetime
from typing import List, Dict, Any

import httpx
from sqlalchemy.orm import Session

from .config import get_settings
from .db import SessionLocal, engine, Base
from . import crud
from .risk import score_transaction, BURST_TX_THRESHOLD_COUNT

settings = get_settings()

ETHERSCAN_API_URL = "https://api.etherscan.io/v2/api"


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


def fetch_transactions_from_etherscan(address: str, limit: int = 50) -> List[Dict[str, Any]]:
    if not settings.etherscan_api_key:
        print("No ETHERSCAN_API_KEY set, skipping fetch.")
        return []

    params = {
        "apikey": settings.etherscan_api_key,
        "chainid": 1,             # 1 = Ethereum mainnet
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 9999999999,
        "page": 1,
        "offset": limit,
        "sort": "desc",
    }

    try:
        resp = httpx.get(ETHERSCAN_API_URL, params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") != "1":
            print(f"Etherscan returned status {data.get('status')}: {data.get('message')}")
            return []
        return data.get("result", [])
    except Exception as e:
        print(f"Error fetching transactions for {address}: {e}")
        return []


def normalize_tx(raw: Dict[str, Any], monitored_address: str) -> Dict[str, Any]:
    # Raw format from Etherscan
    tx_hash = raw.get("hash")
    from_address = raw.get("from")
    to_address = raw.get("to")
    value_wei = int(raw.get("value", "0") or "0")
    value_eth = value_wei / 1e18
    timestamp = datetime.utcfromtimestamp(int(raw.get("timeStamp", "0") or "0"))
    is_error = str(raw.get("isError", "0")) == "1"
    gas_used = int(raw.get("gasUsed", "0") or "0")

    # method / functionName is often provided; we'll keep a short version
    method = raw.get("functionName") or raw.get("methodId") or ""
    method = method[:120]

    return {
        "tx_hash": tx_hash,
        "monitored_address": monitored_address,
        "from_address": from_address,
        "to_address": to_address,
        "value_eth": value_eth,
        "timestamp": timestamp,
        "method": method,
        "gas_used": gas_used,
        "is_error": is_error,
    }


def sync_address(db: Session, address: str) -> None:
    raw_txs = fetch_transactions_from_etherscan(address)
    if not raw_txs:
        return

    for raw in raw_txs:
        tx_hash = raw.get("hash")
        if not tx_hash:
            continue

        if crud.get_transaction_by_hash(db, tx_hash):
            # already stored
            continue

        tx = normalize_tx(raw, monitored_address=address)

        outgoing_count = crud.count_recent_outgoing(
            db,
            monitored_address=address,
            from_address=tx["from_address"],
            window_minutes=10,
            until=tx["timestamp"],
        )

        risk_score, risk_label, risk_reasons = score_transaction(
            value_eth=tx["value_eth"],
            from_address=tx["from_address"],
            to_address=tx["to_address"],
            outgoing_tx_count_window=outgoing_count,
        )

        crud.create_transaction(
            db,
            tx_hash=tx["tx_hash"],
            monitored_address=tx["monitored_address"],
            from_address=tx["from_address"],
            to_address=tx["to_address"],
            value_eth=tx["value_eth"],
            timestamp=tx["timestamp"],
            method=tx["method"],
            gas_used=tx["gas_used"],
            is_error=tx["is_error"],
            risk_score=risk_score,
            risk_label=risk_label,
            risk_reasons=risk_reasons,
        )
        print(f"[ingestor] Stored tx {tx['tx_hash']} for {address} with risk {risk_label}")


def main_loop() -> None:
    init_db()

    if not settings.monitored_addresses:
        print("No MONITORED_ADDRESSES configured. Set env MONITORED_ADDRESSES.")
        return

    print(f"Starting ingestion loop for: {settings.monitored_addresses}")
    while True:
        with SessionLocal() as db:
            for addr in settings.monitored_addresses:
                sync_address(db, addr)
        time.sleep(settings.poll_interval_seconds)


if __name__ == "__main__":
    main_loop()
