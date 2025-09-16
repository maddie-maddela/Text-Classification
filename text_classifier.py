#!/usr/bin/env python3
import re
from typing import Dict, List, Tuple, Union

def _compile(patterns: List[str]) -> List[re.Pattern]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]

# Strong, organ-specific indicators only (avoid symptoms & systemic physiology)
_LUNG_PATTERNS = _compile([
    r"\blung(s)?\b",
    r"\bpulmonar(?:y|ies)\b",
    r"\brespiratory tract\b",          # more specific than 'respiratory' alone
    r"\bbronch\w*\b",                  # bronchus/bronchi/bronchial
    r"\balveol\w*\b",                  # alveoli/alveolar
    r"\bpleur\w*\b",                   # pleura/pleural
    r"\bpneumon\w*\b",                 # pneumonia/pneumonitis
    r"\bCOPD\b",
    r"\bARDS\b",
    r"\binterstitial lung disease\b",
])

_KIDNEY_PATTERNS = _compile([
    r"\bkidney(s)?\b",
    r"\brenal\b",
    r"\bnephr\w*\b",                   # nephron/nephrology/nephritis
    r"\bglomerul\w*\b",
    r"\bcreatinin\w*\b",
    r"\bGFR\b",
    r"\bdialysis\b",
    r"\bproteinuria\b",
    r"\balbuminuria\b",
])

# Optional: terms we explicitly ignore to avoid false positives
# (e.g., symptoms or systemic physiology that shows up across diseases)
_IGNORE_PATTERNS = _compile([
    r"\bdyspnoe?a?\b",                 # dyspnoea/dyspnea
    r"\bshort(ness)? of breath\b",
    r"\brenin-angiotensin-aldosterone(-| )system\b",
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

def classify_medical_abstract(
    text: str,
    return_evidence: bool = False
) -> Union[str, Tuple[str, Dict[str, List[str]]]]:
    """
    Analyze a medical abstract to label it as 'lungs', 'kidneys', 'both', or 'neither'.

    Heuristic rules:
      • Count matches for organ-specific terms only.
      • Ignore common symptoms (e.g., dyspnoea) and systemic physiology (e.g., RAAS),
        which can otherwise cause false positives.

    Args:
        text: Abstract to analyze.
        return_evidence: If True, also return matched terms per class.

    Returns:
        label or (label, evidence_dict)
    """
    text = text or ""
    lung_hits = _find_hits(text, _LUNG_PATTERNS)
    kidney_hits = _find_hits(text, _KIDNEY_PATTERNS)
    _ = _find_hits(text, _IGNORE_PATTERNS)  # not used directly; patterns simply excluded above

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
        evidence = {
            "lungs": [h[0] for h in lung_hits],
            "kidneys": [h[0] for h in kidney_hits],
            "ignored": [h[0] for h in _find_hits(text, _IGNORE_PATTERNS)]
        }
        return label, evidence
    return label

# --- Main execution block ---
if __name__ == "__main__":
    abstract_text = """
    Both, the etiology and phenotype of heart failure differ largely. Following a cardiac
    injury (e.g., myocardial infarction, increased preload or afterload) cellular,
    structural and neurohumoral modulations occur that affect the phenotype being present.
    These processes influence the cell function among intra- as well as intercellular
    behavior. In consequence, activation of the sympathoadrenergic and
    renin-angiotensin-aldosterone-system takes place leading to adaptive mechanisms,
    which are accompanied by volume overload, tachycardia, dyspnoea and further
    deterioration of the cellular function (vicious circle). There exists no heart
    failure specific clinical sign; the clinical symptomatic shows progressive
    deterioration acutely or chronically.
    """

    label, evidence = classify_medical_abstract(abstract_text, return_evidence=True)
    print(label)
    # If you want to see why:
    # import json; print(json.dumps(evidence, indent=2))
