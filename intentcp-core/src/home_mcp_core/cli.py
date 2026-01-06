import typer

app = typer.Typer(
    help="HomeMCP Core CLI",
    no_args_is_help=True,
)


@app.command()
def init() -> None:
    """
    Initialize HomeMCP Core server (configs, folders, etc.).
    """
    typer.echo("✅ intentcp-core init: initialization stub (implement real logic here).")


if __name__ == "__main__":
    app()