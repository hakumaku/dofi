use std::path::PathBuf;

use clap::Parser;

use std::fs;

use super::get_current_dir;
use crate::read_config;

static CONFIG: &str = "dofi.yaml";

#[derive(Parser, Debug)]
pub struct UpdateCommand {
    /// Path to 'dofi.yaml'
    #[arg(short, long, default_value = get_current_dir().into_os_string())]
    pub path: PathBuf,
}

impl UpdateCommand {
    fn normalize_path(&self) -> PathBuf {
        let abspath = if self.path.is_relative() {
            let mut cwd = get_current_dir();
            cwd.push(&self.path);

            let mut buf = PathBuf::new();
            for path in cwd.iter() {
                if path != ".." {
                    buf.push(path);
                } else {
                    buf.pop();
                }
            }
            fs::canonicalize(buf)
        } else {
            fs::canonicalize(&self.path)
        };

        let mut path = match abspath {
            Ok(path) => path,
            Err(_) => {
                eprintln!("{:?} does not exit", self.path);
                std::process::exit(1);
            }
        };

        if !path.ends_with(CONFIG) {
            path.push(CONFIG);
        }

        path
    }

    pub fn update(&self) {
        let path = self.normalize_path();
        let config = read_config(path.to_str().expect("invalid UTF-8 path"));
        for (name, package) in config.into_iter() {
            println!("{}: {}", name, package);
        }
    }
}
