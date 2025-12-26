import librosa
import parselmouth
import numpy as np
import sounddevice as sd
import wave
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key="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")

# ---------------- Audio Recording Functions ----------------

def record_audio(filename="recorded_audio.wav", duration=10, samplerate=16000):
    print(f"Recording for {duration} seconds...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='float32')
    sd.wait()  # Wait until recording is finished

    # Save as WAV file
    audio_int16 = np.int16(audio * 32767)
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio_int16.tobytes())

    print(f"Recording saved as {filename}")
    return filename

# ---------------- Feature Extraction Functions ----------------

def extract_temporal_features(audio, sr):
    intervals = librosa.effects.split(audio, top_db=30)
    speech_rate = len(intervals) / (len(audio) / sr)
    pauses = np.mean([len(p) for p in intervals]) / sr if len(intervals) > 0 else 0
    tempo, _ = librosa.beat.beat_track(y=audio, sr=sr)
    return {"tempo": tempo, "speech_rate": speech_rate, "pauses": pauses}

def extract_acoustic_features(audio, sr):
    snd = parselmouth.Sound(audio, sr)    
    # Pitch (optional, if you want)
    pitch = snd.to_pitch()    
    # Use praat.call for shimmer and jitter
    try:
        shimmer = parselmouth.praat.call(snd, "Get shimmer (local)", 0.0, 0.02, 1.3, 1.6, 0.03, 0.45)
    except:
        shimmer = 0
    try:
        jitter = parselmouth.praat.call(snd, "Get jitter (local)", 0.0, 0.02, 1.3)
    except:
        jitter = 0
    try:
        hnr = parselmouth.praat.call(snd, "To Harmonicity (cc)", 0.01, 75, 0.1, 1.0)
        hnr_value = parselmouth.praat.call(hnr, "Get mean", 0, 0)
    except:
        hnr_value = 0

    return {
        "jitter": jitter,
        "shimmer": shimmer,
        "hnr": hnr_value
    }

def extract_prosodic_features(audio, sr):
    pitch_contours = librosa.yin(audio, fmin=50, fmax=500, sr=sr)
    pitch_var = np.std(pitch_contours) if pitch_contours is not None else 0
    intensity = np.mean(librosa.feature.rms(y=audio))
    return {"pitch_var": pitch_var, "intensity": intensity}

# ---------------- Scoring with GenAI ----------------

def evaluate_task(task_name, audio_file):
    audio, sr = librosa.load(audio_file, sr=16000)

    temporal = extract_temporal_features(audio, sr)
    acoustic = extract_acoustic_features(audio, sr)
    prosodic = extract_prosodic_features(audio, sr)

    features = {"temporal": temporal, "acoustic": acoustic, "prosodic": prosodic}

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a clinical speech evaluation assistant."},
            {"role": "user", "content": f"Task: {task_name}. Features: {features}. Give a score out of 15 considering clarity, fluency, and prosody."}
        ]
    )

    return response.choices[0].message.content

# ---------------- Example Usage ----------------

if __name__ == "__main__":
    task = "Spontaneous Storytelling"

    # Record audio from mic
    recorded_file = record_audio(filename="patient_story.wav", duration=10)

    # Evaluate recorded file
    score = evaluate_task(task, recorded_file)
    print("Evaluation Score:", score)
