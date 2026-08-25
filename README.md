# CodeMate AI

CodeMate AI is an AI-powered coding assistant built with Streamlit and Google Gemini API.

# CodeMate AI

Live Demo: https://codemate-ai-bck9w7mgvsic3prybpr55n.streamlit.app/

## Features

- Explain Python code
- Fix Python errors
- Upload `.py` and `.txt` files
- Multiple response languages
- Light/Dark mode
- Word limit warning
- History panel
- Download AI response and code

## Tech Stack

- Python
- Streamlit
- Google Gemini API

## Setup

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `config.py` file:

```python
GEMINI_API_KEY = "paste_your_gemini_api_key_here"
```

Run the app:

```bash
streamlit run app.py
```

## Demo Screenshot

![CodeMate AI Demo](assets/codemate-demo.png)

## Note

Do not upload your real `config.py` file because it contains your private API key.

## QBankly sequence scraper

This repository includes a standalone scraper script for ordered question extraction by ID range.

### What it does
- Scrapes in strict sequence by `question_id`
- Supports range `30000` to `140000` (configurable)
- Processes in sets of `10000`
- Exports in chunks/folders of `20000`
- Preserves sequence with `sequence_index`
- Keeps repeated question IDs as separate ordered rows
- Handles `429` with `Retry-After` + backoff

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy and edit config:
```bash
cp /home/runner/work/codemate-ai/codemate-ai/qbankly_scraper_config.example.json /home/runner/work/codemate-ai/codemate-ai/qbankly_scraper_config.json
```

3. Run scraper:
```bash
python /home/runner/work/codemate-ai/codemate-ai/qbankly_sequence_scraper.py --config /home/runner/work/codemate-ai/codemate-ai/qbankly_scraper_config.json
```

### Output

Exports are created in:
`/home/runner/work/codemate-ai/codemate-ai/exports/qbankly`

Each 20k export gets its own folder:
- `export_001_<first_id>_<last_id>`
- `export_002_<first_id>_<last_id>`

Each folder contains:
- `questions.jsonl`
- `questions.csv`

Also generated:
- `checkpoint.json` (live resume/checkpoint data)
- `run_summary.json` (set-level run summary)
