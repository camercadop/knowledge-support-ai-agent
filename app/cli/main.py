import typer

from app.cli.commands import support as support_commands
from app.config.logging import configure_logging

configure_logging()

app = typer.Typer(help="Knowledge Support AI Agent CLI.")
app.add_typer(support_commands.app)
