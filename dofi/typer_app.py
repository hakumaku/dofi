import typer


def init_typer_app() -> typer.Typer:
    from dofi.command import github, gitlab

    app = typer.Typer()
    app.add_typer(github.app)
    app.add_typer(gitlab.app)

    return app


typer_app = init_typer_app()
