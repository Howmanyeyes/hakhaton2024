try:
    from fastapi import FastAPI, File, UploadFile, Form
    from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
    from pathlib import Path
    # import shutil
    import threading
    import uvicorn
    import pandas as pd
    import io
    import asyncio
    import httpx
    import matplotlib.pyplot as plt
    from wordcloud import WordCloud
    from fastapi.responses import StreamingResponse
    from pipeline_wordcloud import pipeline_text
    from fastapi.staticfiles import StaticFiles

except ModuleNotFoundError:
    import os, sys
    os.system(f'{sys.executable} -m pip install -r req.txt')
    exit(0)

app = FastAPI(root_path='')

app.mount("/generated", StaticFiles(directory="generated"), name="generated")


@app.post('/rest/upload')
def return_upload(file: UploadFile):
    return {
        "inputs": {
            "enableFeature": {"type": "toggle", "value": True},
            "colorScheme": {"type": "dropdown", "items": ["Red", "Green", "Blue"]},
            "includeNumbers": {"type": "checkbox"},
            "fontSize": {"type": "text", "default": "12"}
        },
        "target_id": "unique-target-id",
    }

@app.post('/rest/process')
def return_image(data: JSONResponse):
    return {
        "image_url": "/generated/test.jpg"
    }
    

app.mount("/", StaticFiles(directory="frontend",html = True), name="static")


if __name__ =='__main__':
    import uvicorn
    uvicorn.run(app, port=80)