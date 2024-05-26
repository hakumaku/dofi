use std::{env::current_dir, path::PathBuf};

use serde::Deserialize;

#[derive(Deserialize, Debug)]
pub struct Settings {
    pub github_id: u32,
    pub github_pat: String,
}

pub fn get_current_dir() -> PathBuf {
    current_dir().expect("permission denied")
}

pub fn get_configuration() -> Result<Settings, config::ConfigError> {
    let cwd = get_current_dir();
    let env_filename = "config.yaml";

    let settings = config::Config::builder()
        .add_source(config::File::from(cwd.join(env_filename)))
        .build()?;

    settings.try_deserialize::<Settings>()
}
