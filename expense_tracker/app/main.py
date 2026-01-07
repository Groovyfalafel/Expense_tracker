from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from .db import Base, engine, SessionLocal
from .models import Transaction
from .schemas import TransactionCreate, TransactionOut
from .categorizer import categorize
from .insights import generate_insights

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Smart Expense Tracker + Insights")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/transactions", response_model=TransactionOut)
def add_transaction(tx: TransactionCreate, db: Session = Depends(get_db)):
    cat = categorize(tx.description)
    row = Transaction(
        date=tx.date,
        description=tx.description,
        amount=tx.amount,
        category=cat,
        source="manual",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.get("/transactions", response_model=list[TransactionOut])
def list_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).order_by(Transaction.date.desc()).all()


@app.delete("/transactions/{tx_id}")
def delete_transaction(tx_id: int, db: Session = Depends(get_db)):
    row = db.query(Transaction).filter(Transaction.id == tx_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(row)
    db.commit()
    return {"deleted_id": tx_id}


@app.get("/insights")
def insights(month: str | None = None, db: Session = Depends(get_db)):
    rows = db.query(Transaction).all()
    data = [
        {
            "id": r.id,
            "date": r.date.isoformat(),
            "description": r.description,
            "amount": r.amount,
            "category": r.category,
            "source": r.source,
        }
        for r in rows
    ]
    return generate_insights(data, focus_month=month)
