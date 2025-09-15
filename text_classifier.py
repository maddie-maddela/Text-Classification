def classify_medical_abstract(text: str) -> str:
    """
    Analyzes a medical abstract to determine if it pertains to lungs, kidneys, both, or neither.

    Args:
        text: The abstract text to analyze.

    Returns:
        A single label: 'lungs', 'kidneys', 'both', or 'neither'.
    """
    # Convert text to lowercase for case-insensitive matching
    lower_text = text.lower()

    # Define keywords for each category
    # 'Dyspnoea' (shortness of breath) is a key lung-related symptom.
    # The 'renin-angiotensin-aldosterone-system' is a hormonal system
    # critically involving the kidneys to regulate blood pressure and fluid balance.
    lung_keywords = ['dyspnoea', 'respiratory', 'pulmonary']
    kidney_keywords = ['renin', 'aldosterone', 'renal', 'nephro']

    # Check for the presence of keywords
    found_lungs = any(keyword in lower_text for keyword in lung_keywords)
    found_kidneys = any(keyword in lower_text for keyword in kidney_keywords)

    # Determine the final classification based on findings
    if found_lungs and found_kidneys:
        return 'both'
    elif found_lungs:
        return 'lungs'
    elif found_kidneys:
        return 'kidneys'
    else:
        return 'neither'

# --- Main execution block ---
if __name__ == "__main__":
    # The abstract text provided in the prompt
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

    # Get the classification label by running the function
    label = classify_medical_abstract(abstract_text)

    # Print the final, single-label response
    print(label)
