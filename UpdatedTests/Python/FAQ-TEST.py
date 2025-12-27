# streamlit_faq.py
import json
from pathlib import Path
import streamlit as st
from datetime import datetime

st.set_page_config(page_title="Functional Activities Questionnaire – Quizzard", page_icon="🧩", layout="centered")

QUESTIONS = [
    "Writing checks, paying bills, balancing checkbook",
    "Assembling tax records, business affairs, or papers",
    "Shopping alone for clothes, household necessities, or groceries",
    "Playing a game of skill, working on a hobby",
    "Heating water, making a cup of coffee, turning off stove after use",
    "Preparing a balanced meal",
    "Keeping track of current events",
    "Paying attention to, understanding, discussing TV, book, magazine",
    "Remembering appointments, family occasions, holidays, medications",
    "Traveling out of neighborhood, driving, arranging to take buses",
]

OPTIONS = [
    {"key": "dependent",        "label": "Dependent",                                          "score": 3},
    {"key": "assist",           "label": "Requires assistance",                                "score": 2},
    {"key": "diff-self",        "label": "Has difficulty but does by self",                    "score": 1},
    {"key": "normal",           "label": "Normal (Has no difficulty to do it by self)",        "score": 0},
    {"key": "never-could-now",  "label": "Never did [the activity] but could do now",          "score": 0},
    {"key": "never-diff",       "label": "Never did and would have difficulty now",            "score": 1},
]

MAX_SCORE = len(QUESTIONS) * 3
PROGRESS_FILE = Path("faq_progress.json")
ROOT_SAVE_PATH = Path("FAQ_Report.txt")  # <-- root folder save target

def init_state():
    if "idx" not in st.session_state:
        st.session_state.idx = 0
    if "answers" not in st.session_state:
        st.session_state.answers = [None] * len(QUESTIONS)
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "last_report_txt" not in st.session_state:
        st.session_state.last_report_txt = ""

def compute_score(answers):
    total = 0
    detail = []
    for i, key in enumerate(answers):
        opt = next((o for o in OPTIONS if o["key"] == key), None)
        score = opt["score"] if opt else 0
        total += score
        detail.append({"q": QUESTIONS[i], "label": opt["label"] if opt else "—", "score": score})
    return total, detail

def report_text(answers):
    total, detail = compute_score(answers)
    lines = []
    lines.append("Functional Activities Questionnaire (FAQ)")
    lines.append("-------------------------------------------")
    for i, row in enumerate(detail, 1):
        lines.append(f"{i}. {row['q']}")
        lines.append(f"   Answer: {row['label']}")
        lines.append(f"   Score: {row['score']}")
    lines.append("")
    lines.append(f"Total Score: {total} / {MAX_SCORE}")
    # optional timestamp footer
    lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return "\n".join(lines)

def save_progress():
    data = {"idx": st.session_state.idx, "answers": st.session_state.answers}
    PROGRESS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

def load_progress():
    if PROGRESS_FILE.exists():
        data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        st.session_state.idx = int(data.get("idx", 0))
        arr = data.get("answers", [])
        if isinstance(arr, list) and len(arr) == len(QUESTIONS):
            st.session_state.answers = arr

# --- UI ---
init_state()

st.markdown("## 🧩 Functional Activities Questionnaire")
st.caption("One question per step • Select one answer")

with st.container(border=True):
    cols = st.columns([1, 3])
    with cols[0]:
        st.markdown(f"**Question {st.session_state.idx+1} of {len(QUESTIONS)}**")
        st.progress((st.session_state.idx)/len(QUESTIONS))
    with cols[1]:
        st.markdown(f"### {QUESTIONS[st.session_state.idx]}")

    # radio group
    label_to_key = {o["label"]: o["key"] for o in OPTIONS}
    key_to_label = {o["key"]: o["label"] for o in OPTIONS}
    current_key = st.session_state.answers[st.session_state.idx]
    current_label = key_to_label[current_key] if current_key else None

    choice = st.radio(
        "Select one:",
        options=[o["label"] for o in OPTIONS],
        index=[o["label"] for o in OPTIONS].index(current_label) if current_label else None,
        key=f"radio_{st.session_state.idx}",
        label_visibility="collapsed",
    )
    st.session_state.answers[st.session_state.idx] = label_to_key[choice] if choice else None

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("◀ Previous", disabled=st.session_state.idx == 0):
            st.session_state.idx -= 1
            st.rerun()
    with c2:
        if st.button("💾 Save Progress"):
            save_progress()
            st.success("Progress saved to faq_progress.json", icon="✅")
    with c3:
        if st.button("⟳ Load Progress", disabled=not PROGRESS_FILE.exists()):
            load_progress()
            st.info("Progress loaded.", icon="ℹ️")
            st.rerun()
    with c4:
        is_last = st.session_state.idx == len(QUESTIONS) - 1
        if st.button("Submit ▶" if is_last else "Next ▶", disabled=st.session_state.answers[st.session_state.idx] is None):
            if is_last:
                st.session_state.submitted = True
                # --- Build report + save to root folder right now ---
                txt = report_text(st.session_state.answers)
                st.session_state.last_report_txt = txt
                ROOT_SAVE_PATH.write_text(txt, encoding="utf-8")
            else:
                st.session_state.idx += 1
            st.rerun()

# Report
if st.session_state.submitted:
    st.divider()
    st.markdown("### ✅ FAQ Summary")
    total, _ = compute_score(st.session_state.answers)
    st.markdown(f"**Total Score:** {total} / {MAX_SCORE}  \n*(Higher scores indicate greater functional difficulty.)*")

    # Show where it was saved in root
    st.success(f"Report saved to root as **{ROOT_SAVE_PATH.name}**", icon="💾")
    st.caption(f"Full path: `{ROOT_SAVE_PATH.resolve()}`")

    # Download button (browser download)
    st.download_button(
        "⬇ Download TXT Report",
        data=st.session_state.last_report_txt or report_text(st.session_state.answers),
        file_name="FAQ_Report.txt",
        mime="text/plain"
    )
