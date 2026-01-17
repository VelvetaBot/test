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
        raise Exception("Serv
