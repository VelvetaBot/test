import os
import uuid
import time
import threading
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

PORT = int(os.getenv("PORT", 8000))

# In-memory task store
tasks = {}

class DownloadRequest(BaseModel):
    url: str
    quality: str   # e.g. "360p", "720p", "audio"

def fake_download(server_name, task_id):
    """
    Replace this with real downloader logic.
    This just simulates progress.
    """
    try:
        for i in range(1, 101):
            time.sleep(0.1)
            tasks[task_id]["progress"] = i
            tasks[task_id]["status"] = "downloading"
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["file"] = f"{task_id}.mp4"
    except:
        raise Exception("Server failed")

def run_with_fallback(task_id, url, quality):
    servers = ["server1", "server2", "server3"]

    for server in servers:
        try:
            tasks[task_id]["status"] = "loading"
            fake_download(server, task_id)   # replace with real logic
            return
        except:
            continue

    tasks[task_id]["status"] = "failed"

@app.post("/start")
def start_download(data: DownloadRequest):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {
        "url": data.url,
        "quality": data.quality,
        "progress": 0,
        "status": "loading",
        "file": None
    }

    t = threading.Thread(
        target=run_with_fallback,
        args=(task_id, data.url, data.quality),
        daemon=True
    )
    t.start()

    return {
        "task_id": task_id,
        "message": "Download started"
    }

@app.get("/status/{task_id}")
def get_status(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]
    return {
        "status": task["status"],
        "progress": task["progress"],
        "file": task["file"]
    }

@app.get("/")
def home():
    return {"status": "Server running"}

# For local run only
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=PORT)
