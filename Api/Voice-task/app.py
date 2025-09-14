from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from datetime import datetime

app = FastAPI()

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SAVE_DIR = r"D:\Projects\Dementia Project\booth-cognitive-screening-tool\Api\Voice-task"
os.makedirs(SAVE_DIR, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
def serve_ui():
    """Serve the recording page"""
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/upload-audio")
async def upload_audio(
    file: UploadFile,
    assessment: str = Form(...),
    question: str = Form(...)
):
    """Save uploaded audio file"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Clean question text → safe filename
    safe_q = "".join(c if c.isalnum() or c in " -_" else "_" for c in question)[:50]

    filename = f"{assessment.replace(' ','_')}-{safe_q}-{timestamp}.webm"
    file_path = os.path.join(SAVE_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"status": "saved", "path": file_path}
