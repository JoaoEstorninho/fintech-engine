from pydantic import BaseModel, Field
from typing import Literal, Optional
from decimal import Decimal


class PaymentRequest(BaseModel):
    amount: Decimal = Field(gt=0, description="Amount must be > 0")
    currency: Literal["EUR", "USD", "GBP"]


class PaymentResponse(BaseModel):
    id: str
    amount: Decimal
    currency: str
    status: Literal["pending", "success", "failed"]
    provider: Optional[str] = None
    retries: int