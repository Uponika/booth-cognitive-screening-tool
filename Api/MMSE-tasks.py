import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import cv2
import numpy as np
import pyttsx3
import sounddevice as sd
import tempfile
from scipy.io.wavfile import write
import openai
import spacy
from datetime import datetime
import pytz
import os
import tkinter as tk
from PIL import Image, ImageGrab

# -------------------------------
# Helper Functions
# -------------------------------
openai.api_key = os.getenv("OPENAI_API_KEY")
# -------------------------------
# Task 4: Show Images
# -------------------------------
def task4_object_naming():
    answers = {}

    # Show wristwatch
    watch_img = mpimg.imread(os.path.join("images", "wristwatch.jpeg"))
    plt.imshow(watch_img)
    plt.axis("off")
    plt.title("Object 1")
    plt.show()
    ans1 = input("What is this object? ")
    answers["object1"] = ans1.strip().lower()

    # Show pencil
    pencil_img = mpimg.imread(os.path.join("images", "pencil.png"))
    plt.imshow(pencil_img)
    plt.axis("off")
    plt.title("Object 2")
    plt.show()
    ans2 = input("What is this object? ")
    answers["object2"] = ans2.strip().lower()

    return answers
# -------------------------------
# Task 5: Object Recall (Voice)
# -------------------------------
def task5_object_recall():
    objects = ["apple", "pen", "carpet"]

    engine = pyttsx3.init()
    # Reduce speaking rate to match Task 6
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 75)

    engine.say(f"Please remember the following three objects: {objects[0]}, {objects[1]}, {objects[2]}")
    engine.runAndWait()

    duration = 5
    fs = 44100
    print(f"Start speaking now. You have {duration} seconds...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()

    # Convert float32 to int16 for Whisper
    recording_int16 = np.int16(recording * 32767)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        write(tmpfile.name, fs, recording_int16)
        audio_path = tmpfile.name

    print(f"Audio recorded and saved to {audio_path}")

    with open(audio_path, "rb") as f:
        transcription = openai.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )

    user_text = transcription.text.lower()
    print("Transcribed text:", user_text)

    # Fuzzy matching for scoring
    import difflib
    score = 0
    for obj in objects:
        match = difflib.get_close_matches(obj, user_text.split(), n=1, cutoff=0.8)
        if match:
            score += 1

    print(f"Task 5 Score: {score} / {len(objects)}")
    return {"score": score, "total": len(objects), "user_text": user_text}

# -------------------------------
# Task 6: Phrase Repetition (Voice)
# -------------------------------
def task6_phrase_repetition():
    phrase = "no ifs, ands, or buts"

    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 75)

    engine.say(f"Repeat the phrase: {phrase}")
    engine.runAndWait()

    duration = 10
    fs = 44100
    print(f"Please repeat the phrase now. You have {duration} seconds...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        write(tmpfile.name, fs, recording)
        audio_path = tmpfile.name

    print(f"Audio recorded and saved to {audio_path}")

    with open(audio_path, "rb") as f:
        transcription = openai.audio.transcriptions.create(
            model="whisper-1",
            file=f
        )

    user_text = transcription.text.lower()
    print("Transcribed text:", user_text)

    score = 1 if phrase in user_text else 0
    print(f"Task 6 Score: {score} / 1")

    return {"score": score, "total": 1, "user_text": user_text}

# Load English model
nlp = spacy.load("en_core_web_sm")

# -------------------------------
# Task 7: Sentence Construction
# -------------------------------
def task7_sentence_construction():
    sentence = input("Task 7: Make up and write a sentence (must contain a noun and a verb):\nYour sentence: ")

    doc = nlp(sentence)
    has_noun = any(token.pos_ == "NOUN" for token in doc)
    has_verb = any(token.pos_ == "VERB" for token in doc)

    score = 1 if has_noun and has_verb else 0
    print(f"Task 7 Score: {score} / 1")

    return {"score": score, "total": 1, "sentence": sentence, "has_noun": has_noun, "has_verb": has_verb}

# -------------------------------
# Task 8: Picture Copying (Tkinter Drawing Panel)
# -------------------------------
def open_drawing_panel(save_path="user_drawing.jpg"):
    root = tk.Tk()
    root.title("Task 8: Drawing Panel - Copy the Picture")

    canvas = tk.Canvas(root, width=500, height=400, bg="white")
    canvas.pack()

    last_x, last_y = None, None

    def draw(event):
        nonlocal last_x, last_y
        if last_x and last_y:
            canvas.create_line(last_x, last_y, event.x, event.y, fill="black", width=3)
        last_x, last_y = event.x, event.y

    def reset(event):
        nonlocal last_x, last_y
        last_x, last_y = None, None

    def save():
        # Save canvas drawing as image
        x = root.winfo_rootx() + canvas.winfo_x()
        y = root.winfo_rooty() + canvas.winfo_y()
        x1 = x + canvas.winfo_width()
        y1 = y + canvas.winfo_height()
        ImageGrab.grab().crop((x, y, x1, y1)).save(save_path)
        print(f"Drawing saved to {save_path}")
        root.destroy()

    canvas.bind("<B1-Motion>", draw)
    canvas.bind("<ButtonRelease-1>", reset)

    save_button = tk.Button(root, text="Save Drawing", command=save)
    save_button.pack()

    root.mainloop()

def task8_picture_copying():
    # Show reference image
    ref_img = mpimg.imread("images/task-image.jpg")
    plt.imshow(ref_img)
    plt.axis("off")
    plt.title("Please copy this picture below")
    plt.show()

    print("A drawing panel will open. Please copy the picture and click 'Save Drawing'.")
    open_drawing_panel("images/user_drawing.jpg")

    user_img_path = "images/user_drawing.jpg"
    if not os.path.exists(user_img_path):
        print("No drawing found. Scoring skipped.")
        return {"score": 0, "total": 1, "reason": "No drawing submitted."}

    user_img = cv2.imread(user_img_path, cv2.IMREAD_GRAYSCALE)

    # Edge detection
    edges = cv2.Canny(user_img, 50, 150, apertureSize=3)

    # Detect lines
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=80, minLineLength=50, maxLineGap=10)

    angle_count = 0
    intersections = 0

    if lines is not None:
        for i in range(len(lines)):
            for j in range(i+1, len(lines)):
                x1, y1, x2, y2 = lines[i][0]
                x3, y3, x4, y4 = lines[j][0]

                # Calculate angle
                v1 = np.array([x2-x1, y2-y1])
                v2 = np.array([x4-x3, y4-y3])
                dot = np.dot(v1, v2)
                norm = np.linalg.norm(v1) * np.linalg.norm(v2)
                if norm == 0:
                    continue
                angle = np.arccos(dot / norm) * 180 / np.pi

                if 10 < angle < 170:
                    angle_count += 1

                # Intersection check
                def ccw(A, B, C):
                    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])
                A, B = (x1, y1), (x2, y2)
                C, D = (x3, y3), (x4, y4)
                if ccw(A, C, D) != ccw(B, C, D) and ccw(A, B, C) != ccw(A, B, D):
                    intersections += 1

    score = 1 if angle_count >= 10 and intersections >= 1 else 0
    print(f"Task 8 Score: {score} / 1 (Angles: {angle_count}, Intersections: {intersections})")

    return {"score": score, "total": 1, "angles": angle_count, "intersections": intersections}

