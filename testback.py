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
    import random
    import string
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

def generate_name():
    return ''.join(random.choices(string.ascii_lowercase, k=8))


@app.post('/rest/upload')
def return_upload(file: UploadFile = File(...)):
    f_content = file.file._file
    f_type = file.filename.split(".")[-1]
    f_name = generate_name()
    if f_type == 'csv':
        df = pd.read_csv(f_content)
    elif f_type == 'xlsx':
        df = pd.read_excel(f_content)
    elif f_type == 'txt':
        with open(f'{f_name}.txt', 'wb') as f:
            f.write(f_content.getvalue())
        return {
            "inputs": {
                "choose color scheme of clowd": {"type": "dropdown", "items": ["red, green, blue"], "default": "red"}
            },
            "target_id": f"{f_name}.txt",
        }
    else:
        return 0 # пиздец а не файл
    df.to_excel(f"{f_type}_{f_name}.xlsx", index=False, engine='openpyxl')
    cols = list(df.columns)
    # rows = len(df) не нужно пока что 
        
    return {
        "inputs": {
            "choose color scheme of clowd": {"type": "dropdown", "items": ["red, green, blue"], "default": "red"},
            "choose column": {"type": "dropdown", "items": cols},
            "type number of row": {"type": "text", "default": ""}
        },
        "target_id": f"{f_name}.xlsx"
    }

@app.post('/rest/process/')
def return_image(data: JSONResponse):
    print(data)
    print(1)
    return {
        "image_url": "/generated/test.jpg"
    }
    

app.mount("/", StaticFiles(directory="frontend",html = True), name="static")


if __name__ =='__main__':
    import uvicorn
    uvicorn.run(app, port=80)