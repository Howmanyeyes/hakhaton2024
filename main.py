try:
    from fastapi import FastAPI, File, UploadFile
    import uvicorn
    import pandas as pd
    import os
    import asyncio
    import json
    import random
    import string
    import matplotlib.pyplot as plt
    from wordcloud import WordCloud
    from pipelines import pipeline_text
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
        n -= 1  
        result = chr(n % 26 + 65) + result  # 65 = 'A'
        n //= 26
    return result+': '

def get_upload(file):
    f_content = file.file._file
    f_type = file.filename.split(".")[-1]
    f_name = generate_name()
    best_colormaps = ['MTC Special','viridis', 'plasma', 'inferno', 'magma', \
                      'cividis', 'Spectral', 'coolwarm', 'YlGnBu', 'RdYlBu', \
                      'PuBuGn', 'hsv']
    if f_type == 'csv':
        df = pd.read_csv(f_content)
    elif f_type == 'xlsx':
        df = pd.read_excel(f_content)
    else: # по умолчанию всё txt
        with open(f'temp_tables/{f_name}.txt', 'wb') as f:
            f.write(f_content.getvalue())
        return {
            "inputs": {
                "Цветовая гамма Облака": {"type": "dropdown", \
                                                 "items": best_colormaps, "default": "red"},
                "Цензор": {"type": "checkbox", "default": True}
            },
            "target_id": f"{f_name}.txt",
        }
    df.to_pickle(f"temp_tables/{f_name}.pkl")
    
    cols = [f'{ind_exel(int(num))}{x}' for num, x in enumerate(["My info is in row"] + list(df.columns), 0)]        
    return {
        "inputs": {
            "Цветовая гамма Облака": {"type": "dropdown", \
                                             "items": best_colormaps, "default": "red"},
            "Выберите столбец": {"type": "dropdown", "items": cols},
            "Выберите строку (ТОЛЬКО отдельно от столбца)": {"type": "text", "default": ""},
            "Цензор": {"type": "checkbox", "default": True}
        },
        "target_id": f"{f_name}.pkl"
    }

async def a_get_upload(file):
    return await asyncio.to_thread(get_upload, file)

@app.post('/rest/upload')
async def return_upload(file: UploadFile = File(...)):
    """Returns a dictionary with the uploaded file's name and possible inputs."""
    return await a_get_upload(file)

with open('bad_words.json', 'r') as f:
    BAD_WORDS = set(json.load(f)) # set кратно ускоряет проверку на вхождение относительно list

def filter_profanity(answers):
    l_words = [x for x in answers if type(x) == str]
    words = [x for x in l_words if x.lower() not in BAD_WORDS]
    return words

def red_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
        red_value = 255  
        green_value = random.randint(0, 50)
        blue_value = random.randint(0, 50)
        return f"rgb({red_value}, {green_value}, {blue_value})"

def create_wordcloud(rating, colour, name):
    MTC = False
    if colour == "MTC Special":
        colour = 'viridis'
        MTC = True
    wordcloud = WordCloud(width=1000, height=1000, background_color="white", \
                          colormap=colour, random_state=42, font_path='MTSWide-Bold.ttf')\
                            .generate_from_frequencies(rating)
    if MTC:
        wordcloud.recolor(color_func=red_color_func)
    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")  
    file_name = f"{name}.png"
    plt.savefig(f"generated/{file_name}", format="png", bbox_inches="tight")
    plt.close()

def get_answers(request: dict): 
    f_name = request['target_id']
    if f_name.endswith('.txt'):
        answers = open(f"temp_tables/{f_name}", 'r', encoding = 'utf8').read()
        os.remove(f"temp_tables/{f_name}")
        return answers
    inputs = request['inputs']
    df = pd.read_pickle(f"temp_tables/{f_name}")
   
    if inputs['Выберите столбец'] == 'My info is in row':
        if inputs['Выберите строку (ТОЛЬКО отдельно от столбца)'] != '':
            answers = df.iloc[int(inputs['Выберите строку (ТОЛЬКО отдельно от столбца)'])]
        else:
            return 0 # return error - polzovatel ne vvodil chislo
    else:
        answers = df[': '.join(inputs['Выберите столбец'].split(': ')[1:])]

    if inputs['Цензор']:
        answers = filter_profanity(answers)
    else:
        answers = [x for x in answers if type(x) == str]
    os.remove(f"temp_tables/{f_name}")
    if len(answers) == 0:
        return ['Некорректные данные', 'Некорректные данные', 'Некорректные данные']
    return answers

async def a_get_answers(request: dict):
    return await asyncio.to_thread(get_answers, request)

@app.post('/rest/process/')
async def return_image(request: dict):
    """Returns image url of wordcloud in form of dict"""
    picture_id = request['target_id'][:-4]
    answers = await a_get_answers(request=request)
    rating = await pipeline_text(answers) 
    colour = request['inputs']['Цветовая гамма Облака']
    create_wordcloud(rating, colour, picture_id)
    with open(f'generated/{picture_id}.json', 
              'w', encoding='utf-8') as json_file:
        json.dump(rating, json_file, ensure_ascii=False, indent=4)
    return {
        "image_url": f"/generated/{picture_id}.png"
    }

def generate_piechart(json_filename):
    # Load the JSON file
    with open(f"generated/{json_filename}.json", 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    # Extracting the names and volumes
    names = list(data.keys())
    volumes = list(data.values())

    # Ensure the output directory exists
    output_dir = "generated/"
    os.makedirs(output_dir, exist_ok=True)

    # Create a pie chart
    plt.figure(figsize=(6, 6))  # Set the figure size for the pie chart
    plt.pie(volumes, labels=names, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    # Define the file path where the chart will be saved
    output_path = os.path.join(output_dir, f'pie_{json_filename}.png')

    # Save the chart as an image
    plt.savefig(output_path)

@app.post('/rest/details/')
async def return_details(result_id: str):
    name = result_id
    generate_piechart(name)
    return {
        "pie_url": f"/generated/pie_{name}.png",
        "json_url": f"/generated/{name}.json",
        "image_url": f"/generated/{name}.png",

    }


app.mount("/", StaticFiles(directory="frontend",html = True), name="static")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, port=8000)