import tkinter as tk
from PIL import Image, ImageDraw
from openai import OpenAI
import base64
import re
import os
import json

API_KEY= "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"  
SAVE_PATH = "images\clock_drawing.png"
CANVAS_SIZE = 400
TARGET_TIME = "11:10"

client = OpenAI(api_key=API_KEY)


def load_image_base64(image_path):
    with open(image_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return encoded

def parse_model_response(response_text):
    match = re.search(r"```(?:json)?\s*(.*?)\s*```", response_text, flags=re.DOTALL)
    if match:
        json_str = match.group(1)
    else:
        json_str = response_text

    json_str = json_str.strip()
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        return {
            "error": "Failed to parse JSON",
            "raw_reply": response_text,
            "exception_msg": str(e),
            "extracted_text": json_str
        }

def evaluate_cdt(image_path, target_time=TARGET_TIME):
    prompt = f"""
You are a cognitive assessment expert evaluating a Clock Drawing Test (CDT) for dementia screening.
Score this clock drawing using these rules:
1. Clock Circle (0–3 points): 3 = closed, well-formed circle; 2 = minor distortion; 1 = open/incomplete; 0 = no circle.
2. Numbers (0–11 points): evenly spaced, correct order. Full credit if all correct; partial credit for missing/misplaced.
3. Hands (0–6 points): placement and proportion for {target_time}.
Return a JSON object as:
{{"circle_score":int, "numbers_score":int, "hands_score":int, "total_score":int, "explanation":str}}
Score strictly according to these rules.
    """

    image_b64 = load_image_base64(image_path)

    response = client.responses.create(
        model="gpt-4o",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text": prompt},
                {"type": "input_image", "image_url": f"data:image/png;base64,{image_b64}"},
            ],
        }]
    )
    output_text = response.output_text
    return parse_model_response(output_text)


if __name__ == "__main__":
    print("\nEvaluating existing clock drawing...")
    result = evaluate_cdt(SAVE_PATH, target_time=TARGET_TIME)
    print(json.dumps(result, indent=2))

# class DrawingApp:
#     def __init__(self, master):
#         self.master = master
#         master.title(f"Clock Drawing Test - Draw a clock showing {TARGET_TIME}")

#         self.canvas = tk.Canvas(master, width=CANVAS_SIZE, height=CANVAS_SIZE, bg="white", cursor="cross")
#         self.canvas.pack()

#         # Display target time at the top of the canvas
#         self.canvas.create_text(CANVAS_SIZE//2, 20, text=f"Draw clock showing {TARGET_TIME}", font=("Arial", 16), fill="blue")

#         self.image = Image.new("RGB", (CANVAS_SIZE, CANVAS_SIZE), "white")
#         self.draw = ImageDraw.Draw(self.image)

#         self.x = None
#         self.y = None

#         self.canvas.bind('<Button-1>', self.set_xy)
#         self.canvas.bind('<B1-Motion>', self.draw_line)

#         self.submit_btn = tk.Button(master, text="Submit Drawing", command=self.save_and_close)
#         self.submit_btn.pack(pady=10)

#         self.submitted = False

#     def set_xy(self, event):
#         self.x, self.y = event.x, event.y

#     def draw_line(self, event):
#         if self.x is not None and self.y is not None:
#             self.canvas.create_line((self.x, self.y, event.x, event.y), fill="black", width=2, capstyle=tk.ROUND, smooth=True)
#             self.draw.line([(self.x, self.y), (event.x, event.y)], fill="black", width=2)
#         self.x, self.y = event.x, event.y

#     def save_and_close(self):
#         # Draw the target time text on the saved image too
#         draw_text = ImageDraw.Draw(self.image)
#         draw_text.text((CANVAS_SIZE//2 - 80, 10), f"Draw clock showing {TARGET_TIME}", fill="blue")
#         self.image.save(SAVE_PATH, "PNG")
#         self.submitted = True
#         self.master.destroy()

# def load_image_base64(image_path):
#     with open(image_path, "rb") as f:
#         encoded = base64.b64encode(f.read()).decode("utf-8")
#     return encoded

# def parse_model_response(response_text):
#     # Match content inside ``` or ```json
#     match = re.search(r"```(?:json)?\s*(.*?)\s*```", response_text, flags=re.DOTALL)
#     if match:
#         json_str = match.group(1)  # Extract just the JSON inside the backticks
#     else:
#         json_str = response_text

#     json_str = json_str.strip()  # Remove whitespace/newlines outside JSON

#     try:
#         return json.loads(json_str)
#     except json.JSONDecodeError as e:
#         return {
#             "error": "Failed to parse JSON",
#             "raw_reply": response_text,
#             "exception_msg": str(e),
#             "extracted_text": json_str
#         }


# def evaluate_cdt(image_path, target_time=TARGET_TIME):
#     prompt = f"""
# You are a cognitive assessment expert evaluating a Clock Drawing Test (CDT) for dementia screening.
# Score this clock drawing using these rules:
# 1. Clock Circle (0–3 points): 3 = closed, well-formed circle; 2 = minor distortion; 1 = open/incomplete; 0 = no circle.
# 2. Numbers (0–11 points): evenly spaced, correct order. Full credit if all correct; partial credit for missing/misplaced.
# 3. Hands (0–6 points): placement and proportion for {target_time}.
# Return a JSON object as:
# {{"circle_score":int, "numbers_score":int, "hands_score":int, "total_score":int, "explanation":str}}
# Score strictly according to these rules.
#     """

#     image_b64 = load_image_base64(image_path)

#     response = client.responses.create(
#         model="gpt-4o",
#         input=[
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "input_text", "text": prompt},
#                     {"type": "input_image", "image_url": f"data:image/png;base64,{image_b64}"},
#                 ],
#             }
#         ]
#     )
#     output_text = response.output_text
#     return parse_model_response(output_text)

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = DrawingApp(root)
#     root.mainloop()

#     if app.submitted:
#         print("\nEvaluating drawing...")
#         result = evaluate_cdt(SAVE_PATH, target_time=TARGET_TIME)
#         print(json.dumps(result, indent=2))
#     else:
#         print("No drawing submitted.")