
from synonyms import Synonyms
from typing import Iterable
import asyncio

MAX_BATCH = 300
MAX_OUT = 60

def strlistfmt(strs: Iterable):
            for str in strs:
                str = str.split('. ')[-1].strip()
                if len(str): yield str

def response_formatter(response):
    response = response.split('\n')
    return list(strlistfmt(response))

model = Synonyms('https://hack.agicotech.ru/api')
asyncio.run(model.check_model())

async def tree_iteration(data : list):
    batch_amount = (len(data) + MAX_BATCH - 1) // MAX_BATCH
    batch_size = (len(data) + batch_amount - 1) // batch_amount
    data_array = []
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        batch_res = await pipeline_array_words(batch)
        data_array += batch_res
    return data_array

async def pipeline_array_words(data: Iterable[str]):
    data = await model.process(data)
    if data is None:
        data = ''
    data = response_formatter(data)
    return data

async def pipeline_text(data: str | Iterable[str]):
    if type(data) == str: data = data.split('\n')
    data = pipeline_array_words(data)
    while len(data) > 60:
        data = pipeline_array_words(data)
    return {s : i for i, s in enumerate(data[::-1])}