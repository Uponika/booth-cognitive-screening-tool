import streamlit as st
import requests
import io
from PIL import Image, ImageDraw
import sounddevice as sd
import numpy as np
import tempfile
import os
from scipy.io.wavfile import write
from streamlit_drawable_canvas import st_canvas


st.set_page_config(page_title="Cognitive Assessment Tool", layout="centered")

st.title("🧠 Cognitive Assessment Tool")

# -------------------------------
# Task 1: Date & Time
# -------------------------------
st.header("Task 1: Date & Time")
year = st.text_input("Year")
season = st.text_input("Season")
month = st.text_input("Month")
day_of_week = st.text_input("Day of Week")
date = st.text_input("Date (DD)")
if st.button("Submit Task 1"):
    st.success(f"Submitted: {year}, {season}, {month}, {day_of_week}, {date}")


# -------------------------------
# Task 2: Location
# -------------------------------
st.header("Task 2: Location")
state = st.text_input("State/Province")
county = st.text_input("County/Division")
town_city = st.text_input("Town/City")
hospital = st.text_input("Hospital")
floor = st.text_input("Floor")
if st.button("Submit Task 2"):
    st.success(f"Submitted location: {state}, {county}, {town_city}, {hospital}, {floor}")


# -------------------------------
# Task 3: Backward Counting
# -------------------------------
st.header("Task 3: Backward Counting")
task3_answer = st.text_area("Count backward from 100 by 7s (stop after 5 answers)")
if st.button("Submit Task 3"):
    st.success(f"Your counting: {task3_answer}")


# -------------------------------
# Task 4: Object Naming
# -------------------------------
st.header("Task 4: Object Naming")

col1, col2 = st.columns(2)
with col1:
    st.image("images/wristwatch.jpeg", caption="Object 1")
    ans1 = st.text_input("What is this object? (Object 1)")
with col2:
    st.image("images/pencil.png", caption="Object 2")
    ans2 = st.text_input("What is this object? (Object 2)")

if st.button("Submit Task 4"):
    st.success(f"Answers submitted: {ans1}, {ans2}")


# -------------------------------
# Task 5: Object Recall (Voice)
# -------------------------------
st.header("Task 5: Object Recall (Voice)")

if st.button("Play Instruction for Task 5"):
    st.info("🔊 Please remember the following three objects: apple, pen, carpet")

duration = 5
fs = 44100
if st.button("🎙️ Record Recall (5s)"):
    st.info("Recording started... Speak now.")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    recording_int16 = np.int16(recording * 32767)
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write(tmpfile.name, fs, recording_int16)
    st.audio(tmpfile.name)
    st.success(f"Audio recorded: {tmpfile.name}")


# -------------------------------
# Task 6: Phrase Repetition (Voice)
# -------------------------------
st.header("Task 6: Phrase Repetition (Voice)")
if st.button("Play Instruction for Task 6"):
    st.info("🔊 Repeat the phrase: 'no ifs, ands, or buts'")

duration = 10
if st.button("🎙️ Record Phrase Repetition (10s)"):
    st.info("Recording started... Repeat phrase now.")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    tmpfile = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    write(tmpfile.name, fs, recording)
    st.audio(tmpfile.name)
    st.success(f"Audio recorded: {tmpfile.name}")


# -------------------------------
# Task 7: Sentence Construction
# -------------------------------
st.header("Task 7: Sentence Construction")
sentence = st.text_area("Make a sentence that contains a noun and a verb")
if st.button("Submit Task 7"):
    st.success(f"Your sentence: {sentence}")


# -------------------------------
# Task 8: Picture Copying
# -------------------------------
st.header("Task 8: Picture Copying")
st.image("images/task-image.jpg", caption="Please copy this picture")

canvas_width, canvas_height = 500, 400
canvas_result = st_canvas(

    fill_color="rgba(0, 0, 0, 0)",  # Transparent fill
    stroke_width=3,
    stroke_color="#000000",
    background_color="#FFFFFF",
    width=canvas_width,
    height=canvas_height,
    drawing_mode="freedraw",
    key="canvas",
)

if st.button("Save Drawing (Task 8)"):
    if canvas_result.image_data is not None:
        img = Image.fromarray((canvas_result.image_data).astype(np.uint8))
        save_path = "images/user_drawing.png"
        img.save(save_path)
        st.success(f"Drawing saved: {save_path}")
        st.image(save_path)

    else:
        st.error("No drawing submitted.")
