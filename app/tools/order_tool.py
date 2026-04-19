import json

ORDERS_MAP = None

def load_orders():
    global ORDERS_MAP

    if ORDERS_MAP is None:
        file_path = r"D:\Ksolves\app\data\orders.json"
        print("📂 Loading orders ONCE from:", file_path)

        with open(file_path, "r") as f:
            data = json.load(f)

        # handle both formats
        orders = data.get("orders", []) if isinstance(data, dict) else data

        # ✅ convert list → dict (O(1) lookup)
        ORDERS_MAP = {
            str(o.get("order_id")).strip(): o
            for o in orders
        }

        print("✅ Total orders loaded:", len(ORDERS_MAP))

    return ORDERS_MAP


def get_order(order_id: str):
    orders_map = load_orders()

    order_id = str(order_id).strip()
    print(f"🔍 Looking for order_id: {order_id}")

    order = orders_map.get(order_id)

    if order:
        print(f"✅ Found order: {order_id}")
        return order

    print(f"❌ Order NOT found: {order_id}")
    return None