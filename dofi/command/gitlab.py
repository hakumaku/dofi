import typer

app = typer.Typer(name="gitlab")


@app.command("update")
def install_or_update():
    pass
