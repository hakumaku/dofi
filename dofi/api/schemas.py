from datetime import datetime

from pydantic import BaseModel, Field


class GithubAuthor(BaseModel):
    login: str
    id: int
    node_id: str
    avatar_url: str
    gravatar_id: str
    url: str
    html_url: str
    followers_url: str
    following_url: str
    gists_url: str
    starred_url: str
    subscriptions_url: str
    organizations_url: str
    repos_url: str
    events_url: str
    received_events_url: str
    type: str
    site_admin: bool


class GithubAsset(BaseModel):
    url: str
    id: int
    node_id: str
    name: str
    label: str
    uploader: GithubAuthor
    content_type: str
    state: str
    size: int
    download_count: int
    created_at: datetime
    updated_at: datetime
    browser_download_url: str


class GithubReaction(BaseModel):
    url: str
    total_count: int
    plus_one: int = Field(alias="+1")
    minus_one: int = Field(alias="-1")
    laugh: int
    hooray: int
    confused: int
    heart: int
    rocket: int
    eyes: int

    class Config:
        allow_population_by_field_name = True


class GithubReleaseInfo(BaseModel):
    url: str
    assets_url: str
    upload_url: str
    html_url: str
    id: int
    author: GithubAuthor
    node_id: str
    tag_name: str
    target_commitish: str
    name: str
    draft: bool
    prerelease: bool
    created_at: datetime
    published_at: datetime
    published_at: datetime
    assets: list[GithubAsset]
    tarball_url: str
    zipball_url: str
    body: str
    reactions: GithubReaction
    mentions_count: int
