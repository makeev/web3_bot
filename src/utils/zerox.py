from urllib.parse import urlencode

import aiohttp


class ZeroXException(Exception):
    pass


class ZeroXProtocol(aiohttp.ClientSession):
    """
    https://docs.0x.org/0x-api-swap/api-references/
    """
    # @TODO пока нас интересует только это
    _endpoint = 'https://polygon.api.0x.org'
    _path = 'swap'
    _v = 'v1'

    def _url(self, method):
        return '{endpoint}/{path}/{version}/{method}'.format(
            endpoint=self._endpoint,
            path=self._path,
            version=self._v,
            method=method
        )

    async def _check_status(self, response):
        # Проверяем статус и бросаем исключения
        # @TODO
        if response.status != 200:
            text = await response.text()
            raise ZeroXException('status %d, response: %s' % (response.status, text))

    async def _request(self, *args, **kwargs):
        # можем что-то делать с дефолтными запросами
        r = await super()._request(*args, **kwargs)
        await self._check_status(r)
        return r

    async def quote(self, **kwargs):
        method = 'quote'
        print('%s?%s' % (self._url(method), urlencode(kwargs)))
        return await self.get(
            self._url(method),
            params=kwargs
        )

    async def price(self, **kwargs):
        method = 'price'
        return await self.get(
            self._url(method),
            params=kwargs
        )

    async def sources(self):
        method = 'sources'
        return await self.get(
            self._url(method),
        )
