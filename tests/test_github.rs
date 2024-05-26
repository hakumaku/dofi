#[cfg(test)]
mod tests {
    use dofi::{get_configuration, GithubClient};

    #[tokio::test]
    async fn test_github_api() {
        let settings = get_configuration().expect("failed to load `config.yaml`");
        let client = GithubClient::new(settings.github_id, &settings.github_pat);
        let release_info = client
            .get_release_info("derailed/k9s")
            .await
            .expect("failed to retrieve release info");
    }
}
