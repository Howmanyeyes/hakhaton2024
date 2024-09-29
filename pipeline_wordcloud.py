
from synonyms import Synonyms
from typing import Iterable
import asyncio

MAX_BATCH = 300
MAX_OUT = 60

def strlistfmt(strs: Iterable):
            for str in strs:
                str = ''.join(s for s in str.strip() if s.isalpha() or s == ' ')
                if len(str) and not ':' in str: yield str

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

async def pipeline_array_words(data: Iterable[str] | str):
    data = await model.process(data)
    if data is None:
        data = ''
    data = response_formatter(data)
    return data

def remove_multiple_spaces(s: str):
    s = ' '.join(subs for subs in s.split(' ') if len(subs))
    return s

def remove_empty_lines_and_spaces(text: Iterable[str]):
    yield from (remove_multiple_spaces(s) for s in text if len(s))

async def pipeline_text(data: str | Iterable[str]):
    if type(data) == str: data = data.split('\n')
    data = list(remove_empty_lines_and_spaces(data))
    data = await tree_iteration(data)
    while len(data) > MAX_OUT:
        data = await tree_iteration(data)
    return {s : i for i, s in enumerate(data[::-1], 1)}