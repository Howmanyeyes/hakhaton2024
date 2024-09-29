from llama import llama
from typing import Iterable
class Synonyms:
    def __init__(self, api_url, max_out):
        self.llama = llama(api_url, 'synonyms')
    #SYSTEM = """Ты - продвинутая языковая модель и твоя задача - анализ результатов опросов. Тебе нужно сгруппировать полученные в виде столбца строк ответы по смыслу в группы с синонимичным значением. В ответ давай ТОЛЬКО названия групп, каждое - от 1 до 3 слов в отельной строке"""
        self.SYSTEM = f"""Ты - продвинутая языковая модель и твоя задача - анализ результатов опросов. Среди всех предоставленных построчно ответов объедини все синонимичные. Все ответы надо сократить до 1-3 слов с сохранением смысла и языка. В ответ дай ТОЛЬКО обработанную информацию - не более {max_out} самых популярных ответов, разделенные новой строкой, БЕЗ нумерации и прочих пояснений."""

        self.MODELFILE = f"""FROM llama3.2:3b
PARAMETER temperature 0.5
SYSTEM {self.SYSTEM}
"""
    async def check_model(self):
        res, models = await self.llama.ps()
        if not res:
            return
        models = models.get('models', [])
        if any(model['name'] == 'synonyms' for model in models):
            return
        await self.llama.pull('llama3.2:3b')
        await self.llama.create('synonyms', self.MODELFILE)


    async def process(self, data: str):
        res, json = await self.llama.generate(prompt=data, system=self.SYSTEM)
        if not res: return ''
        text = json.get('response', '')
        print(text)
        return text

async def main():
    syn = Synonyms('https://hack.agicotech.ru/api')
    await syn.check_model()
    data = []
    for _ in range(1000):
        s = input()
        if len(s):
            data.append(s)
        else:
            break
    answer = await syn.process(data)
    print(answer)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())