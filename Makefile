.PHONY: format lint build test coverage run

format:
	@cargo fmt

lint:
	@cargo clippy

build:
	@cargo build

test:
	@cargo test --lib --bins --tests -- --nocapture

coverage:
	@cargo tarpaulin --ignore-tests

run:
	@cargo run
