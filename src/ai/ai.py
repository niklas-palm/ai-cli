import click

from ai.bedrock.bedrock import get_summary
from ai.utils.helpers import *


class Config(object):
    def __init__(self) -> None:
        self.verbose = False


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
@click.option("-v", "--verbose", is_flag=True)
@pass_config
def cli(config, verbose):
    config.verbose = verbose


@cli.command()
@click.option(
    "-m",
    "--mode",
    type=str,
    default="detailed",
    show_default=True,
    help="Summary mode can be any adjective: detailed | concise | joyful etc",
)
@pass_config
def summarise(config, mode):
    """Reads data from stdin and summarises it"""

    # Read data from stdin
    text_to_summarise = click.get_text_stream("stdin").read()

    # Get summary of input
    summary = get_summary(config, text_to_summarise, mode)

    click.secho("\nSUMMARY", bold=True, fg="magenta")
    click.secho(f"{summary}", fg="green")


@cli.command()
@click.argument(
    "input",
    type=str,
    required=True,
)
def fetch(input):
    """fetches the provided url or file and sends the text to stdout"""
    if is_local_filepath(input):
        text = get_local_file_text(input)
        click.echo(text)
        return

    if is_url(input):
        text = fetch_url(input)
        click.echo(text)
        return

    else:
        click.secho("The input you provided is not yet supported", fg="red")
