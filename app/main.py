"""import asyncio
import json
import os

from app.task_queue.worker import worker
from app.agents.orchestrator import build_graph


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "tickets.json")

graph = build_graph()

# 🔥 CONFIG
QUEUE_SIZE = 100
WORKERS = 10   # increase to 20/50 for more parallelism


# =========================
# 🔹 PROCESS FUNCTION
# =========================
async def process_ticket(ticket):
    try:
        result = graph.invoke({"ticket": ticket})
        print(f"✅ Processed: {ticket['ticket_id']}")
        return result
    except Exception as e:
        print(f"❌ Failed: {ticket['ticket_id']} → {e}")
        return {"status": "failed", "ticket": ticket}


# =========================
# 🔹 PRODUCER (CONTINUOUS INPUT)
# =========================
async def producer(queue):
    with open(DATA_PATH) as f:
        tickets = json.load(f)

    i = 0
    while True:
        ticket = tickets[i % len(tickets)]

        await queue.put(ticket)
        print(f"📥 Incoming: {ticket['ticket_id']}")

        i += 1
        await asyncio.sleep(0.5)  # simulate real-time traffic


# =========================
# 🔹 MAIN LOOP
# =========================
async def main():
    queue = asyncio.Queue(maxsize=QUEUE_SIZE)

    # 🔥 Start workers (parallel consumers)
    for _ in range(WORKERS):
        asyncio.create_task(worker(queue, process_ticket))

    # 🔥 Start producer (continuous stream)
    await producer(queue)


if __name__ == "__main__":
    asyncio.run(main())
"""
import asyncio
import json
import os

from app.task_queue.worker import worker
from app.agents.orchestrator import build_graph

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "tickets.json")

graph = build_graph()

# 🔥 CONFIG
QUEUE_SIZE = 100
WORKERS = 10   # increase to 20/50 for more parallelism


# =========================
# 🔹 PROCESS FUNCTION
# =========================
async def process_ticket(ticket):
    try:
        result = graph.invoke({"ticket": ticket})
        print(f"✅ Processed: {ticket['ticket_id']}")
        return result
    except Exception as e:
        print(f"❌ Failed: {ticket['ticket_id']} → {e}")
        return {"status": "failed", "ticket": ticket}


# =========================
# 🔹 PRODUCER (CONTINUOUS INPUT)  🚫 (NOT USED NOW, KEPT)
# =========================
async def producer(queue):
    try:
        with open(DATA_PATH) as f:
            tickets = json.load(f)

        i = 0
        while True:
            ticket = tickets[i % len(tickets)]

            await queue.put(ticket)
            print(f"📥 Incoming: {ticket['ticket_id']}")

            i += 1
            await asyncio.sleep(0.5)

    except asyncio.CancelledError:
        print("🛑 Producer stopped gracefully")


# =========================
# 🔹 MAIN (BATCH JSON PIPELINE) ✅
# =========================
async def main():
    from app.utils.file_utils import load_json, save_json

    INCOMING = os.path.join(BASE_DIR, "data", "incoming.json")
    PROCESSING = os.path.join(BASE_DIR, "data", "processing.json")
    COMPLETED = os.path.join(BASE_DIR, "data", "completed.json")
    TICKETS = os.path.join(BASE_DIR, "data", "tickets.json")

    incoming = load_json(INCOMING)

    # 🔥 AUTO LOAD if empty
    if not incoming:
        print("⚡ Loading tickets.json into incoming queue...")
        incoming = load_json(TICKETS)
        save_json(INCOMING, incoming)

    # reload after possible update
    incoming = load_json(INCOMING)
    processing = load_json(PROCESSING)
    completed = load_json(COMPLETED)

    print(f"📥 Total incoming tickets: {len(incoming)}")

    results = []

    while incoming:
        ticket = incoming.pop(0)

        # 👉 move to processing
        processing.append(ticket)
        save_json(PROCESSING, processing)
        save_json(INCOMING, incoming)

        print(f"⚙️ Processing: {ticket['ticket_id']}")

        # 👉 process
        result = await process_ticket(ticket)

        # 👉 remove from processing
        processing = [
            t for t in processing if t["ticket_id"] != ticket["ticket_id"]
        ]
        save_json(PROCESSING, processing)

        # 👉 move to completed
        completed.append(result)
        save_json(COMPLETED, completed)

        print(f"✅ Completed: {ticket['ticket_id']}")

        results.append(result)

    print("\n🎉 ALL TICKETS PROCESSED\n")

    for r in results:
        print(r)


# =========================
# 🔹 ENTRY
# =========================
if __name__ == "__main__":
    asyncio.run(main())