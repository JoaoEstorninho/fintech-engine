from app.models.payment import Payment
from app.core.db_session import get_db


class PaymentRepository:

    def create(self, payment: Payment):
        with get_db() as db:
            db.add(payment)
            db.commit()
            db.refresh(payment)
            return payment

    def get(self, payment_id: str):
        with get_db() as db:
            return db.query(Payment).filter(Payment.id == payment_id).first()

    def update(self, payment: Payment):
        with get_db() as db:
            db.merge(payment)
            db.commit()