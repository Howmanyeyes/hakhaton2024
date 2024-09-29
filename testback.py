try:
    from fastapi import FastAPI, File, UploadFile, Form
    from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
    from pathlib import Path
    # import shutil
    import threading
    import uvicorn
    import pandas as pd
    import io
    import os
    import asyncio
    import json
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

def ind_exel(n):
    result = ''
    if n == 0:
        return ''
    while n > 0:
        n -= 1  # Adjust for 0-indexed logic (Excel is 1-indexed)
        result = chr(n % 26 + 65) + result  # Convert to A-Z (65 is ASCII 'A')
        n //= 26
    return result+': '

def get_upload(file):
    f_content = file.file._file
    f_type = file.filename.split(".")[-1]
    f_name = generate_name()
    best_colormaps = ['MTC Special','viridis', 'plasma', 'inferno', 'magma', 'cividis', 'Spectral', 'coolwarm', 'YlGnBu', 'RdYlBu', 'PuBuGn', 'hsv']
    if f_type == 'csv':
        df = pd.read_csv(f_content)
    elif f_type == 'xlsx':
        df = pd.read_excel(f_content)
    else: # по умолчанию всё txt
        with open(f'{f_name}.txt', 'wb') as f:
            f.write(f_content.getvalue())
        return {
            "inputs": {
                "choose color scheme of clowd": {"type": "dropdown", "items": best_colormaps, "default": "red"},
                "filter profanity": {"type": "checkbox", "default": True}
            },
            "target_id": f"{f_name}.txt",
        }
    df.to_excel(f"{f_name}.xlsx", index=False, engine='openpyxl')
    
    cols = [f'{ind_exel(int(num))}{x}' for num, x in enumerate(["My info is in row"] + list(df.columns), 0)]
    # rows = len(df) не нужно пока что 
        
    return {
        "inputs": {
            "choose color scheme of clowd": {"type": "dropdown", "items": best_colormaps, "default": "red"},
            "choose column": {"type": "dropdown", "items": cols},
            "type number of row (ONLY if you use rows)": {"type": "text", "default": ""},
            "filter profanity": {"type": "checkbox", "default": True}
        },
        "target_id": f"{f_name}.xlsx"
    }

async def a_get_upload(file):
    return await asyncio.to_thread(get_upload, file)

@app.post('/rest/upload')
async def return_upload(file: UploadFile = File(...)):
    return await a_get_upload(file)

with open('bad_words.json', 'r') as f:
    BAD_WORDS = set(json.load(f)) # set кратно ускоряет проверку на вхождение относительно list

def filter_profanity(answers):
    l_words = [x for x in answers if type(x) == str] # and len(x) < 3]
    words = [x for x in l_words if x.lower() not in BAD_WORDS]
    return words
def red_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        red_value = 255  # Maximum red value to keep it bright
        green_value = random.randint(0, 50)  # Small random value for green (to keep red dominant)
        blue_value = random.randint(0, 50)  # Small random value for blue (to keep red bright)
        return f"rgb({red_value}, {green_value}, {blue_value})"

def create_wordcloud(rating, colour, name):
    # Create a WordCloud object with the specified color
    MTC = False
    if colour == "MTC Special":
        colour = 'viridis'
        MTC = True
    wordcloud = WordCloud(width=1000, height=1000, background_color="white", colormap=colour, random_state=42).generate_from_frequencies(rating)
    if MTC:
        wordcloud.recolor(color_func=red_color_func)
    # Display the generated word cloud
    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")  # No axis for cleaner look

    # Save the word cloud as a PNG file with the given name
    file_name = f"{name}.png"
    plt.savefig(f"generated/{file_name}", format="png", bbox_inches="tight")
    plt.close()

@app.post('/rest/process/')
async def return_image(request: dict):
    
    if request['target_id'].endswith('.txt'):
        answers = open(request['target_id'], 'r', encoding = 'utf8').read()
        # пайплайн чето тут ретюрн уже с картинкой
    inputs = request['inputs']
    df = pd.read_excel(request['target_id'])
   
    if inputs['choose column'] == 'My info is in row' and \
        inputs['type number of row (ONLY if you use rows)'] != '':
        answers = df.iloc[int(inputs['type number of row (ONLY if you use rows)'])]
    elif inputs['choose column'] == 'My info is in row' and \
        inputs['type number of row (ONLY if you use rows)'] == '':
        return 0 # return error - polzovatel dolbaeb
    else:
        answers = df[inputs['choose column'].split(': ')[1]]

    if inputs['filter profanity']:
        answers = filter_profanity(answers)
    else:
        answers = [x for x in answers if type(x) == str]
    # ретюрнить ансеры в пайплайн
    rating = {'suka': 1, 'kaaaaaaal':2,'pizda':3, 'ebnis':15} # await pipeline_text(answers) заглушка, с тобой делать надо, дебагер выдает ошибку:     while len(data) > 60: TypeError: object of type 'coroutine' has no len()
    os.remove(f"{request['target_id']}")

    colour = request['inputs']['choose color scheme of clowd']
    create_wordcloud(rating, colour, request['target_id'])
    return {
        "image_url": f"/generated/{request['target_id']}.png"
    }
    

app.mount("/", StaticFiles(directory="frontend",html = True), name="static")


if __name__ =='__main__':
    import uvicorn
    uvicorn.run(app, port=80)