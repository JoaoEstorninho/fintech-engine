from sqlalchemy import Column, String, Float, Integer
from app.core.db import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String, primary_key=True, index=True)
    amount = Column(Float)
    currency = Column(String)
    status = Column(String)
    provider = Column(String, nullable=True)
    retries = Column(Integer)