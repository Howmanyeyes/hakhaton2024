
from synonyms import Synonyms
from typing import Iterable
import asyncio
def strlistfmt(strs: Iterable):
            for str in strs:
                str = str.split('. ')[-1].strip()
                if len(str): yield str

def response_formatter(response):
    response = response.split('\n')
    return list(strlistfmt(response))

model = Synonyms('https://hack.agicotech.ru/api')
asyncio.run(model.check_model())

async def pipeline_text(data: str | Iterable[str]):
       data = await model.process(data)
       if data is None:
            data = ''
       data = response_formatter(data)
       data = {s:i for i, s in enumerate(data[::-1])}
       return data