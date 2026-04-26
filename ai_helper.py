from google import genai
import streamlit as st

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

client = genai.Client(api_key=GEMINI_API_KEY)

MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash"
]


def ask_gemini(prompt):
    last_error = None

    for model in MODELS:
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text

        except Exception as e:
            last_error = e
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                continue
            else:
                raise e

    return f"""
## Temporary Model Issue

Gemini models are currently busy.

Please try again after a few minutes.

Technical error:
{last_error}
"""


def explain_code(code, language="English"):
    prompt = f"""
You are CodeMate AI, a professional but beginner-friendly coding tutor.

The user wants an explanation of Python code.

Response language: {language}

Python code:
{code}

Write the response in this exact structure:

## What this code does
Explain the overall purpose clearly.

## Line-by-line explanation
Explain the important lines in simple words.

## Important concepts
Mention the programming concepts used.

## Improved version if needed
If the code can be improved, provide a cleaner version inside a Python markdown code block.
If no improvement is needed, say that the code is already fine.

## Beginner summary
Give a short and easy summary.

Rules:
- Keep the explanation beginner-friendly.
- Do not make the answer too long.
- If response language is Urdu, write in Urdu script.
- If response language is Roman Urdu, write in Roman Urdu.
- Any improved code must be inside triple backticks.
"""

    return ask_gemini(prompt)


def fix_error(error_text, language="English"):
    prompt = f"""
You are CodeMate AI, a professional Python debugging assistant.

The user has pasted Python code or an error message.

Response language: {language}

User input:
{error_text}

Write the response in this exact structure:

## Problem
Explain what is wrong.

## Why it happened
Explain the reason in simple words.

## Fixed code
Provide corrected Python code inside a Python markdown code block.

## Explanation of fix
Explain what you changed and why.

## Best practice tip
Give one useful tip to avoid this mistake in the future.

Rules:
- Keep the answer beginner-friendly.
- If response language is Urdu, write in Urdu script.
- If response language is Roman Urdu, write in Roman Urdu.
- Fixed code must be inside triple backticks.
"""

    return ask_gemini(prompt)