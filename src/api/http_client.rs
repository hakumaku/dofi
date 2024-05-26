use reqwest::{header::HeaderMap, RequestBuilder};

pub struct HttpClient {
    /// Reference:
    /// https://github.com/seanmonstar/reqwest/issues/988#issuecomment-1475364352
    /// https://github.com/tokio-rs/axum/blob/main/axum/src/test_helpers/test_client.rs
    base_url: String,
    headers: HeaderMap,
    client: reqwest::Client,
}

impl HttpClient {
    pub fn new(base_url: &str, headers: HeaderMap) -> Self {
        let client = reqwest::Client::builder().build().unwrap();
        Self {
            base_url: base_url.to_owned(),
            headers,
            client,
        }
    }

    #[allow(dead_code)]
    pub fn get(&self, url: &str) -> RequestBuilder {
        self.client
            .get(format!("{}{}", self.base_url, url))
            .headers(self.headers.clone())
    }

    #[allow(dead_code)]
    pub fn post(&self, url: &str) -> RequestBuilder {
        self.client
            .post(format!("{}{}", self.base_url, url))
            .headers(self.headers.clone())
    }
}
