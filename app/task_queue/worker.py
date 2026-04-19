import asyncio
from app.config import MAX_RETRIES

dead_letter_queue = []


async def worker(queue, process_func):
    while True:  # 🔥 infinite loop
        ticket = await queue.get()

        try:
            result = await process_func(ticket)
            print("✅ Done:", result["ticket"]["ticket_id"])

        except Exception as e:
            print("❌ Failed:", e)

        finally:
            queue.task_done()