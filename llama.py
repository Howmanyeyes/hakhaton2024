import aiohttp
import asyncio
from pydantic import BaseModel
from typing import Literal, Optional

def get_kwargs(locals: dict):
    data = {k:v for k, v in locals.items() if not k in {'self', 'kwargs'} and v is not None}
    kwargs = locals.get('kwargs', {})
    if len(kwargs): data.update(kwargs)
    return data

class llama:
    def __init__ (self, api_url = f'http://localhost:11434/api', model = 'llama3.2:3b'):
        self.api_url = api_url.strip('/')
        self.model = model

    async def _api_call_post(self, endpoint, json = {}, resp_json = True):
        async with aiohttp.ClientSession() as session:
            resp = await session.post(f'{self.api_url}/{endpoint}', json = json)
            if resp.status == 200:
                return True, await (resp.json() if resp_json else resp.text())
            return False, await resp.text()
    
    async def _api_call_get(self, endpoint):
        async with aiohttp.ClientSession() as session:
            resp = await session.get(f'{self.api_url}/{endpoint}')
            if  resp.status == 200:
                return True, await resp.json()
            return False, await resp.text()


    async def generate(self,  prompt: str, # the prompt to generate a response for
                        model: str = None, # the model name
                        stream: bool = False, # if false the response will be returned as a single response object, rather than a stream of objects
                        suffix: str = None, # the text after the model response
                        format: str = None, # example: json
                        options: dict = None, # https://github.com/ollama/ollama/blob/main/docs/modelfile.md#valid-parameters-and-values
                        template: str = None, #  the prompt template to use (overrides what is defined in the Modelfile
                        system: str = None, # system message to (overrides what is defined in the Modelfile)
                        context: list = None, # the context parameter returned from a previous request to /generate, this can be used to keep a short conversational memory
                        images: list = None, # list of base64-encoded images
                        raw: bool = None, # if true no formatting will be applied to the prompt. You may choose to use the raw parameter if you are specifying a full templated prompt in your request to the API
                        keep_alive: str = None, # controls how long the model will stay loaded into memory following the request (default: 5m)
                        **kwargs):
        payload = get_kwargs(locals())
        if model is None: payload['model'] = self.model
        return await self._api_call_post('generate', json=payload)
    
    class Message(BaseModel):
        role : Literal['system', 'user', 'assistant', 'tool']
        content: str
        images: Optional[list[str]]
        tool_calls: Optional[list[str]]


    async def chat (self,
                    messages: list[Message],
                    tools = None,
                    model : str = None,
                    format: str = None,
                    options: dict = None,
                    stream: bool = False,
                    keep_alive : str = None
                   ):
        if model is None: payload['model'] = self.model
        payload = get_kwargs(locals())
        return await self._api_call_post('chat', json=payload)
    
    async def create(self,
                    name: str,
                    modelfile: str = None,
                    stream: bool = False,
                    path : str = None # path to ModelFile
                   ):
        payload = get_kwargs(locals())
        return await self._api_call_post('create', json=payload)
    
    async def tags(self):
        """returns available models"""
        return await self._api_call_get('tags')
    
    async def show(self,
                   name: str,
                   verbose: bool = False # True for full data
                   ):
        return await self._api_call_post('show', 
                                         json=dict(
                            name = name, verbose = verbose ))
    
    async def copy(self,
                   source: str,
                   destination: str):
        """Copy a model. Creates a model with another name from an existing model."""
        return (await self._api_call_post('copy', 
                                         json=dict(
                            source = source, destination = destination),
                            resp_json=False)) [0]
        
    async def delete(self, name: str):
        async with aiohttp.ClientSession() as session:
            resp = await session.delete(f'{self.api_url}/delete', json = dict(name = name))
            if resp.status == 200: return True
            else: return False, resp.status

    async def pull(self, name: str,
                   insecure: bool = False,
                   stream: bool = False):
        return await self._api_call_post('pull', json = dict(
            name = name,
            insecure = insecure,
            stream= stream
        ))
    async def push(self, name: str,
                   insecure: bool = False,
                   stream: bool = False):
        return await self._api_call_post('push', json = dict(
            name = name,
            insecure = insecure,
            stream= stream
        ))
    async def mbed(self, 
                   input: str | list[str],
                   model: str = None,
                   truncate: bool = None,
                   options: dict = None,
                   keep_alive = None):
        """Generate embeddings from a model"""
        payload = get_kwargs(locals())
        if model is None: payload['model'] = self.model
        return await self._api_call_post('mbed', json=payload)

    async def ps(self):
        """List models that are currently loaded into memory."""
        return await self._api_call_get('ps')

async def main():
    Lama = llama('https://hack.agicotech.ru/api')
    resp = await Lama.generate('What are main defferences between dogs?')
    print(resp)


if __name__ == "__main__":
    asyncio.run(main())