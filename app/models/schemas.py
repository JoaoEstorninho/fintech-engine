from pydantic import BaseModel

class PaymentRequest(BaseModel):
    amount: float
    currency: str

class PaymentResponse(BaseModel):
    id: str
    amount: float
    currency: str
    status: str
    provider: str | None = None