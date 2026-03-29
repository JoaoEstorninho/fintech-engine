from pydantic import BaseModel, Field
from typing import Literal


class PaymentRequest(BaseModel):
    amount: float = Field(gt=0, description="Amount must be > 0")
    currency: Literal["EUR", "USD", "GBP"]


class PaymentResponse(BaseModel):
    id: str
    amount: float
    currency: str
    status: str
    provider: str | None = None