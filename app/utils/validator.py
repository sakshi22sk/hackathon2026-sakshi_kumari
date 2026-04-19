def validate_ticket(ticket):
    if "ticket_id" not in ticket:
        raise ValueError("Missing ticket_id")
    if "customer_email" not in ticket:
        raise ValueError("Missing customer_email")
    if "message" not in ticket:
        raise ValueError("Missing message")