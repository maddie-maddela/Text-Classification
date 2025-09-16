#!/usr/bin/env python3
import re
from typing import Dict, List, Tuple
import streamlit as st

# ---------- Heuristics (organ-specific; avoid symptoms/systemic-only terms) ----------
def _compile(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]

LUNG_PATTERNS = _compile([
    r"\blung(s)?\b",
    r"\bpulmonar(?:y|ies)\b",
    r"\brespiratory tract\b",
    r"\bbronch\w*\b",
    r"\balveol\w*\b",
    r"\bpleur\w*\b",
    r"\bpneumon\w*\b",
    r"\bCOPD\b",
    r"\bARDS\b",
    r"\binterstitial lung disease\b",
])

KIDNEY_PATTERNS = _compile([
    r"\bkidney(s)?\b",
    r"\brenal\b",
    r"\bnephr\w*\b",
    r"\bglomerul\w*\b",
    r"\bcreatinin\w*\b",
    r"\bGFR\b",
    r"\bdialysis\b",
    r"\bproteinuria\b",
    r"\balbuminuria\b",
])

IGNORE_PATTERNS = _compile([
    r"\bdyspnoe?a?\b",                           # dyspnoea/dyspnea (symptom)
    r"\bshort(ness)? of breath\b",
    r"\brenin-angiotensin-aldosterone(-| )system\b",  # systemic physiology
    r"\bRAAS\b",
    r"\btachycardia\b",
    r"\bhypertension\b",
])

def _find_hits(text: str, patterns: List[re.Pattern]) -> List[Tuple[str, Tuple[int, int]]]:
    hits = []
    for p in patterns:
        for m in p.finditer(text):
            hits.append((m.group(0), m.span()))
    return hits

def classify_medical_abstract(text: str, return_evidence: bool = False):
    text = text or ""
    lung_hits = _find_hits(text, LUNG_PATTERNS)
    kidney_hits = _find_hits(text, KIDNEY_PATTERNS)
    ignored_hits = _find_hits(text, IGNORE_PATTERNS)

    has_lungs = len(lung_hits) > 0
    has_kidneys = len(kidney_hits) > 0

    if has_lungs and has_kidneys:
        label = "both"
    elif has_lungs:
        label = "lungs"
    elif has_kidneys:
        label = "kidneys"
    else:
        label = "neither"

    if return_evidence:
        return label, {
            "lungs": [h[0] for h in lung_hits],
            "kidneys": [h[0] for h in kidney_hits],
            "ignored": [h[0] for h in ignored_hits],
        }
    return label

# ---------- UI ----------
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

st.set_page_config(page_title="Organ Pertinence Classifier", page_icon="🩺", layout="centered")
st.title("🩺 Organ Pertinence Classifier")
st.write("Study the abstract and decide if it pertains to **lungs**, **kidneys**, **both**, or **neither**. Returns a single label.")

# Input area
col1, col2 = st.columns([3, 2])
with col1:
    show_evidence = st.checkbox("Show evidence (matched terms)", value=False)
with col2:
    use_sample = st.toggle("Use sample abstract", value=True)

uploaded = st.file_uploader("…or upload a .txt file", type=["txt"])

if uploaded is not None:
    text = uploaded.read().decode("utf-8", errors="ignore")
else:
    text = DEFAULT_TEXT if use_sample else ""

text = st.text_area("Abstract", value=text, height=260, placeholder="Paste abstract text here…")

# Action
if st.button("Classify", type="primary", use_container_width=True):
    if show_evidence:
        label, evidence = classify_medical_abstract(text, return_evidence=True)
    else:
        label = classify_medical_abstract(text, return_evidence=False)

    st.subheader("Result")
    st.success(label)

    if show_evidence:
        with st.expander("Matched terms (debug)"):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.caption("Lungs")
                if evidence["lungs"]:
                    st.write(", ".join(sorted(set(evidence["lungs"]))))

                else:
                    st.write("—")
            with c2:
                st.caption("Kidneys")
                if evidence["kidneys"]:
                    st.write(", ".join(sorted(set(evidence["kidneys"]))))

                else:
                    st.write("—")
            with c3:
                st.caption("Ignored (symptoms/systemic)")
                if evidence["ignored"]:
                    st.write(", ".join(sorted(set(evidence["ignored"]))))

                else:
                    st.write("—")
