import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser
from PIL import Image, ImageDraw, ImageTk, ImageFont
from datetime import datetime

BRAND = "#0d6efd"   # bootstrap primary blue
HEADER_HEIGHT = 80
CANVAS_W, CANVAS_H = 900, 600

def script_dir():
    # Save alongside the .py file (same “root path”)
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

class ClockDrawingApp:
    def __init__(self, root):
        self.root = root
        root.title("Clock Drawing Test – Quizzard Style")
        root.geometry("1100x820")

        # State
        self.tool = "pen"
        self.stroke_color = "#111111"
        self.stroke_size = 6
        self.last = None
        self.history = []  # stack of PIL images
        self.max_history = 50

        # PIL drawing surface (what we actually save)
        self.img = Image.new("RGB", (CANVAS_W, CANVAS_H), "white")
        self.draw = ImageDraw.Draw(self.img)
        self._add_intro_text()

        # --- UI Layout ---
        outer = ttk.Frame(root, padding=12)
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer)
        header.pack(fill="x", pady=(0, 8))

        title_badge = tk.Label(
            header, text="Clock Drawing Test", bg="white", fg=BRAND,
            font=("Segoe UI", 12, "bold"), bd=0, relief="flat", padx=12, pady=6
        )
        title_badge.pack(side="left")
        target = ttk.Label(
            header, text="Target time: 10 minutes after 11",
            font=("Segoe UI", 10, "bold")
        )
        target.pack(side="right")

        # Instructions
        instr = tk.Frame(outer, bg="#f8fbff", highlightthickness=0)
        instr.pack(fill="x", pady=(0, 10))
        left_border = tk.Frame(instr, bg=BRAND, width=8, height=1)
        left_border.pack(side="left", fill="y")
        instr_body = tk.Frame(instr, bg="#f8fbff", padx=14, pady=10)
        instr_body.pack(fill="both", expand=True)
        tk.Label(instr_body, text="Follow the instructions below to draw a clock.",
                 fg=BRAND, bg="#f8fbff", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        steps = [
            "Step 1. Draw a full circle",
            "Step 2. Place numbers on the circle like a clock",
            "Step 3. Place hands on the clock showing the time to be 10 minutes after 11",
        ]
        for s in steps:
            tk.Label(instr_body, text="• " + s, bg="#f8fbff",
                     font=("Segoe UI", 11, "bold")).pack(anchor="w")

        # Toolbar
        tools = ttk.Frame(outer)
        tools.pack(fill="x", pady=(0, 8))

        self.pen_btn = ttk.Button(tools, text="✏️ Pen", command=self.use_pen)
        self.eraser_btn = ttk.Button(tools, text="🧽 Eraser", command=self.use_eraser)
        self.pen_btn.grid(row=0, column=0, padx=4, pady=4)
        self.eraser_btn.grid(row=0, column=1, padx=4, pady=4)

        ttk.Separator(tools, orient="vertical").grid(row=0, column=2, sticky="ns", padx=8)

        ttk.Label(tools, text="Color", font=("Segoe UI", 10, "bold")).grid(row=0, column=3, padx=(6, 2))
        self.color_btn = tk.Button(tools, width=3, bg=self.stroke_color, command=self.pick_color)
        self.color_btn.grid(row=0, column=4, padx=(0, 8))

        ttk.Label(tools, text="Size", font=("Segoe UI", 10, "bold")).grid(row=0, column=5, padx=(6, 2))
        self.size_var = tk.IntVar(value=self.stroke_size)
        self.size_scale = ttk.Scale(tools, from_=2, to=40, orient="horizontal",
                                    command=self.on_size_change, length=180)
        self.size_scale.set(self.stroke_size)
        self.size_scale.grid(row=0, column=6, padx=(0, 6))
        self.size_lbl = ttk.Label(tools, text=str(self.stroke_size), font=("Segoe UI", 10, "bold"))
        self.size_lbl.grid(row=0, column=7, padx=(0, 8))

        tools.grid_columnconfigure(8, weight=1)  # spacer / push right side

        self.undo_btn = ttk.Button(tools, text="↶ Undo", command=self.undo)
        self.clear_btn = ttk.Button(tools, text="🗑️ Clear", command=self.clear_canvas)
        self.submit_btn = ttk.Button(tools, text="✅ Submit", command=self.submit)
        self.undo_btn.grid(row=0, column=9, padx=4, pady=4)
        self.clear_btn.grid(row=0, column=10, padx=4, pady=4)
        self.submit_btn.grid(row=0, column=11, padx=4, pady=4)

        # Canvas area
        canvas_wrap = tk.Frame(outer, bd=2, relief="groove", bg="#ffffff")
        canvas_wrap.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(canvas_wrap, width=CANVAS_W, height=CANVAS_H,
                                bg="white", highlightthickness=0)
        self.canvas.pack(padx=10, pady=10)

        # Prepare image on canvas
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.canvas_image_id = self.canvas.create_image(0, 0, image=self.tkimg, anchor="nw")

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        # Visual state
        self._set_active_button(self.pen_btn)
        self.push_history()  # baseline

        # Tip
        ttk.Label(
            outer,
            text="Tip: Use the mouse to draw. You can Undo or Clear anytime.",
            foreground="#666"
        ).pack(anchor="w", pady=(6, 0))

        # Style polish (optional)
        try:
            from ctypes import windll  # noqa
            root.iconbitmap("")  # can set a .ico if you like
        except Exception:
            pass

    # ---------- Drawing helpers ----------
    def _update_canvas_from_image(self):
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.canvas.itemconfig(self.canvas_image_id, image=self.tkimg)

    def _add_intro_text(self):
        # Subtle watermark line like the JS init()
        try:
            font = ImageFont.truetype(self._pick_font(), 20)
        except Exception:
            font = ImageFont.load_default()
        self.draw.text((16, 12), "Draw a clock showing 10 minutes after 11",
                       fill=(13, 110, 253, 180), font=font)

    def _pick_font(self):
        # Try a few common fonts; fallback handled by PIL if not found
        candidates = [
            "SegoeUI.ttf", "Segoe UI.ttf", "Arial.ttf", "Roboto-Regular.ttf"
        ]
        sysfont = os.path.join(os.path.expanduser("~"), "AppData/Local/Microsoft/Windows/Fonts")
        search_paths = ["", sysfont, "/usr/share/fonts", "/Library/Fonts", "/System/Library/Fonts"]
        for folder in search_paths:
            for name in candidates:
                p = os.path.join(folder, name)
                if os.path.exists(p):
                    return p
        raise FileNotFoundError

    def push_history(self):
        # Keep a capped stack of previous images
        self.history.append(self.img.copy())
        if len(self.history) > self.max_history:
            self.history.pop(0)

    # ---------- Tools ----------
    def _set_active_button(self, btn):
        # Give a bolded/relief visual
        for b in (self.pen_btn, self.eraser_btn):
            b.state(["!pressed"])
        btn.state(["pressed"])

    def use_pen(self):
        self.tool = "pen"
        self._set_active_button(self.pen_btn)

    def use_eraser(self):
        self.tool = "eraser"
        self._set_active_button(self.eraser_btn)

    def pick_color(self):
        color = colorchooser.askcolor(initialcolor=self.stroke_color, title="Pick stroke color")
        if color and color[1]:
            self.stroke_color = color[1]
            self.color_btn.configure(bg=self.stroke_color)

    def on_size_change(self, val):
        try:
            self.stroke_size = int(float(val))
        except Exception:
            self.stroke_size = 6
        self.size_lbl.config(text=str(self.stroke_size))

    # ---------- Mouse drawing ----------
    def on_press(self, event):
        self.push_history()
        self.last = (event.x, event.y)

    def on_move(self, event):
        if not self.last:
            return
        x0, y0 = self.last
        x1, y1 = event.x, event.y

        # Draw on PIL image
        color = self.stroke_color if self.tool == "pen" else "#ffffff"
        self.draw.line((x0, y0, x1, y1), fill=color, width=self.stroke_size, joint="curve")

        # Update canvas
        self._update_canvas_from_image()

        # Next segment
        self.last = (x1, y1)

    def on_release(self, _event):
        self.last = None

    # ---------- Commands ----------
    def undo(self):
        if len(self.history) <= 1:
            return
        # Discard current, revert to previous
        self.history.pop()
        self.img = self.history[-1].copy()
        self.draw = ImageDraw.Draw(self.img)
        self._update_canvas_from_image()

    def clear_canvas(self):
        self.push_history()
        self.img = Image.new("RGB", (CANVAS_W, CANVAS_H), "white")
        self.draw = ImageDraw.Draw(self.img)
        self._update_canvas_from_image()

    def submit(self):
        # Compose header + drawing and save alongside the script
        out_w, out_h = CANVAS_W, CANVAS_H + HEADER_HEIGHT
        final_img = Image.new("RGB", (out_w, out_h), "white")
        fdraw = ImageDraw.Draw(final_img)

        # Header text
        title = "Clock Drawing Test – Draw 10 minutes after 11"
        try:
            font = ImageFont.truetype(self._pick_font(), 28)
        except Exception:
            font = ImageFont.load_default()

        fdraw.text((16, 24), title, fill=BRAND, font=font, anchor="ls")  # left, baseline-ish

        # Paste the drawing
        final_img.paste(self.img, (0, HEADER_HEIGHT))

        # Save to same root path
        out_path = os.path.join(script_dir(), "clock_drawing.png")
        try:
            final_img.save(out_path, "PNG")
            messagebox.showinfo("Saved", f"Image saved:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Save failed", f"Could not save image:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    # Use ttk theme if available
    try:
        from tkinter import ttk
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
    except Exception:
        pass
    app = ClockDrawingApp(root)
    root.mainloop()
