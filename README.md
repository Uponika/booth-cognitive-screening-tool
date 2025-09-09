# booth-cognitive-screening-tool

# Cognitive Assessment Tool 🧠

![Python](https://img.shields.io/badge/python-3.11-blue?logo=python)
![License](https://img.shields.io/badge/license-MIT-green)

This project implements a series of cognitive assessment tasks including **object naming, memory recall, sentence construction, phrase repetition, and picture copying**. It combines a Python backend with an interactive UI for assessment.

---

## Project Structure

- `Api/` – Backend scripts for each cognitive task.  
- `UI/` – Frontend interface for users to perform assessments.  
- `images/` – Reference and object images used in tasks.  
- `requirements.txt` – Python dependencies for backend.  

---

## Setup Instructions

### 1️⃣ Create a Virtual Environment
```bash 
python -m venv .venv
```

### 2️⃣ Activate the Virtual Environment
```bash 
.venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash 
pip install -r Api/requirements.txt
```
### 4️⃣ Run Backend Tasks
```bash 
cd Api
python MMSE-tasks.py
```

### 5️⃣ Run the UI
```bash 
cd ../UI
python app.py
```

