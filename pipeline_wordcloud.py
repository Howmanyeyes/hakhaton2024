
from synonyms import Synonyms
from typing import Iterable
import asyncio

MAX_BATCH = 300
MAX_OUT = 60

def response_formatter(response: str):
    strs = response.split('\n')
    ans = []
    longcounter = 0
    for str in strs:
        str = ''.join(s for s in str.strip() if s.isalpha() or s == ' ')
        nwords = len(str.split(' '))
        if 0 < nwords <= 10 and not ':' in str: ans.append(str)
        else: longcounter += 1

        if longcounter >= 3:
                print('HIT LONGCOUNTER')
                return []
    return ans 

model = Synonyms('https://hack.agicotech.ru/api', MAX_OUT)
asyncio.run(model.check_model())

async def tree_iteration(data : list):
    batch_amount = (len(data) + MAX_BATCH - 1) // MAX_BATCH
    batch_size = (len(data) + batch_amount - 1) // batch_amount
    data_array = []
    for i in range(0, len(data), batch_size):
        print(f'PROCESSED BATCH {i}')
        batch = data[i:i+batch_size]
        batch_res = await pipeline_array_words(batch)
        data_array += batch_res
    return data_array

async def pipeline_array_words(data: Iterable[str] | str):
    input = '\n'.join(data)
    for i in range(10):
        data = await model.process(input)
        data = response_formatter(data)
        if len(data):
            print(f'OK RESPONSE IN {i} REQUEST')
            return data
    return []

def remove_multiple_spaces(s: str):
    s = ' '.join(subs for subs in s.split(' ') if len(subs))
    return s

def remove_empty_lines_and_spaces(text: Iterable[str]):
    yield from (remove_multiple_spaces(s) for s in text if len(s))

async def pipeline_text(data: str | Iterable[str]):
    if type(data) == str: data = data.split('\n')
    data = list(remove_empty_lines_and_spaces(data))
    data = await tree_iteration(data)
    l = len(data)
    while l > MAX_OUT:
        print(f'HIT MAX_OUT : {l}/{MAX_OUT}')
        data = await tree_iteration(data)
        l = len(data)
    return {s : i for i, s in enumerate(data[::-1], 1)}