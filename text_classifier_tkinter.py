#!/usr/bin/env python3
# app.py
# GUI classifier: outputs a single label: lungs / kidneys / both / neither

import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import List, Tuple

# ---------- Defaults ----------
DEFAULT_TEXT = (
    "Both, the etiology and phenotype of heart failure differ largely. Following a cardiac injury "
    "(e.g., myocardial infarction, increased preload or afterload) cellular, structural and "
    "neurohumoral modulations occur that affect the phenotype being present. These processes "
    "influence the cell function among intra- as well as intercellular behavior. In consequence, "
    "activation of the sympathoadrenergic and renin-angiotensin-aldosterone-system takes place "
    "leading to adaptive mechanisms, which are accompanied by volume overload, tachycardia, "
    "dyspnoea and further deterioration of the cellular function (vicious circle). There exists no "
    "heart failure specific clinical sign; the clinical symptomatic shows progressive deterioration "
    "acutely or chronically."
)

# ---------- Patterns ----------
LUNG_PATTERNS = [
    r"\blung(s)?\b",
    r"\bpulmonar(?:y|ies)\b",
    r"\brespirator(?:y|ies)\b",
    r"\bbronch\w*\b",
    r"\balveol\w*\b",
    r"\bspirometr\w*\b",
    r"\bpleur\w*\b",
    r"\binterstitial lung disease\b",
    r"\bARDS\b",
    r"\bCOPD\b",
    r"\bpneumon\w*\b",
]

KIDNEY_PATTERNS = [
    r"\bkidney(s)?\b",
    r"\brenal\b",
    r"\bnephr\w*\b",         # nephron, nephrology, nephritis, etc.
    r"\bglomerul\w*\b",
    r"\bcreatinin\w*\b",
    r"\bGFR\b",
    r"\bdialysis\b",
    r"\balbuminuria\b",
]

def _compile(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]

CP_LUNG = _compile(LUNG_PATTERNS)
CP_KIDNEY = _compile(KIDNEY_PATTERNS)

def _find_hits(text: str, pats: List[re.Pattern]) -> List[Tuple[str, Tuple[int, int]]]:
    hits = []
    for pat in pats:
        for m in pat.finditer(text):
            hits.append((m.group(0), m.span()))
    return hits

def classify(text: str) -> str:
    t = text if isinstance(text, str) else ""
    lung_hits = _find_hits(t, CP_LUNG)
    kidney_hits = _find_hits(t, CP_KIDNEY)

    has_lungs = len(lung_hits) > 0
    has_kidneys = len(kidney_hits) > 0

    if has_lungs and has_kidneys:
        return "both"
    if has_lungs:
        return "lungs"
    if has_kidneys:
        return "kidneys"
    return "neither"

# ---------- GUI ----------
def main():
    root = tk.Tk()
    root.title("Organ Pertinence Classifier")
    root.geometry("900x600")

    # Top controls
    top = ttk.Frame(root, padding=10)
    top.pack(fill="x")

    ttk.Label(top, text="Paste abstract text below, then click Classify").pack(side="left")

    def load_file():
        path = filedialog.askopenfilename(
            title="Open abstract",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            try:
                text = Path(path).read_text(encoding="utf-8", errors="ignore")
                text_box.delete("1.0", "end")
                text_box.insert("1.0", text)
            except Exception as e:
                messagebox.showerror("Error", f"Couldn't open file:\n{e}")

    def save_text():
        path = filedialog.asksaveasfilename(
            title="Save text",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            try: 
                Path(path).write_text(text_box.get("1.0", "end-1c"), encoding="utf-8")
            except Exception as e:
                messagebox.showerror("Error", f"Couldn't save file:\n{e}")

    btn_frame = ttk.Frame(top)
    btn_frame.pack(side="right")
    ttk.Button(btn_frame, text="Open…", command=load_file).pack(side="left", padx=4)
    ttk.Button(btn_frame, text="Save…", command=save_text).pack(side="left", padx=4)

    # Text input
    center = ttk.Frame(root, padding=(10, 0, 10, 0))
    center.pack(fill="both", expand=True)

    text_box = tk.Text(center, wrap="word", height=20, undo=True)
    text_box.pack(fill="both", expand=True)
    text_box.insert("1.0", DEFAULT_TEXT)

    # Bottom action row
    bottom = ttk.Frame(root, padding=10)
    bottom.pack(fill="x")

    result_var = tk.StringVar(value="")
    result_label = ttk.Label(bottom, textvariable=result_var, font=("Segoe UI", 14, "bold"))
    result_label.pack(side="right")

    def do_classify():
        txt = text_box.get("1.0", "end-1c").strip()
        if not txt:
            messagebox.showwarning("No text", "Please paste an abstract first.")
            return
        label = classify(txt)
        result_var.set(label)   # single-word label only

    ttk.Button(bottom, text="Clear", command=lambda: (text_box.delete("1.0", "end"), result_var.set(""))).pack(side="left")
    ttk.Button(bottom, text="Classify", command=do_classify).pack(side="left", padx=8)

    root.mainloop()

if __name__ == "__main__":
    main()
