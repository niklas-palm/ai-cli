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
    help="Summary mode can be: detailed | concise",
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
    """Fetches the provided url or file and sends the text to stdout"""
    if is_local_filepath(input):
        text = fetch_pdf(input)
        click.echo(text)
        return

    if is_url(input):
        text = fetch_url(input)
        click.echo(text)
        return

    else:
        click.secho("The input you provided is not yet supported", fg="red")


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
    https://github.com/openai/whisper?tab=readme-ov-file#available-models-and-languages"""
    if not os.path.exists(filepath):
        click.echo("File not found")
        return

    if not (filepath.endswith('.wav') or filepath.endswith('.mp3')):
        click.echo("File must be a wav or mp3 audio file")
        return

    warnings.filterwarnings("ignore")
    model = whisper.load_model(whispermodel)
    result = model.transcribe(filepath)
    warnings.resetwarnings()

    transcription = result["text"]
    click.echo(transcription)
    return

