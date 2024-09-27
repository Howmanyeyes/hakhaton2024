from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse
from pathlib import Path
# import shutil
import uvicorn
import pandas as pd
import io

app = FastAPI()

# Path to the HTML file
html_file_path = Path(__file__).parent / "front.html"

@app.get("/", response_class=HTMLResponse)
async def read_root():
    # Read the content of the HTML file
    if html_file_path.exists():
        html_content = html_file_path.read_text(encoding='utf-8')
        return HTMLResponse(content=html_content)
    else:
        return HTMLResponse(content="<h1>Error: front.html not found!</h1>", status_code=404)

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...), file_type: str = Form(...), where_look: str = Form(...), what_look: str = Form(...)):
    # Read the file contents
    contents = await file.read()
    f_format = file.filename.split(".")[-1]
    if f_format == 'csv':
        df = pd.read_csv(io.StringIO(contents.decode()))
    if f_format == 'xlsx':
        df = pd.read_excel(io.BytesIO(contents))
        

    print(df)
    
    # Return the file contents in the response as a string (for text files)
    # return {"file_name": file.filename, "content": contents.decode("utf-8")}  # Decode as utf-8 for text files




# To run the server, use this command:
# uvicorn main:app --reload


if __name__ == "__main__":
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
