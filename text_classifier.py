#!/usr/bin/env python3
"""
Organ-pertinence classifier (lungs / kidneys / both / neither)

Usage:
  # 1) Run with the built-in sample (from your prompt)
  python app.py

  # 2) Or pass text directly
  python app.py --text "Abstract text goes here..."

  # 3) Or read from a file
  python app.py --file path/to/abstract.txt

  # Optional: show matched terms for debugging
  python app.py --text "..." --show-matches
"""

import re
import argparse
from pathlib import Path
from typing import List, Tuple

# Default text from the prompt
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

# Terms that strongly indicate LUNGS (direct organ/system mentions).
# Note: We intentionally exclude symptoms like "dyspnea" to avoid false positives.
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

# Terms that strongly indicate KIDNEYS (direct organ/system mentions).
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

def compile_patterns(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p, flags=re.IGNORECASE) for p in patterns]

CP_LUNG = compile_patterns(LUNG_PATTERNS)
CP_KIDNEY = compile_patterns(KIDNEY_PATTERNS)

def find_matches(text: str, compiled: List[re.Pattern]) -> List[Tuple[str, Tuple[int, int]]]:
    """Return list of (matched_text, (start, end)) for any pattern matches."""
    hits = []
    for pat in compiled:
        for m in pat.finditer(text):
            hits.append((m.group(0), m.span()))
    return hits

def classify(text: str, show_matches: bool = False) -> str:
    t = text.lower()

    lung_hits = find_matches(t, CP_LUNG)
    kidney_hits = find_matches(t, CP_KIDNEY)

    if show_matches:
        if lung_hits:
            print("Lung matches:", [h[0] for h in lung_hits])
        if kidney_hits:
            print("Kidney matches:", [h[0] for h in kidney_hits])

    has_lungs = len(lung_hits) > 0
    has_kidneys = len(kidney_hits) > 0

    if has_lungs and has_kidneys:
        return "both"
    if has_lungs:
        return "lungs"
    if has_kidneys:
        return "kidneys"
    return "neither"

def main():
    parser = argparse.ArgumentParser(description="Classify abstract as lungs/kidneys/both/neither.")
    parser.add_argument("--text", type=str, help="Abstract text to classify.")
    parser.add_argument("--file", type=str, help="Path to a file containing the abstract.")
    parser.add_argument("--show-matches", action="store_true", help="Print matched terms for debugging.")
    args = parser.parse_args()

    if args.file:
        text = Path(args.file).read_text(encoding="utf-8", errors="ignore")
    elif args.text:
        text = args.text
    else:
        text = DEFAULT_TEXT  # fall back to the prompt’s sample

    label = classify(text, show_matches=args.show_matches)
    print(label)

if __name__ == "__main__":
    main()
