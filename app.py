import streamlit as st
import re
from datetime import datetime
from ai_helper import explain_code, fix_error

MAX_WORDS = 9000
WARNING_WORDS = 8000

st.set_page_config(
    page_title="CodeMate AI",
    page_icon="🤖",
    layout="wide"
)

# ---------------- HELPER FUNCTIONS ----------------
def count_words(text):
    return len(text.split())


def extract_code_blocks(text):
    code_blocks = re.findall(r"```(?:python)?\n(.*?)```", text, re.DOTALL)
    return "\n\n".join(code_blocks).strip()


def add_to_history(task, language, user_input, ai_response):
    if "history" not in st.session_state:
        st.session_state.history = []

    st.session_state.history.insert(
        0,
        {
            "time": datetime.now().strftime("%I:%M %p"),
            "task": task,
            "language": language,
            "input": user_input[:250],
            "response": ai_response[:500],
        },
    )

    st.session_state.history = st.session_state.history[:5]


if "history" not in st.session_state:
    st.session_state.history = []

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.toggle("Dark mode", key="dark_mode")

    st.markdown("---")
    st.markdown("## Controls")

    task = st.radio(
        "Choose a feature",
        ["Explain Code", "Fix Error"]
    )

    language = st.selectbox(
        "Response language",
        [
            "English",
            "Urdu",
            "Roman Urdu",
            "Hindi",
            "Arabic",
            "Spanish",
            "French",
            "German",
            "Turkish"
        ]
    )

    st.markdown("---")

    st.info(
        f"""
**Limit:** {MAX_WORDS} words  
**Warning after:** {WARNING_WORDS} words
"""
    )

    st.markdown("---")
    st.markdown("## History")

    if len(st.session_state.history) == 0:
        st.caption("No history yet.")
    else:
        for item in st.session_state.history:
            with st.expander(f"{item['task']} - {item['time']}"):
                st.caption(f"Language: {item['language']}")
                st.write("**Input:**")
                st.write(item["input"])
                st.write("**Response preview:**")
                st.write(item["response"])


# ---------------- THEME COLORS ----------------
theme = "Dark" if st.session_state.dark_mode else "Light"

if theme == "Light":
    bg = "#f6efe5"
    sidebar_bg = "#eee3d4"
    card_bg = "#fffaf2"
    text = "#2b2520"
    muted = "#6a5b4d"
    border = "#e0cdb8"
    accent = "#c7785c"
    accent_hover = "#b4684f"
    upload_btn = "#f3e7d9"
    input_bg = "#fffaf2"
else:
    bg = "#151312"
    sidebar_bg = "#1f1b18"
    card_bg = "#211d1a"
    text = "#f5eee7"
    muted = "#c8b8a8"
    border = "#3a3029"
    accent = "#d48768"
    accent_hover = "#c17458"
    upload_btn = "#2d2723"
    input_bg = "#211d1a"


# ---------------- CSS ----------------
st.markdown(
    f"""
<style>
    header[data-testid="stHeader"] {{
        background: {bg};
        height: 3rem;
    }}

    #MainMenu {{
        visibility: hidden;
    }}

    footer {{
        visibility: hidden;
    }}

    .stDeployButton {{
        display: none;
    }}

    .stApp {{
        background: {bg};
        color: {text};
    }}

    .block-container {{
    padding-top: 0rem;
    padding-bottom: 2rem;
    max-width: 1050px;
}}

    section[data-testid="stSidebar"] {{
        background: {sidebar_bg};
        border-right: 1px solid {border};
    }}

    section[data-testid="stSidebar"] > div:first-child {{
        padding-top: 1rem !important;
    }}

    section[data-testid="stSidebar"] * {{
        color: {text} !important;
    }}

    section[data-testid="stSidebar"] div[role="radiogroup"] label {{
        cursor: pointer !important;
    }}

    div[data-baseweb="select"] > div {{
        background-color: {card_bg} !important;
        border: 1px solid {border} !important;
        border-radius: 12px !important;
        color: {text} !important;
        cursor: pointer !important;
    }}

    div[data-baseweb="select"],
    div[data-baseweb="select"] *,
    div[data-baseweb="select"] svg {{
        cursor: pointer !important;
    }}

    div[data-baseweb="select"] span {{
        color: {text} !important;
    }}

    .hero-box {{
        background: {card_bg};
        padding: 28px 34px;
        border-radius: 24px;
        border: 1px solid {border};
        box-shadow: 0 12px 30px rgba(84, 57, 34, 0.07);
        margin-bottom: 28px;
    }}

    .hero-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
        margin-bottom: 10px;
    }}

    .hero-title {{
    font-size: 42px;
    font-weight: 800;
    color: {text};
    letter-spacing: -1px;
    margin: 0 0 8px 0;
    text-align: center;
}}

    .hero-subtitle {{
    font-size: 14px;
    color: {muted};
    line-height: 1.5;
    max-width: 760px;
    margin: 0 auto;
    text-align: center;
}}

    .theme-wrapper {{
        min-width: 145px;
    }}

    .input-title {{
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 16px;
        color: {text};
    }}

    h1, h2, h3, h4 {{
        color: {text} !important;
    }}

    p, label, span {{
        color: {text} !important;
    }}

    .stTextArea textarea {{
        background: {input_bg} !important;
        color: {text} !important;
        border: 1px solid {border} !important;
        border-radius: 18px !important;
        font-size: 15px !important;
        line-height: 1.55 !important;
    }}

    .stTextArea textarea:focus {{
        border-color: {accent} !important;
        box-shadow: 0 0 0 2px rgba(199, 120, 92, 0.20) !important;
    }}

    [data-testid="stFileUploader"] {{
        background: {card_bg} !important;
        border: 1px dashed {accent} !important;
        border-radius: 18px !important;
        padding: 12px !important;
        margin-bottom: 14px !important;
    }}

    [data-testid="stFileUploader"] section {{
        background: transparent !important;
        border: none !important;
    }}

    [data-testid="stFileUploader"] div {{
        color: {text} !important;
    }}

    [data-testid="stFileUploader"] button {{
        background: {upload_btn} !important;
        color: {text} !important;
        border: 1px solid {border} !important;
        border-radius: 999px !important;
        box-shadow: none !important;
        cursor: pointer !important;
    }}

    [data-testid="stFileUploader"] button:hover {{
        background: {border} !important;
        color: {text} !important;
    }}

    [data-testid="stFileUploaderFile"] {{
        background: {upload_btn} !important;
        border: 1px solid {border} !important;
        border-radius: 14px !important;
        color: {text} !important;
    }}

    div.stButton > button {{
        background: {accent};
        color: white !important;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 999px;
        font-weight: 700;
        transition: 0.18s ease;
        margin-top: 8px;
    }}

    div.stButton > button:hover {{
        background: {accent_hover};
        color: white !important;
        transform: translateY(-1px);
    }}

    div.stDownloadButton > button {{
        background: {text};
        color: {bg} !important;
        border: none;
        border-radius: 999px;
        font-weight: 700;
        padding: 0.7rem 1.35rem;
    }}

    div.stDownloadButton > button:hover {{
        background: {muted};
        color: {bg} !important;
    }}

    div[data-testid="stAlert"] {{
        border-radius: 16px;
        border: none;
    }}

    div[data-testid="stProgress"] > div > div > div {{
        background-color: {accent};
    }}

    pre {{
        background: #111111 !important;
        border-radius: 16px !important;
        padding: 18px !important;
    }}

    code {{
        color: #f8f8f2 !important;
    }}

    .streamlit-expanderHeader {{
        background: {card_bg} !important;
        border-radius: 14px !important;
        color: {text} !important;
    }}

    hr {{
        border-color: {border};
        margin-top: 1rem;
        margin-bottom: 1rem;
    }}
</style>
""",
    unsafe_allow_html=True
)


