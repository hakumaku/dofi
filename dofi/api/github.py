import logging
import re
from pathlib import Path
from types import TracebackType
from typing import Mapping, NamedTuple, Type

from dofi.api.schemas import GithubReleaseInfo
from dofi.utils.network import ClientSessionProxy, HttpClient, HttpRequest
from dofi.utils.parse import parse_version

logger = logging.getLogger(__name__)


class Repository(NamedTuple):
    username: str
    repo_name: str


def _parse_version_in_url(url: str) -> str:
    return parse_version(url, match_pattern=r".*/(v?[.\d]*)/")


def select_download_url(info: GithubReleaseInfo, pattern: str) -> str:
    download_url: list[str] = [asset.browser_download_url for asset in info.assets]
    matched_urls: list[str] = list(filter(lambda url: re.search(pattern, url) is not None, download_url))

    if len(matched_urls) == 1:
        return matched_urls[0]
    elif len(matched_urls) == 0:
        messages: list[str] = [
            "matching url is not found",
            f"pattern: '{pattern}'",
            f"browser_download_urls: {download_url}",
        ]
    else:
        messages = [
            "multiple matching urls are found",
            f"pattern: '{pattern}'",
            f"browser_download_urls: {download_url}",
        ]

    raise RuntimeError("\n".join(messages))


class GithubAPI:
    def __init__(self, *, access_token: str | None = None):
        headers: Mapping[str, str] | None = None
        if access_token:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-GitHub-Api-Version": "2022-11-28",
            }

        self.base_url = "https://api.github.com"
        self._client = HttpClient(headers=headers)
        self._session: ClientSessionProxy | None = None

    async def __aenter__(self) -> "GithubAPI":
        self._session = await self._client.__aenter__()
        return self

    async def __aexit__(
        self, exc_type: Type[BaseException] | None, exc_val: BaseException | None, exc_tb: TracebackType | None
    ):
        self._session = None
        return await self._client.__aexit__(exc_type, exc_val, exc_tb)

    async def get_release_info(self, repositories: list[Repository]) -> list[GithubReleaseInfo]:
        requests: list[HttpRequest] = [
            {"url": f"{self.base_url}/repos/{repos.username}/{repos.repo_name}/releases/latest"}
            for repos in repositories
        ]
        responses = await self._session.get_many(requests)

        release_info: list[GithubReleaseInfo] = []
        for response in responses:
            info = GithubReleaseInfo.parse_raw(response.contents)
            release_info.append(info)

        return release_info

    async def download(self, targets: list[tuple[GithubReleaseInfo, str]], *, dest: Path | None = None):
        # TODO: compare local version with remote version
        download_urls = [select_download_url(info, pattern) for info, pattern in targets]
        dest = dest if dest is not None else Path.home() / "Downloads"
        requests: list[HttpRequest] = [{"url": url, "download": dest} for url in download_urls]
        return await self._session.get_many(requests)

        # shutil.unpack_archive(output, extract_dir=tempdir)

        # binary = [binary for binary in output.parent.glob(f"**/{self.bin}") if binary.is_file()]
        # assert len(binary) == 1
        # binary_path = Path(binary[0])
        # binary_path.chmod(stat.S_IXUSR)

        # dest_path = Path.home() / ".local" / "bin" / binary_path.name

        # shutil.move(binary_path, dest_path)
