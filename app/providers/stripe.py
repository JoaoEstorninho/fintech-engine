import random

def process_payment(amount: float):
    if random.random() > 0.3:
        return {"status": "success", "provider": "stripe"}
    return {"status": "failed", "provider": "stripe"}