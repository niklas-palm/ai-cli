## ai cli

Simple cli to summarise text with Bedrock. Contains some convenvience commands to read data online and from PDFs.
Also has audio transcription capabilities using [Whisper](https://github.com/openai/whisper). 

### Prerequisites

- Python >=3.8,<3.12
- [ffmpeg](#ffmpeg)
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

```bash
ai transcribe local_file.mp3 | ai summarise
```

## ffmpeg

#### on Ubuntu or Debian
`sudo apt update && sudo apt install ffmpeg`

#### on Arch Linux
`sudo pacman -S ffmpeg`

#### on MacOS using [Homebrew](https://brew.sh/)
`brew install ffmpeg`

#### on Windows using [Chocolatey](https://chocolatey.org/)
`choco install ffmpeg`

#### on Windows using [Scoop](https://scoop.sh/)
`scoop install ffmpeg`