from pydantic import BaseModel
from datetime import date

class TransactionCreate(BaseModel):
    date: date
    description: str
    amount: float

class TransactionOut(BaseModel):
    id: int
    date: date
    description: str
    amount: float
    category: str
    source: str

    class Config:
        from_attributes = True
