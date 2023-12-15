import warnings

import click
import whisper
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
def summarise(config, mode, input=""):
    """Reads data from stdin and summarises it"""

    if input:
        text_to_summarise = input

    else:
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
@click.option(
    "-s",
    "--silent",
    is_flag=True,
    help="Does not echo the text to summarise to stdout",
)
def fetch(input, silent):
    """fetches the provided url or file and sends the text to stdout"""
    if is_local_filepath(input):
        text = get_local_file_text(input)
        if not silent:
            click.echo(text)
        return text

    if is_url(input):
        text = fetch_url(input)
        if not silent:
            click.echo(text)
        return text

    else:
        click.secho("The input you provided is not yet supported", fg="red")


@cli.command()
@click.argument(
    "input",
    type=str,
    required=True,
)
@click.option(
    "-m",
    "--mode",
    type=str,
    default="detailed",
    show_default=True,
    help="Summary mode can be any adjective: detailed | concise | joyful etc",
)
@click.pass_context
def fs(ctx, input, mode):
    """Combines the fetch and summarise commands into one."""
    # Invoke fetch command
    text_to_summarise = ctx.invoke(fetch, input=input, silent=True)

    # Invoke summarise command
    ctx.invoke(summarise, input=text_to_summarise, mode=mode)


@cli.command()
@click.argument(
    "filepath",
    type=str,
    required=True,
)
@click.option(
    "-wm",
    "--whispermodel",
    type=str,
    default="tiny.en",
    show_default=True,
    help="Whisper model to use.",
)
def transcribe(filepath, whispermodel):
    """Parses the provided audio file (wav or mp3) and sends the text to stdout. Note: This is a
    slow process. Supported models can be found at:\n
    https://github.com/openai/whisper?tab=readme-ov-file#available-models-and-languages
    """
    if not os.path.exists(filepath):
        click.echo("File not found")
        return

    click.echo("Transcribing...")
    warnings.filterwarnings("ignore")
    model = whisper.load_model(whispermodel)
    result = model.transcribe(filepath)
    warnings.resetwarnings()

    transcription = result["text"]
    click.echo(transcription)
    return
