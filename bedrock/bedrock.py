import bedrock
import time
import json
import boto3
import botocore
import click
import nltk
import time

# What model of Amazon Bedrock to use
MODEL_ID = "amazon.titan-tg1-large"


bedrock = boto3.client(
    service_name="bedrock",
    region_name="us-west-2",
    endpoint_url="https://prod.us-west-2.frontend.bedrock.aws.dev",
)


def get_summary(
    config: object, text: str, mode: str = "detailed", max_chunk_size: int = 4000
) -> str:
    """Summarises the input using Amazon Bedrock.

    Parameters:
        config (object): Config object
        text (str): Text content to summarise.
        mode (str): Summary mode. detailed | concise
        max_chunk_size (int): Maximum chunk size to send for inference


    Returns:
        summary (str): Summary of the input text content.
    """

    if len(text.split()) < 30:
        raise Exception("Cant summarise something that short...")

    nltk.download("punkt")

    click.secho(f"Text is {len(text.split())} words", fg="magenta")

    start = time.perf_counter()

    # If text needs to be split, and then "map-reduce" the summaries
    if len(text.split()) > max_chunk_size:
        while len(text.split()) > max_chunk_size:
            text = split_and_summarise(config, text, max_chunk_size)

        click.secho(
            f"All chunks summarised, now creating summary of summaries...",
            fg="magenta",
        )

        prompt = f"""The following is a set of summaries:
        {text}
        Take these and combine it into a final, {mode} summary including all main themes. 
        {mode.upper()} SUMMARY:"""

        summary = send_request_with_retry(config.verbose, prompt)

    # Incoming data doesn't need splitting, and can be summarised straight away.
    else:
        click.secho(
            f"Creating summary...",
            fg="magenta",
        )

        prompt = f"""Including all main themes, write a {mode} summary of the following:
        {text}
        {mode.upper()} SUMMARY:"""

        summary = send_request_with_retry(config.verbose, prompt)

    time_spent = time.perf_counter() - start
    click.secho(f"Time spent summarising: {round(time_spent, 2)} seconds", fg="magenta")
    return summary.strip()


def split_and_summarise(config: object, text: str, chunk_size: int) -> str:
    """Splits input text into chunks, and summarises each chunk with bedrock

    Parameters:
        config (object): Config object
        text (str): Text content to split and summarise.
        chunk_size (str): Max size of chunks.

    Returns:
        all_summaries (str): All summaries, aggregated into one string
    """

    # Split text in chunks
    text_chunks = split_into_chunks(text, chunk_size, 5)
    summary = ""

    click.secho(f"Creating {len(text_chunks)} individual summaries.", fg="magenta")

    summaries = []
    with click.progressbar(text_chunks, label="Summarising each chunk") as chunks:
        for index, chunk in enumerate(chunks):
            prompt = f"""Write a concise summary of the following, including all main themes:
            "{chunk}"
            CONCISE SUMMARY:"""

            # Send chunk for summarisation
            summary = send_request_with_retry(config.verbose, prompt)
            if config.verbose:
                click.secho("\n=================")
                click.secho(f"CHUNK {index+1} summary:")
                click.secho(summary, fg="green")
                click.secho("=================")
            summaries.append(summary)

    all_summaries = " ".join(summaries)

    click.secho(
        f"All summaries are together {len(all_summaries.split())} words long",
        fg="magenta",
    )

    return all_summaries


def send_request_with_retry(verbose: bool, prompt: str, retries: int = 4) -> str:
    """Invokes Bedrock with the provided prompt, with custom retry mechanism with exponential
    back off to overcome the very harsch, default, throttling limits of bedrock.

    (Note that boto3 uses it's own retry and backodd mechanism as well, but with very short
    initial wait time)

    Parameters:
        verbose (bool): Logs more if True
        prompt (str): Prompt to send to bedrock.
        retries (int): Number of times to retry.

    Returns:
        response (str): Reponse from Bedrock.
    """

    if verbose:
        click.secho(f"\nCurrent prompt is {len(prompt.split())} words")

    prompt_config = {
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": 3000,
            "stopSequences": [],
            "temperature": 0.7,
            "topP": 0.2,
        },
    }
    body = json.dumps(prompt_config)
    initial_wait_time = 2
    for _ in range(retries):
        try:
            response = bedrock.invoke_model(
                body=body,
                modelId=MODEL_ID,
                accept="application/json",
                contentType="application/json",
            )
            response_body = json.loads(response.get("body").read())

            results = response_body.get("results")[0].get("outputText")
            return results
        except botocore.exceptions.ClientError as error:
            if error.response["Error"]["Code"] == "ThrottlingException":
                click.secho("\nExperiencing some throttling. Hold on...", fg="red")
            if (
                error.response["Error"]["Code"] == "ValidationException"
                and "Too many input tokens" in error.response["Error"]["Message"]
            ):
                click.secho(error, fg="red")
                click.secho(
                    "\nThis particular batch contained too many tokens. Sometime the number of token per word is > 3, but I don't know why or when.",
                    fg="cyan",
                )
                click.secho("Skipping this chunk of the summary to keep it simple.")
                return ""

            else:
                click.secho(error, fg="red")
                if verbose:
                    # THIS PATH SHOULD PROBABLY BE SOMETHING MORE CONISTENT
                    error_prompt_path = "error_prompt.txt"
                    with open(error_prompt_path, "wt") as f:
                        f.write(prompt)
                    click.secho(
                        f"You can find the prompt that created the error at {error_prompt_path}",
                        fg="red",
                        bold=True,
                    )

        # If it's a throttling error, wait for a while before retrying
        time.sleep(initial_wait_time)
        initial_wait_time *= 2  # Exponential backoff

    click.secho("Despite waiting, this time the throttling gods won...", fg="red")
    raise Exception("You're beeing throttled, dude.")


def split_into_chunks(text: str, chunk_size: int, num_sentence_overlap: int) -> list:
    """Splits the text input into chunks of full sentences consisting of
    slightly more than max_word_count words, with an overlap of num_sentence_overlap sentences.

    (Breaks if there are no sentences in input text)

    Parameters:
        text (str): Text to split into chunks.
        chunk_size (int): Number of words per chunk. (best effort)
        num_sentence_overlap (int): Number of sentences to overlap each chunk.

    Returns:
        chunks (list): list of strings.
    """

    if chunk_size < 40:
        raise Exception("chunk_size must be larger than 50")

    if num_sentence_overlap < 1:
        raise Exception("num_sentence_overlap must larger than 0")

    # Tokenize the input text into sentences.
    sentences = nltk.sent_tokenize(text)

    min_sentences = 5
    min_words = min_sentences * 20  # 20 is average number of words in a sentence
    if len(sentences) < min_sentences | len(text) < min_words:
        click.secho(
            "Too little text to do any splitting. Using the text as is.", fg="magenta"
        )
        return text

    # Initialize variables to keep track of the current chunk and chunks list.
    current_chunk = []
    chunks = []

    # Initialize variables to keep track of the current word count and maximum word count.
    current_word_count = 0

    i = 0
    while i < len(sentences) - 1:
        sentence = sentences[i]
        current_chunk.append(sentence)
        current_word_count += len(nltk.word_tokenize(sentence))

        if current_word_count >= chunk_size:
            chunks.append(" ".join(current_chunk))

            i -= num_sentence_overlap - 1
            current_word_count = 0
            current_chunk = []

            continue
        i += 1

    if len(current_chunk) > 0:
        chunks.append(" ".join(current_chunk))

    return chunks