# -------------------------------
# GPT-based Scoring for Tasks 1–4
# -------------------------------
def score_with_gpt(task_name, user_response, reference_answers):
    if task_name == "Task 3: Backward Counting":
        reference_text = ', '.join(reference_answers["counting"])
    else:
        reference_text = reference_answers

    prompt = f"""
You are a scoring assistant.
Compare the user's full answer with the reference answers.
Give 1 point for each correct part, 0 for incorrect.
Return the score in JSON as: {{'score': X, 'total': Y}}.

Reference answers:
{reference_text}

User answer:
{user_response}
"""
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful scoring assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return response.choices[0].message.content

# -------------------------------
# Main Script
# -------------------------------
toronto_tz = pytz.timezone("America/Toronto")
now_toronto = datetime.now(toronto_tz)

tasks = {
    "Task 1: Date & Time": {
        "question": "What is the year, season, date, day of the week, and month?",
        "answers": {
            "year": "2025",
            "season": "fall",
            "month": "September",
            "day_of_week": now_toronto.strftime("%A"),
            "date": now_toronto.strftime("%d")
        }
    },
    "Task 2: Location": {
        "question": "Where are we now: State, County, Town/City, Hospital, Floor?",
        "answers": {
            "state": "Ontario",
            "county": "Toronto Division",
            "town_city": "Toronto",
            "hospital": "St. Michael's Hospital",
            "floor": "3"
        }
    },
    "Task 3: Backward Counting": {
        "question": "I would like you to count backward from 100 by sevens. Stop after five answers.",
        "answers": {
            "counting": ["93", "86", "79", "72", "65"]
        }
    },
    "Task 4: Object Naming": {
        "question": "Please name the objects shown in the images.",
        "answers": {
            "object1": "wristwatch",
            "object2": "pencil"
        }
    }
}

# Collect responses for Tasks 1–4
user_responses = {}
for task_name, task_data in tasks.items():
    print(f"\n{task_name}")

    if task_name == "Task 4: Object Naming":
        user_responses[task_name] = task4_object_naming()
        continue
    else:
        response = input(f"{task_data['question']}\nYour answer: ")
        user_responses[task_name] = response

    # response = input(f"{task_data['question']}\nYour answer: ")
    # user_responses[task_name] = response

# -------------------------------
# Scoring Tasks 1–4
# -------------------------------
print("\n--- Scoring Results ---")
for task_name, user_response in user_responses.items():
    result = score_with_gpt(task_name, user_response, tasks[task_name]['answers'])
    print(f"{task_name} Result: {result}\n")

# -------------------------------
# Run Task 5–8
# -------------------------------
print("\nTask 5: Object Recall")
task5_result = task5_object_recall()
print("Task 5 Result:", task5_result)

print("\nTask 6: Phrase Repetition")
task6_result = task6_phrase_repetition()
print("Task 6 Result:", task6_result)

print("\nTask 7: Sentence Construction")
task7_result = task7_sentence_construction()
print("Task 7 Result:", task7_result)

print("\nTask 8: Picture Copying")
task8_result = task8_picture_copying()
print("Task 8 Result:", task8_result)