from app.agents.classifier import classify_ticket_nlp

def decide(state):
    ticket = state["ticket"]

    result = classify_ticket_nlp(ticket)

    priority = result.get("priority", "LOW")   # ❗ FIXED (was MEDIUM before)
    source = result.get("source", "unknown")

    # ✅ DECISION LOGIC
    if priority == "HIGH":
        decision = "escalate"
        confidence = 0.95

    elif priority == "MEDIUM":
        decision = "escalate"
        confidence = 0.75

    else:
        decision = "resolve"
        confidence = 0.85

    return {
        **state,
        "decision": decision,
        "priority": priority,
        "confidence": confidence,
        "reason": f"{source} classification → {priority}"
    }