from langgraph.graph import StateGraph
from typing import TypedDict
from app.agents.classifier import classify_ticket_nlp
from app.tools.order_tool import get_order
from app.tools.customer_tool import get_customer
from app.tools.refund_tool import check_refund_eligibility, issue_refund
from app.tools.notification_tool import send_reply
from app.tools.escalation_tool import escalate


from typing import TypedDict
class AgentState(TypedDict):
    ticket: dict
    customer: dict
    order: dict
    decision: str
    response: str
    confidence: float
    reason: str
    priority: str  

# STEP 1: Fetch data
def fetch_data(state):
    ticket = state["ticket"]

    customer = get_customer(ticket["customer_email"])
    order = get_order(ticket["order_id"])

    if not customer:
        raise Exception("Customer not found")

    if not order:
        return {
            **state,
            "customer": customer,
            "order": None,
            "decision": "escalate",
            "response": "Order not found → escalated"
        }

    # ✅ ADD THIS RETURN (CRITICAL FIX)
    return {
        **state,
        "customer": customer,
        "order": order
    }

# STEP 2: Decide action


def decide(state):
    ticket = state["ticket"]

    result = classify_ticket_nlp(ticket)

    priority = result.get("priority", "MEDIUM")
    source = result.get("source", "unknown")

    if priority == "HIGH":
        decision = "escalate"
        confidence = 0.9
    elif priority == "MEDIUM":
        decision = "escalate"
        confidence = 0.7
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

# STEP 3: Resolve
def resolve(state):
    order = state.get("order")

    # ❗ FIX: prevent crash
    if not order:
        return {
            **state,
            "decision": "escalate",
            "priority": "LOW",
            "confidence": 0.3,
            "reason": "No purchase found for this order ID",
            "response": "Request rejected: No purchase found for this order ID"
        }

    return {
        **state,
        "response": f"Refund issued: {{'status': 'success', 'amount': {order['amount']}}}"
    }

# STEP 4: Escalate
def escalate_node(state):
    ticket = state["ticket"]

    result = escalate(
    ticket["ticket_id"],
    state.get("reason", ""),
    state.get("priority", "MEDIUM")
)

    return {**state, "response": str(result)}


# BUILD GRAPH
def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("fetch", fetch_data)
    graph.add_node("decide", decide)
    graph.add_node("resolve", resolve)
    graph.add_node("escalate", escalate_node)

    graph.set_entry_point("fetch")

    graph.add_edge("fetch", "decide")

    graph.add_conditional_edges(
        "decide",
        lambda state: state["decision"],
        {
            "resolve": "resolve",
            "escalate": "escalate"
        }
    )

    graph.set_finish_point("resolve")
    graph.set_finish_point("escalate")

    return graph.compile()