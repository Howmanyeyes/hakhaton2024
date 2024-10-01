import re
import json
import aiohttp



class OpenAI():

    async def chat_completions_create(**payload):
        ...

    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.chat_completions_create = self._send_to_openai(f'{self.base_url}/chat/completions')

    def _send_to_openai(self, endpoint_url: str,):
        async def send_to_openai(**payload: dict) -> aiohttp.ClientResponse:
            #payload['api_key'] = self.api_key
            """
            Send a request to openai.
            :param api_key: your api key
            :param timeout: timeout in seconds
            :param payload: the request body, as detailed here: https://beta.openai.com/docs/api-reference
            """
            async with aiohttp.ClientSession() as client:
                return await client.post(
                    url=endpoint_url,
                    json=payload,
                    headers={"content_type": "application/json", "Authorization": f"Bearer {self.api_key}"},
                )

        return send_to_openai

class Synonims_chatgpt:
    @staticmethod
    def isolate_json(text: str):
        data = re.search(r'\{.*?\}', text, re.DOTALL)
        if data:
            data = data.group(0)
            return json.loads(data)
        return {}


    def __init__(self, api_key, base_url) -> None:
        self.client  = OpenAI(api_key=api_key, \
                                base_url=base_url)
        self.init_prompt = \
 """You will receive several messages containing survey answers, each as a list of words or phrases. After receiving "end of data," group all similar answers by meaning and provide a summary of the groups. The summary should include the group name and the percentage of each group, with a maximum of 50 groups returned.

Format the result in JSON without any additional commentary or explanation.

Example Input:
message 1:
деньги
зарплата
хороший коллектив
хорошая зп
адекватные коллеги

message 2:
бесплатная еда в офисе
хорошие отпускные
дмс
оплата труда
гибкий график

message 3:
end of data

Example Output:
{
  "Зарплата": 50,
  "Коллектив": 20,
  "Удобный офис": 10,
  "Гибкий график": 10
}"""
    async def process(self, prompt: str):
        prompt = '\n'.join(s.strip() for s in prompt.split('\n') if len(s))
        response = await self.client.chat_completions_create(
            model="gpt-4o",
            messages=[{"role": "user", "content": self.init_prompt}, {"role": "user", "content": prompt}]
            #,stream=True
            #,timeout=600
            )
        resp_text = await response.json()
        resp_text = resp_text['choices'][0]['message']['content']
        return self.isolate_json(resp_text)
    
async def main():
    from decouple import config
    syns = Synonims_chatgpt(config('TOKEN'), config('BASE_URL'))
    with open('test_data.txt', 'r', encoding='utf-8') as f:
        data = f.read()
    ans = await syns.process(data)
    print(ans)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())