# PDF Tool — Merge & Split

[![CI](https://github.com/pavanbg7/pdf-tool/actions/workflows/ci.yml/badge.svg)](https://github.com/pavanbg7/pdf-tool/actions/workflows/ci.yml)

A command-line tool for merging multiple PDFs into one, or splitting a PDF into multiple files, built to fail gracefully instead of crashing with a raw traceback

## Features

- Merge any number of PDFs into a single file, in the order given
- Split a PDF two ways:
- Into equal chunks (e.g. every 3 pages)
- Into custom page ranges (e.g. `1-3,5,7-10`)
- Clear, human-readable error messages for every failure case — never a raw Python traceback
- Safe against interruption (Ctrl+C) — never leaves a corrupted/partial output file
- Sensible exit codes for use in scripts or CI pipelines
- Full `--help` on every command

## Installation

**1. Clone the repository**
```bash
git clone https://github.com/pavanbg7/pdf-tool.git
cd pdf-tool
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

## Usage

### Merge PDFs
```bash
python pdf_main.py merge file1.pdf file2.pdf file3.pdf -o merged.pdf
```

### Split a PDF — equal chunks
```bash
python pdf_main.py split input.pdf -o output_folder --every 3
```
Splits into groups of 3 pages each: `pages_1-3.pdf`, `pages_4-6.pdf`, etc.

### Split a PDF — custom ranges
```bash
python pdf_main.py split input.pdf -o output_folder --ranges "1-3,5,7-10"
```
Creates one file per range: `pages_1-3.pdf`, `pages_5-5.pdf`, `pages_7-10.pdf`

### Help
```bash
python pdf_main.py --help
python pdf_main.py merge --help
python pdf_main.py split --help
```
## Running with Docker

You can run this tool without installing Python or any dependencies locally, using Docker.

**Build the image:**
```bash
docker build -t pdf-tool .
```

**Run it** (mount a local folder so the container can read/write your files):
```bash
docker run -v "/path/to/your/files:/data" pdf-tool merge /data/file1.pdf /data/file2.pdf -o /data/merged.pdf
```

Replace `/path/to/your/files` with the folder on your machine containing your PDFs. All file paths in the command must use `/data/...` since that's the path *inside* the container.

**See help:**
```bash
docker run pdf-tool --help
```

## Error Handling

| Scenario | Behavior |
|---|---|
| Input file doesn't exist | Clear error message, exit code 2 |
| File isn't a valid PDF (wrong extension or corrupted) | Clear error message, exit code 3 |
| Output directory doesn't exist | Clear error message with a tip, exit code 2 |
| Invalid page range (non-numeric, reversed, out of bounds) | Clear error message, exit code 4 |
| `--every` given as 0 or negative | Clear error message, exit code 4 |
| Interrupted mid-run (Ctrl+C) | Clean message, no traceback, no partial output file, exit code 130 |
| Success | Exit code 0 |

## Project Structure

```
pdf-tool/
├── pdf_main.py       # All logic and CLI
├── requirements.txt
└── README.md
```

## Live Demo / Testing

Run through the examples above with your own PDF files to try it out. No server or deployment needed — this is a local CLI tool.
