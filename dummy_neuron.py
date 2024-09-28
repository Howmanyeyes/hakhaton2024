from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from pathlib import Path
# import shutil
import uvicorn
import json
import pandas as pd
import io
import asyncio
import httpx
import time
app = FastAPI()


@app.post("/sort/")
async def sort(words: dict):
    words = {"suka": 1, "kal": 5, "ebal": 2}
    asyncio.sleep(3)
    return words


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1337)