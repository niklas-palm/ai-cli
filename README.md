## ai cli

Simple cli to summarise text with Bedrock. Contains some convenvience commands to read data online and PDFs

### Prerequisites

- Access to Amazon Bedrock
- Valid AWS credentials in your environment

### Installation

1. Install cli

   ```bash
   pip install .
   ```

### Examples

## Web

```bash
ai fetch https://en.wikipedia.org/wiki/London_System | ai summarise
```

```bash
ai fetch https://en.wikipedia.org/wiki/London_System | ai summarise -m concise
```

```bash
ai fetch https://en.wikipedia.org/wiki/London_System | ai summarise -m joyful
```

## Local files

```bash
ai fetch local_file.pdf | ai summarise
```
