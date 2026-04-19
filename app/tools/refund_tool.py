def check_refund_eligibility(order):
    if order["status"] != "delivered":
        return False, "Not delivered"
    return True, "Eligible"

def issue_refund(order_id, amount):
    return {"status": "success", "amount": amount}