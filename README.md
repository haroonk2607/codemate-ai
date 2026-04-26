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

