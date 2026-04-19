import json

def get_customer(email):
    with open("data/customers.json") as f:
        customers = json.load(f)

    for c in customers:
        if c["email"] == email:
            return c
    return None