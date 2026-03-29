from app.core.db import SessionLocal
from app.models.payment import Payment


class PaymentRepository:

    def create(self, payment: Payment):
        db = SessionLocal()
        db.add(payment)
        db.commit()
        db.refresh(payment)
        db.close()
        return payment

    def get(self, payment_id: str):
        db = SessionLocal()
        payment = db.query(Payment).filter(Payment.id == payment_id).first()
        db.close()
        return payment

    def update(self, payment: Payment):
        db = SessionLocal()
        db.merge(payment)
        db.commit()
        db.close()