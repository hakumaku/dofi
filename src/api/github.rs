use crate::HttpClient;
use reqwest::{
    header::{HeaderMap, HeaderValue},
    Error,
};
use serde_json::Value;

#[derive(Debug)]
pub struct GithubAssetDownloadURL(String);

impl GithubAssetDownloadURL {
    pub fn parse(value: &Value) -> Result<GithubAssetDownloadURL, String> {
        if let Value::String(url) = value.get("browser_download_url").unwrap() {
            Ok(Self(url.to_string()))
        } else {
            Err(format!("{value}"))
        }
    }
}

pub struct GithubClient {
    client: HttpClient,
}

impl Default for GithubClient {
    fn default() -> Self {
        Self {
            client: HttpClient::new("http://api.github.com", HeaderMap::new()),
        }
    }
}

impl GithubClient {
    pub fn new(user_id: u32, github_pat: &String) -> Self {
        let value = format!("Bearer {}", github_pat);
        let mut headers = HeaderMap::new();
        headers.insert("User-Agent", user_id.into());
        headers.insert(
            "Authorization",
            HeaderValue::from_str(value.as_str()).unwrap(),
        );

        Self {
            client: HttpClient::new("http://api.github.com", headers),
        }
    }

    pub async fn get_release_info(&self, repo: &str) -> Result<Vec<GithubAssetDownloadURL>, Error> {
        // retrieve release info from API
        let url = format!("/repos/{}/releases/latest", repo);
        let response = self.client.get(&url).send().await?;
        let json = response.json::<serde_json::Value>().await?;

        // collect json["assets"]["browser_download_url"]
        let assets = json.get("assets").unwrap();
        let release_info: Vec<GithubAssetDownloadURL> = assets
            .as_array()
            .unwrap()
            .iter()
            .map(|asset| GithubAssetDownloadURL::parse(asset).unwrap())
            .collect();
        Ok(release_info)
    }
}
