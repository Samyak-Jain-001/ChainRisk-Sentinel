from typing import Optional

from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .db import SessionLocal, engine, Base
from . import crud
from .schemas import TransactionRead, TransactionsResponse  # <-- make sure TransactionRead is imported

app = FastAPI(title="Onchain Wallet Risk Monitor")

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
def root():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/transactions", response_model=TransactionsResponse, tags=["transactions"])
def list_transactions(
    monitored_address: Optional[str] = None,
    risk_label: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    items, total = crud.get_transactions(
        db,
        monitored_address=monitored_address,
        risk_label=risk_label,
        limit=limit,
        offset=offset,
    )

    # Convert SQLAlchemy objects -> Pydantic models
    pydantic_items = [TransactionRead.model_validate(tx) for tx in items]

    return TransactionsResponse(items=pydantic_items, total=total)


@app.get("/alerts", response_model=TransactionsResponse, tags=["transactions"])
def list_alerts(
    monitored_address: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    items, total = crud.get_alerts(
        db,
        monitored_address=monitored_address,
        limit=limit,
        offset=offset,
    )

    pydantic_items = [TransactionRead.model_validate(tx) for tx in items]

    return TransactionsResponse(items=pydantic_items, total=total)
