from sqlalchemy import Column, Integer, String, Float, Date
from .db import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    description = Column(String, index=True)
    amount = Column(Float)
    category = Column(String, index=True)
    source = Column(String, default="manual")
