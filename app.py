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


def add_to_history(task, language, user_input, ai_response, extracted_code=""):
    if "history" not in st.session_state:
        st.session_state.history = []

    st.session_state.history.insert(
        0,
        {
            "time": datetime.now().strftime("%d %b, %I:%M %p"),
            "task": task,
            "language": language,
            "input": user_input,
            "response": ai_response,
            "code": extracted_code,
        },
    )

    # Keep latest 10 outputs in sidebar history
    st.session_state.history = st.session_state.history[:10]



if "history" not in st.session_state:
    st.session_state.history = []

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

if "last_result" not in st.session_state:
    st.session_state.last_result = ""

if "last_code" not in st.session_state:
    st.session_state.last_code = ""

if "last_task" not in st.session_state:
    st.session_state.last_task = ""

if "last_language" not in st.session_state:
    st.session_state.last_language = ""

if "last_input" not in st.session_state:
    st.session_state.last_input = ""

if "last_time" not in st.session_state:
    st.session_state.last_time = ""


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
        for idx, item in enumerate(st.session_state.history):
            with st.expander(f"{item['task']} - {item['time']}"):
                st.caption(f"Language: {item['language']}")
                st.write("**Input preview:**")
                st.write(item["input"][:350])

                if st.button("Show this output", key=f"show_history_{idx}"):
                    st.session_state.last_result = item["response"]
                    st.session_state.last_code = item.get("code", "")
                    st.session_state.last_task = item["task"]
                    st.session_state.last_language = item["language"]
                    st.session_state.last_input = item["input"]
                    st.session_state.last_time = item["time"]
                    st.rerun()


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

    p, label {{
        color: {text} !important;
    }}

    .stMarkdown p,
    .stMarkdown li,
    .stMarkdown div {{
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

    div.stButton > button p,
    div.stButton > button span {{
        color: white !important;
    }}

    div.stDownloadButton > button p,
    div.stDownloadButton > button span {{
        color: {bg} !important;
    }}

    div[data-testid="stAlert"] {{
        border-radius: 16px;
        border: none;
    }}

    div[data-testid="stProgress"] > div > div > div {{
        background-color: {accent};
    }}

    /* Code blocks - fixed for both light and dark mode */
    pre {{
        background: #111111 !important;
        border-radius: 16px !important;
        padding: 18px !important;
        border: 1px solid #2b2b2b !important;
    }}

    code {{
        color: #f8f8f2 !important;
        background: transparent !important;
    }}

    div[data-testid="stCodeBlock"] {{
        background: #111111 !important;
        border-radius: 16px !important;
        border: 1px solid #2b2b2b !important;
    }}

    div[data-testid="stCodeBlock"] pre,
    div[data-testid="stCodeBlock"] code,
    div[data-testid="stCodeBlock"] span {{
        color: #f8f8f2 !important;
        background: transparent !important;
    }}

    div[data-testid="stCodeBlock"] button {{
        color: #ffffff !important;
        background: #2b2b2b !important;
        border-radius: 8px !important;
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

            extracted_code = extract_code_blocks(result)

            # Save latest output so it does not disappear after theme/language/sidebar changes
            st.session_state.last_result = result
            st.session_state.last_code = extracted_code
            st.session_state.last_task = task
            st.session_state.last_language = language
            st.session_state.last_input = user_input
            st.session_state.last_time = datetime.now().strftime("%d %b, %I:%M %p")

            add_to_history(task, language, user_input, result, extracted_code)

        except Exception as e:
            st.error("Something went wrong while getting AI response.")
            st.code(str(e))


# ---------------- SAVED OUTPUT SECTION ----------------
# This section is outside the button click block, so output stays visible
# even when user changes theme, language, sidebar, or uploads another file.
if st.session_state.last_result:
    st.markdown("## AI Response")
    st.caption(
        f"Showing saved output: {st.session_state.last_task} | "
        f"{st.session_state.last_language} | {st.session_state.last_time}"
    )
    st.markdown(st.session_state.last_result)

    st.markdown("---")

    if st.session_state.last_code:
        st.markdown("## Copy-ready Code")
        st.code(st.session_state.last_code, language="python")

        st.download_button(
            label="Download Code",
            data=st.session_state.last_code,
            file_name="codemate_solution.py",
            mime="text/x-python",
            key="download_saved_code"
        )
    else:
        st.info("No separate code block found in the AI response.")

    st.download_button(
        label="Download Full AI Response",
        data=st.session_state.last_result,
        file_name="codemate_response.txt",
        mime="text/plain",
        key="download_saved_response"
    )
