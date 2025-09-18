# voice_assessment_sd.py
import streamlit as st
import sounddevice as sd
import numpy as np
import wave, io, os, time, queue, threading
from datetime import datetime

# ---------- Config ----------
st.set_page_config(page_title="Speech Assessment Recorder", page_icon="🗣️", layout="centered")
SAMPLE_RATE = 16000        # 16 kHz mono
MAX_SECONDS = 120          # 2 minutes default
OUTPUT_DIR = "recordings"  # local folder to also save a copy (optional)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------- Question Bank ----------
QUESTION_BANK = {
    "story": {
        "label": "Spontaneous Storytelling",
        "hint":  "Patient narrates a personal memory or event.",
        "items": [
            "Tell me about a memorable trip you took. What made it special?",
            "Describe a time you felt proud of yourself and why.",
            "Share a childhood memory that really stands out."
        ],
    },
    "procedure": {
        "label": "Procedural Description",
        "hint":  "Explain a familiar process.",
        "items": [
            "Explain how to make a cup of tea, step by step.",
            "Describe the steps to change a flat tire safely.",
            "Explain how to send an email from your phone or computer."
        ],
    },
    "descriptive": {
        "label": "Descriptive Task",
        "hint":  "Describe an object, scene, or environment.",
        "items": [
            "Describe what you see outside a window on a rainy day.",
            "Describe your kitchen as if to someone who cannot see it.",
            "Describe a park or garden you like: sounds, colors, and people."
        ],
    },
}

# ---------- Session State ----------
def init_state():
    st.session_state.setdefault("assessment_key", "story")
    st.session_state.setdefault("question", QUESTION_BANK["story"]["items"][0])
    st.session_state.setdefault("recording", False)
    st.session_state.setdefault("start_ts", None)
    st.session_state.setdefault("stop_by_timer", False)
    st.session_state.setdefault("wav_bytes", None)
    st.session_state.setdefault("local_file", None)
    st.session_state.setdefault("rec_thread", None)
    st.session_state.setdefault("stop_event", None)
    st.session_state.setdefault("frames_bytes", [])  # list of raw int16 bytes
init_state()

def reset_audio_buffers():
    st.session_state.frames_bytes = []
    st.session_state.wav_bytes = None
    st.session_state.local_file = None
    st.session_state.stop_by_timer = False

# ---------- WAV helpers ----------
def build_wav_from_bytes(frames_bytes: list[bytes], samplerate: int) -> bytes:
    """Combine raw int16 mono chunks into a WAV in-memory bytes."""
    if not frames_bytes:
        return None
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # int16
        wf.setframerate(samplerate)
        for chunk in frames_bytes:
            wf.writeframes(chunk)
    return buf.getvalue()

