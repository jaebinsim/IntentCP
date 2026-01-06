import typer

app = typer.Typer(
    help="IntentCP Core CLI",
    no_args_is_help=True,
)


@app.command()
def init() -> None:
    """
    Initialize IntentCP Core server (configs, folders, etc.).
    """
    typer.echo("✅ intentcp-core init: initialization stub (implement real logic here).")


if __name__ == "__main__":
    app()