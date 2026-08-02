import typer

from app.cli.commands import analytics as analytics_commands
from app.cli.commands import support as support_commands

app = typer.Typer(help="Knowledge Support AI Agent CLI.", invoke_without_command=True)
app.add_typer(support_commands.app, name="support")
app.add_typer(analytics_commands.app, name="analytics")


@app.callback()
def main() -> None:
    from app.config.logging import configure_logging
    configure_logging(mode="cli")


if __name__ == "__main__":
    app()
