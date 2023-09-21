## ai cli

Simple cli to summarise websites and PDFs with Amazon Bedrock.

### Prerequisites

- Access to Amazon Bedrock
- The updated `boto3` and `botocore` .whl that contains the new Bedrock client

### Installation

1. Initialise venv and activate environment

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Update `setup.py` script to reference your local `boto3` and `botocore` .whl

3. Install cli

```bash
pip install --editable .
```

The editable flag means we can edit the code without having to reinstall the CLI.

4. Test it out.

```bash
ai fetch https://en.wikipedia.org/wiki/London_System | ai summarise
```

```bash
ai fetch benefit_agreements.pdf | ai summarise
```
