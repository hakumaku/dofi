use clap::Parser;

use dofi::Args;

fn main() {
    let args = Args::parse();

    args.run()
}
