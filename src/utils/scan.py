import aiohttp


class ScanApi(aiohttp.ClientSession):
    _api_endpoint = None
    _api_key = None

    def __init__(self, api_endpoint, api_key, **kwargs):
        self._api_endpoint = api_endpoint
        self._api_key = api_key
        super().__init__(**kwargs)

    async def call(self, module, action, **params):
        params['module'] = module
        params['action'] = action
        params['apikey'] = self._api_key
        r = await self.get(self._api_endpoint, params=params)
        return await r.json()
