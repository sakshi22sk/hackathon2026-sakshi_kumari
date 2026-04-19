def escalate(ticket_id, summary, priority):
    return {
        "status": "escalated",
        "ticket_id": ticket_id,
        "priority": priority,
        "summary": summary
    }