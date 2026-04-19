import os
import json
from dotenv import load_dotenv
from groq import Groq
load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

# ✅ Initialize client ONLY if key exists
if api_key:
    client = Groq(api_key=api_key)
else:
    print("⚠️ No API key found → using rule-based fallback")
    client = None


# =========================
# 🔹 RULE-BASED CLASSIFIER (SHARED)
# =========================
def rule_based_classification(text, source="rule_based"):
    text = text.lower()

    # 🔴 HIGH PRIORITY (critical cases)
    if any(word in text for word in [
        "hacked", "fraud", "unauthorized", "money deducted", "stolen", "account hacked"
    ]):
        return {"priority": "HIGH", "category": "fraud", "source": source}

    if any(word in text for word in [
        "not received", "missing", "lost package", "never arrived"
    ]):
        return {"priority": "HIGH", "category": "delivery", "source": source}

    # 🟠 MEDIUM PRIORITY
    if any(word in text for word in [
        "delay", "late", "shipping issue", "where is my order"
    ]):
        return {"priority": "MEDIUM", "category": "delivery", "source": source}

    if any(word in text for word in [
        "cancel", "change order", "modify order"
    ]):
        return {"priority": "MEDIUM", "category": "order", "source": source}

    # 🟢 LOW PRIORITY
    if any(word in text for word in [
        "refund", "return", "exchange", "replace", "damaged"
    ]):
        return {"priority": "LOW", "category": "refund", "source": source}

    return {"priority": "LOW", "category": "general", "source": source}

# =========================
# 🔹 MAIN CLASSIFIER
# =========================
def classify_ticket_nlp(ticket):
    text = ticket["body"]

    # =========================
    # ✅ CASE 1: NO API → RULE BASED
    # =========================
    if client is None:
        return rule_based_classification(text, source="rule_based")

    # =========================
    # 🤖 CASE 2: NLP AVAILABLE
    # =========================
    try:
        prompt = f"""
        Classify this support ticket into:
        - priority: HIGH, MEDIUM, or LOW
        - category: refund, delivery, fraud, order, general

        Ticket:
        {text}

        Respond ONLY in JSON format:
        {{
            "priority": "HIGH",
            "category": "fraud"
        }}
        """
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
)

        content = response.choices[0].message.content.strip()

        # ✅ SAFE PARSE (NO eval)
        try:
            result = json.loads(content)
        except:
            print("⚠️ Invalid JSON from LLM → fallback")
            return rule_based_classification(text, source="fallback_parse")

        # ✅ VALIDATE OUTPUT
        if "priority" not in result or "category" not in result:
            print("⚠️ Incomplete LLM response → fallback")
            return rule_based_classification(text, source="fallback_validation")

        result["source"] = "nlp"

        return result

    # =========================
    # 🔥 CASE 3: API FAILS
    # =========================
    except Exception as e:
        print(f"⚠️ NLP failed → fallback triggered: {e}")
        return rule_based_classification(text, source="fallback_api")