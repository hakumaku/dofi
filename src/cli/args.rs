use clap::{Parser, Subcommand};

use super::UpdateCommand;

#[derive(Subcommand, Debug)]
pub enum Command {
    Update(UpdateCommand),
}

#[derive(Parser, Debug)]
#[command(name = "MyApp")]
#[command(version = "1.0")]
#[command(about = "Does awesome things", long_about = None)]
#[command(propagate_version = true)]
#[command(subcommand_required = true)]
#[command(arg_required_else_help = true)]
pub struct Args {
    #[command(subcommand)]
    command: Command,
}

impl Args {
    pub fn run(&self) {
        match &self.command {
            Command::Update(command) => command.update(),
        }
    }
}
