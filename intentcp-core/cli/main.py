import typer
from pathlib import Path

app = typer.Typer(help="HomeMCP Core CLI")

@app.command()
def init(
    config_path: Path = typer.Option(
        Path("config/settings.toml"),
        "--config",
        "-c",
        help="설정 파일 경로",
    )
):
    example = Path("config/settings.example.toml")
    if not example.exists():
        typer.echo("config/settings.example.toml 이 존재하지 않습니다.")
        raise typer.Exit(1)

    if config_path.exists():
        typer.echo(f"{config_path} 이미 존재합니다. 덮어쓰지 않습니다.")
        raise typer.Exit(1)

    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
    typer.echo(f"초기 설정 파일을 {config_path} 에 생성했습니다.")


if __name__ == "__main__":
    app()