# ---------------- HERO SECTION ----------------
st.markdown(
    """
    <div class="hero-box">
        <div class="hero-title">CodeMate AI</div>
        <div class="hero-subtitle">
            Your calm coding assistant for understanding Python, fixing errors,
            uploading files, and turning confusing code into clear explanations.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------- INPUT SECTION ----------------
st.markdown('<div class="input-title">Input area</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload a Python/Text file optional",
    type=["py", "txt"]
)

file_text = ""

if uploaded_file is not None:
    try:
        file_text = uploaded_file.read().decode("utf-8")
        st.success(f"File uploaded: {uploaded_file.name}")
    except UnicodeDecodeError:
        st.error("Could not read this file. Please upload a valid .py or .txt file.")

default_text = file_text if file_text else ""

if task == "Explain Code":
    input_label = "Paste your Python code here:"
    button_label = "Explain Code"
    placeholder_text = "Example:\nfor i in range(5):\n    print(i)"
else:
    input_label = "Paste your code or error message here:"
    button_label = "Fix Error"
    placeholder_text = "Example:\nNameError: name 'y_pred_lr' is not defined"

st.markdown(f"**{input_label}**")

user_input = st.text_area(
    "Code input",
    value=default_text,
    height=120,
    placeholder=placeholder_text,
    label_visibility="collapsed"
)

word_count = count_words(user_input)

progress_value = min(word_count / MAX_WORDS, 1.0)
st.progress(progress_value)
st.caption(f"Words used: {word_count}/{MAX_WORDS}")

if WARNING_WORDS <= word_count < MAX_WORDS:
    st.warning("Your input is getting long. Try to keep it shorter to save API usage.")

if word_count >= MAX_WORDS:
    st.error("Your input is too long. Please reduce it below 9000 words.")

button_left, button_right = st.columns([4, 1])

with button_right:
    generate_clicked = st.button(button_label, use_container_width=True)


# ---------------- GENERATE RESPONSE ----------------
if generate_clicked:
    if user_input.strip() == "":
        st.warning("Please paste code/error or upload a file first.")

    elif word_count >= MAX_WORDS:
        st.error("Input is too long. Please reduce it before generating.")

    else:
        try:
            with st.spinner("CodeMate AI is thinking..."):
                if task == "Explain Code":
                    result = explain_code(user_input, language)
                else:
                    result = fix_error(user_input, language)

            add_to_history(task, language, user_input, result)

            st.markdown("## AI Response")
            st.markdown(result)

            st.markdown("---")

            extracted_code = extract_code_blocks(result)

            if extracted_code:
                st.markdown("## Copy-ready Code")
                st.code(extracted_code, language="python")

                st.download_button(
                    label="Download Code",
                    data=extracted_code,
                    file_name="codemate_solution.py",
                    mime="text/x-python"
                )
            else:
                st.info("No separate code block found in the AI response.")

            st.download_button(
                label="Download Full AI Response",
                data=result,
                file_name="codemate_response.txt",
                mime="text/plain"
            )

        except Exception as e:
            st.error("Something went wrong while getting AI response.")
            st.code(str(e))