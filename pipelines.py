
from synonyms import Synonyms
from chatapi import Synonims_chatgpt
from typing import Iterable
import asyncio
from decouple import config

MAX_BATCH = 600

#model = Synonyms('https://hack.agicotech.ru/api', MAX_OUT)
#asyncio.run(model.check_model()) 
# LLama работает прямо скажем так себе\

model = Synonims_chatgpt(config('TOKEN'), config('BASE_URL'))

async def divided_process(data : list):
    """Обработка результатов по кускам"""
    batch_amount = (len(data) + MAX_BATCH - 1) // MAX_BATCH # Количество запросов
    batch_size = (len(data) + batch_amount - 1) // batch_amount # Размер запроса
    result = {}
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        batch_res = {}
        batch_res = await pipeline_array_words(batch)

        for k, v in batch_res.items():
            if k in result:
                result[k] += v/batch_amount
            else:
                result[k] = v/batch_amount
        return result



async def pipeline_array_words(data: Iterable[str] | str): 
    input = '\n'.join(data)
    for i in range(3):# Нейросеть иногда выдает некрасивые данные
        data = await model.process(input)
        if len(data):
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