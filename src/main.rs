use dofi::read_config;

fn main() {
    let config = read_config("./dofi.yaml");
    for (name, package) in config.into_iter() {
        println!("{}: {}", name, package);
    }
}
