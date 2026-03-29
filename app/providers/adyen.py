import random

def process_payment(amount: float):
    if random.random() > 0.5:
        return {"status": "success", "provider": "adyen"}
    return {"status": "failed", "provider": "adyen"}