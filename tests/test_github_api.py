import pytest

from dofi.api.github import GithubAPI, Repository
from dofi.settings.env import get_env_settings


@pytest.mark.asyncio
async def test_github_api():
    env = get_env_settings()
    async with GithubAPI(access_token=env.GITHUB_PAT) as api:
        info = await api.get_release_info(
            [
                Repository("jesseduffield", "lazygit"),
                Repository("jesseduffield", "lazydocker"),
            ]
        )
        result = await api.download(
            [
                (info[0], "lazygit_.*_Linux_x86_64.tar.gz"),
                (info[1], "lazydocker_.*_Linux_x86_64.tar.gz"),
            ]
        )

    print(result)


@pytest.mark.asyncio
async def test_github_api_download():
    async with GithubAPI() as api:
        info = await api.download(
            [
                Repository("jesseduffield", "lazygit"),
                Repository("jesseduffield", "lazydocker"),
            ]
        )

    print(info)
