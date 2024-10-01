
from synonyms import Synonyms
from chatapi import Synonims_chatgpt
from typing import Iterable
import asyncio
from decouple import config

MAX_BATCH = 600

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

#model = Synonyms('https://hack.agicotech.ru/api', MAX_OUT)
#asyncio.run(model.check_model()) 
# LLama работает прямо скажем так себе\

model = Synonims_chatgpt(config('TOKEN'), config('BASE_URL'))

async def divided_process(data : list):
    """Обработка результатов по кускам"""
    batch_amount = (len(data) + MAX_BATCH - 1) // MAX_BATCH
    batch_size = (len(data) + batch_amount - 1) // batch_amount
    result = {}
    for i in range(0, len(data), batch_size):
        print(f'PROCESSED BATCH {i}')
        batch = data[i:i+batch_size]
        batch_res = {}
        for _ in range(3):
            batch_res = await pipeline_array_words(batch)
            if len(batch_res):
                break
        for k, v in batch_res.items():
            if k in result:
                result[k] += v/batch_amount
            else:
                result[k] = v/batch_amount
        return result



async def pipeline_array_words(data: Iterable[str] | str):
    input = '\n'.join(data)
    for i in range(10):
        data = await model.process(input)
        #data = response_formatter(data)
        if len(data):
            print(f'OK RESPONSE IN {i} REQUEST')
            return data
    return {}

def remove_multiple_spaces(s: str):
    s = ' '.join(subs for subs in s.split(' ') if len(subs))
    return s

def remove_empty_lines_and_spaces(text: Iterable[str]):
    yield from (remove_multiple_spaces(s) for s in text if len(s))

async def pipeline_text(data: str | Iterable[str]):
    if type(data) == str: data = data.split('\n')
    data = list(remove_empty_lines_and_spaces(data))
    data = await divided_process(data)
    return data