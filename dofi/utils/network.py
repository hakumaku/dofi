import asyncio
import functools
import logging
from dataclasses import dataclass
from http.cookies import SimpleCookie
from pathlib import Path
from types import TracebackType
from typing import Any, Awaitable, Literal, Mapping, Protocol, Sequence, Type, TypeAlias, TypedDict

from aiohttp import ClientResponse, ClientSession, ClientTimeout
from typing_extensions import NotRequired
from yarl import URL

Method: TypeAlias = Literal["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"]

logger = logging.Logger(__name__)


class _RequestContextManager(Protocol):
    def __aenter__(self) -> Awaitable[ClientResponse]:
        """
        Typehint "aiohttp.request"
        """


class _RequestPartial(Protocol):
    def __call__(self) -> _RequestContextManager:
        """
        Typehint "functools.partial" of aiohttp request methods.
        """


class HttpRequest(TypedDict):
    url: str
    params: NotRequired[Mapping[str, str]]
    data: NotRequired[Any]
    json: NotRequired[Any]
    cookies: NotRequired[Mapping[str, str]]
    headers: NotRequired[Mapping[str, str]]
    download: NotRequired[Path]


@dataclass(slots=True, frozen=True)
class HttpResponse:
    url: URL
    status: int
    reason: object
    contents: bytes
    cookies: SimpleCookie[str]

    def __str__(self) -> str:
        return f"<Response [{self.status}]>"


class ClientSessionProxy:
    def __init__(self, session: ClientSession):
        self._session = session

    async def _request(self, fn: _RequestPartial, *, download: Path | None = None) -> HttpResponse | None:
        async with fn() as response:
            if download is None:
                return HttpResponse(
                    url=response.url,
                    status=response.status,
                    reason=response.reason,
                    cookies=response.cookies,
                    contents=await response.read(),
                )

            output = download / response.content_disposition.filename
            with open(output, "wb") as f:
                async for chunk in response.content.iter_chunked(2**20):
                    f.write(chunk)

            return HttpResponse(
                url=response.url,
                status=response.status,
                reason=response.reason,
                cookies=response.cookies,
                contents=b"",
            )

    async def get(
        self,
        url: str,
        *,
        params: Mapping[str, str] = None,
        cookies: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        download: Path | None = None,
    ):
        fn = functools.partial(
            self._session.get,
            url,
            params=params,
            cookies=cookies,
            headers=headers,
        )
        return await self._request(fn, download=download)

    async def get_many(self, requests: Sequence[HttpRequest]) -> list[HttpResponse]:
        tasks = [
            self._request(
                functools.partial(
                    self._session.get,
                    req["url"],
                    params=req.get("params", None),
                    cookies=req.get("cookies", None),
                    headers=req.get("headers", None),
                ),
                download=req.get("download", None),
            )
            for req in requests
        ]
        result = list(await asyncio.gather(*tasks))
        return result

    async def post(
        self,
        url: str,
        *,
        data: Any = None,
        json: Any = None,
        cookies: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
    ):
        fn = functools.partial(
            self._session.post,
            url,
            data=data,
            json=json,
            cookies=cookies,
            headers=headers,
        )
        return await self._request(fn)

    async def post_many(self, requests: Sequence[HttpRequest]) -> list[HttpResponse]:
        tasks = [
            self._request(
                functools.partial(
                    self._session.post,
                    req["url"],
                    data=req.get("data", None),
                    json=req.get("json", None),
                    cookies=req.get("cookies", None),
                    headers=req.get("headers", None),
                )
            )
            for req in requests
        ]
        result = list(await asyncio.gather(*tasks))
        return result


class HttpClient:
    def __init__(
        self, *, base_url: str | None = None, headers: Mapping[str, str] | None = None, timeout: int | None = None
    ):
        self.base_url = base_url
        self.timeout = ClientTimeout(total=timeout)
        self.headers = headers
        self._client_session: ClientSession | None = None

    async def __aenter__(self) -> "ClientSessionProxy":
        self._client_session = ClientSession(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self.headers,
        )
        return ClientSessionProxy(self._client_session)

    async def __aexit__(
        self, exc_type: Type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ):
        await self._client_session.close()
        self._client_session = None
