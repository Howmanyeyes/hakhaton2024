from llama import llama

class Synonyms:
    def __init__(self, api_url):
        self.llama = llama(api_url, 'synonyms')
    SYSTEM = """You are an advanced language model specialized in analyzing survey data. Your task is to process a list of textual survey responses, group them based on synonymous or similar meanings, and generate concise group names. Each group name should encapsulate the group's meaning in 1-3 words. Provide a maximum of 50 group names, sorted from the most to the least popular based on the number of responses in each group. The output should be two column in csv format: group names and index of group mass (how many rows are included in it). Ensure that the group names are clear, distinct, and accurately represent the underlying responses in their original language without being overly generic or ambiguous. Your response must contain only requested data and nothing else."""
    MODELFILE = f"""FROM llama3.2:3b
PARAMETER temperature 0.5
SYSTEM {SYSTEM}
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
        return res, json

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
    res, answer = await syn.process('\n'.join(data))
    print(answer.get('response', answer))

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())