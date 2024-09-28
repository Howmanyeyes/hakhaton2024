try:
    from fastapi import FastAPI, File, UploadFile, Form
    from fastapi.responses import HTMLResponse
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
except ModuleNotFoundError:
    import os, sys
    os.system(f'{sys.executable} -m pip install -r req.txt')
    exit(0)

app = FastAPI()


class Q:
    def __init__(self):
        self.que = []
        self.lenght = 0
    
    def avaliability_c(self):
        if self.lenght == 0:
            return True
        else:
            return False

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


def get_and_filter(df, what_look):
    
    l_words = list(df[what_look])
    l_words = [x for x in l_words if type(x) == str and len(x) < 3] #IIIIIIIIIIIIISSSSSSSPTRAVIT
    
    '''
    # filtration starts here
    bad_words = ['fuck', 'shit', 'bitch']
    words = ' \n '.join(l_words)
    words = words.split(' ')
    words = [x for x in words if x.lower() not in bad_words]
    words = ' '.join(words)
    # filtered
    '''
    import time
    time.sleep(10)

    words = '\n'.join(l_words) #this line needed only when no filtering
    return words

async def a_get_and_filter(df, what_look):
    words = await asyncio.to_thread(get_and_filter, df, what_look)
    return words

@app.post("/simple_upload/")
async def upload_file(what_look: str = Form(...), file: UploadFile = File(...)):
    
    contents = await file.read()
    f_format = file.filename.split(".")[-1]
    if f_format == 'csv':
        df = pd.read_csv(io.StringIO(contents.decode()))
    elif f_format == 'xlsx':
        df = pd.read_excel(io.BytesIO(contents))

    if what_look not in df.head():
        return 0
    
    """get_and_filter_t = threading.Thread(target=get_and_filter, args=(df, what_look))
    words = get_and_filter_t.start()
    while get_and_filter_t.is_alive():
        await asyncio.sleep(0.01)
        print('thread is alive')
        get_and_filter_t.join()""" # threads try
    try:
        words = await a_get_and_filter(df, what_look)
    except Exception as e:
        print(e)
        return 0
    print(words)
        
    """async with httpx.AsyncClient() as client:
        words = await client.post('http://localhost:1337/sort/', json = {'words': words})
        
    

    # words = words.json() надо тут чето сделать вместо евала
    words = eval(words._content)
    
    weighted_words = [[x, y] for x, y in zip(words.keys(), words.values())]
    # print(weighted_words)
    """
    words = pipeline_text(words) # Возвращает {строка : вес}

    wc = WordCloud(background_color="white", max_words=1000)
    wc.generate_from_frequencies(words)
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    # plt.savefig('foo.png')


    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
    return que_num

# @app.get("/get_clowd/")
# async def get_clowd():

    
    # plt.show() for debug, just to see picture
    
        

@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...), file_type: str = Form(...), where_look: str = Form(...), what_look: str = Form(...)):
    # Read the file contents
    contents = await file.read()
    f_format = file.filename.split(".")[-1]
    if f_format == 'csv':
        df = pd.read_csv(io.StringIO(contents.decode()))
    if f_format == 'xlsx':
        df = pd.read_excel(io.BytesIO(contents))
    
    if (where_look == 'col' or where_look == 'idk') and what_look in df.haed():
        pass
    elif where_look == 'row' and what_look == int:
        pass
    else:
        return 0


    print(df)
    
    # Return the file contents in the response as a string (for text files)
    # return {"file_name": file.filename, "content": contents.decode("utf-8")}  # Decode as utf-8 for text files




# To run the server, use this command:
# uvicorn main:app --reload


if __name__ == "__main__":
    QUE = Q()
    QUE.que.append('kal\ngovno\nshit')
    uvicorn.run(app, host="0.0.0.0", port=8000)
