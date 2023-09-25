## ai cli

Simple cli to summarise text with Bedrock. Contains some convenvience commands to feth and send data from URLs and PDFs to stdout

### Prerequisites

- Access to Amazon Bedrock
- The updated `boto3` and `botocore` .whl that contains the new Bedrock client

### Installation

1. Initialise venv and activate environment

```bash
python3 -m venv venv
source venv/bin/activate
```
1. Ensure you have PYTHONPATH set in your environment

`export PYTHONPATH="${PYTHONPATH}:${PWD}"`


1. Update `setup.py` script to reference your local `boto3` and `botocore` .whl

1. Install cli

```bash
pip install --editable .
```

The editable flag means we can edit the code without having to reinstall the CLI.

### Examples

```bash
ai fetch https://en.wikipedia.org/wiki/London_System | ai summarise
```

```bash
ai fetch benefit_agreements.pdf | ai summarise
```

### Throttling

At the time of writing, Bedrock has 3 RPM limit by default. If you're facing severe issues with that, use [this sim](https://sim.amazon.com/issues/V1042706657) to requeset a limit increase. Internal accounts can get up to 60 RPM at the time of writing.