def save_wav_file(frames_bytes: list[bytes], samplerate: int, file_path: str):
    with wave.open(file_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        for chunk in frames_bytes:
            wf.writeframes(chunk)

# ---------- Background Recorder (sounddevice) ----------
def start_recording_thread(samplerate: int, max_seconds: int):
    q = queue.Queue()
    stop_event = threading.Event()
    st.session_state.stop_event = stop_event

    def audio_callback(indata, frames, time_info, status):
        # indata dtype=int16, mono channel expected
        if status:
            # You can log statuses if needed: st.write(status)
            pass
        q.put(bytes(indata))  # raw bytes (int16)

    def runner():
        start_time = time.time()
        try:
            with sd.RawInputStream(samplerate=samplerate, channels=1, dtype='int16', callback=audio_callback):
                while not stop_event.is_set():
                    # Pull audio chunks as they arrive
                    try:
                        chunk = q.get(timeout=0.1)
                        st.session_state.frames_bytes.append(chunk)
                    except queue.Empty:
                        pass
                    # Auto-stop at max_seconds
                    if time.time() - start_time >= max_seconds:
                        st.session_state.stop_by_timer = True
                        break
        except Exception as e:
            # Expose any microphone/driver errors in the UI
            st.session_state.recording = False
            st.session_state.wav_bytes = None
            st.session_state.local_file = None
            st.session_state["rec_error"] = str(e)
            return

        # Build WAV in memory
        wav_bytes = build_wav_from_bytes(st.session_state.frames_bytes, samplerate)
        st.session_state.wav_bytes = wav_bytes

        # Also save a copy locally (optional)
        if wav_bytes:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            base = QUESTION_BANK[st.session_state.assessment_key]['label'].replace(" ", "_")
            fname = f"{base}_{ts}.wav"
            fpath = os.path.join(OUTPUT_DIR, fname)
            save_wav_file(st.session_state.frames_bytes, samplerate, fpath)
            st.session_state.local_file = fpath

        st.session_state.recording = False  # mark finished

    t = threading.Thread(target=runner, daemon=True)
    t.start()
    st.session_state.rec_thread = t

# ---------- UI ----------
st.title("🗣️ Speech Assessment Recorder (SoundDevice)")

# Assessment selector
left, right = st.columns([2, 3])
with left:
    assessment_key = st.selectbox(
        "Assessment style",
        options=list(QUESTION_BANK.keys()),
        format_func=lambda k: QUESTION_BANK[k]["label"],
        index=list(QUESTION_BANK.keys()).index(st.session_state.assessment_key),
    )
with right:
    st.markdown(f"**What to do:** {QUESTION_BANK[assessment_key]['hint']}")

if assessment_key != st.session_state.assessment_key:
    st.session_state.assessment_key = assessment_key
    st.session_state.question = QUESTION_BANK[assessment_key]["items"][0]
    reset_audio_buffers()

# Question selector
question = st.radio(
    "Pick one question to answer:",
    options=QUESTION_BANK[assessment_key]["items"],
    index=QUESTION_BANK[assessment_key]["items"].index(st.session_state.question),
)
if question != st.session_state.question:
    st.session_state.question = question
    reset_audio_buffers()

st.markdown(
    "> **Instructions:** Click **Start** to begin recording. You can **Stop** anytime. "
    f"If you don’t stop, recording will end automatically after **{MAX_SECONDS//60} minute(s)**."
)

# Controls
c1, c2, c3 = st.columns([1, 1, 3])
with c1:
    start_clicked = st.button("▶️ Start", type="primary", disabled=st.session_state.recording)
with c2:
    stop_clicked  = st.button("⏹️ Stop", disabled=not st.session_state.recording)

# Start
if start_clicked:
    reset_audio_buffers()
    st.session_state.recording = True
    st.session_state.start_ts = time.time()
    # Launch background recording thread
    start_recording_thread(SAMPLE_RATE, MAX_SECONDS)

# Stop
if stop_clicked and st.session_state.recording:
    # Signal thread to stop
    if st.session_state.stop_event:
        st.session_state.stop_event.set()

# Timer (client-side countdown) + status
timer_box = st.empty()
status_box = st.empty()

if st.session_state.recording:
    # Show a live countdown using JS on the client; server will still hard-stop at MAX_SECONDS
    remaining = MAX_SECONDS - int(time.time() - (st.session_state.start_ts or time.time()))
    remaining = max(0, remaining)
    mm, ss = divmod(remaining, 60)
    timer_box.info(f"⏱️ Recording… Time left: **{mm:02d}:{ss:02d}**")
    status_box.write("🎙️ Speak now… (microphone in use)")
else:
    # Finished or idle
    if st.session_state.wav_bytes:
        finished_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status_box.success(
            f"✅ Finished at {finished_str} "
            + ("(auto-stopped at 2:00)" if st.session_state.stop_by_timer else "(stopped)")
        )
    elif "rec_error" in st.session_state:
        status_box.error(f"⚠️ Recording error: {st.session_state['rec_error']}")
    else:
        status_box.info("Ready to record.")

# Download section
if st.session_state.wav_bytes:
    file_base = f"{QUESTION_BANK[assessment_key]['label'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
    st.subheader("🎧 Your recording is ready")
    st.write(f"**Assessment:** {QUESTION_BANK[assessment_key]['label']}  \n**Question:** {st.session_state.question}")

    st.download_button(
        label="⬇️ Download Recording (WAV)",
        data=st.session_state.wav_bytes,
        file_name=file_base,
        mime="audio/wav",
    )

    if st.session_state.local_file:
        st.caption(f"Also saved locally: `{st.session_state.local_file}`")

# Troubleshooting
with st.expander("Troubleshooting"):
    st.markdown("""
- First time, your OS may ask for microphone permission. Allow it.
- This app records **on the machine where Streamlit is running** (local desktop laptop).
- If you get errors like *Invalid sample rate* or *No default input device*, open your system **Sound** settings and choose a working mic.
- On Windows, if you see *Error querying device* or *WASAPI* issues, select the correct default input device and try again.
""")
