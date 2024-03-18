use serde::{Deserialize, Serialize};
use std::{collections::HashMap, fmt::Display, fs::File};

#[derive(Debug, Serialize, Deserialize)]
struct GithubPackageVersion {
    command: Vec<String>,
    pattern: String,
    strip: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GithubPackage {
    repo: String,
    artifact: String,
    version: GithubPackageVersion,
}

type GithubPackages = HashMap<String, GithubPackage>;

impl Display for GithubPackage {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.repo)
    }
}

pub fn read_config(path: &str) -> GithubPackages {
    let result = serde_yaml::from_reader(
        File::open(path).unwrap_or_else(|_| panic!("cannot open '{}'", path)),
    );
    if let Err(e) = result {
        eprintln!("{}", e);
        std::process::exit(1);
    }

    result.unwrap()
}
