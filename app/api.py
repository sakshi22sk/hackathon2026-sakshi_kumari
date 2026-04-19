from fastapi import FastAPI
import asyncio
from app.agents.orchestrator import build_graph

app = FastAPI()

graph = build_graph()

# 🔥 in-memory queue
queue = asyncio.Queue()

# store results for UI
results_store = {}


# =========================
# 🔹 WORKER (runs forever)
# =========================
async def worker():
    while True:
        ticket, job_id = await queue.get()

        try:
            result = graph.invoke({"ticket": ticket})
            results_store[job_id] = {
                "status": "done",
                "result": result
            }
        except Exception as e:
            results_store[job_id] = {
                "status": "failed",
                "error": str(e)
            }

        queue.task_done()


# =========================
# 🔹 START WORKERS
# =========================
@app.on_event("startup")
async def start_workers():
    for _ in range(10):  # 🔥 parallel workers
        asyncio.create_task(worker())


# =========================
# 🔹 API ENDPOINTS
# =========================
@app.get("/")
def home():
    return {"status": "Running 🚀"}


@app.post("/ticket")
async def submit_ticket(ticket: dict):
    job_id = str(len(results_store) + 1)

    results_store[job_id] = {"status": "queued"}

    await queue.put((ticket, job_id))

    return {
        "job_id": job_id,
        "status": "queued"
    }


@app.get("/job/{job_id}")
def get_status(job_id: str):
    return results_store.get(job_id, {"status": "not_found"})