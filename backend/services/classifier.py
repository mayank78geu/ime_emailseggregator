"""
Classifier — determines shipping email record category from a text block.
Categories: TONNAGE | CARGO_VC | CARGO_TC
"""

KEYWORDS = {
    "TONNAGE": [
        "DWT", "OPEN", "M/V", "MV ", "VESSEL", "O/A", "BULK CARRIER",
        "SCRUBBER", "GEARED", "BUILT", "FLAG", "LOA", "BEAM", "GRAIN CAP",
        "HO/HA", "CRANE", "KNOTS", "BALLAST", "LADEN", "SDBC", "SDSTBC",
        "GRABBER", "BWTS", "CLASS", "HULL"
    ],
    "CARGO_VC": [
        "LOAD PORT", "POL", "DISCHARGE PORT", "POD", "LAYCAN", "MOLOCHOPT",
        "MT HRC", "MT IRON", "MT UREA", "MT COAL", "CARGO", "FIOS",
        "PWWD", "SSHEX", "SHINC", "FHINC", "CQD", "TTL", "COM :",
        "LOADING PORT", "DISCHARGING PORT", "LOADPORT", "DISCH"
    ],
    "CARGO_TC": [
        "DELIVERY", "REDELIVERY", "TCT", "TIME CHARTER", "DURATION",
        "DELY", "REDEL", "1 TCT", "2 TCT", "3 TCT", "ADDCOM",
        "ADC", "WOG", "SMX", "UMX", "PMAX", "HMAX",
        "SHORT PERIOD", "YEARS", "MONTHS", "DAYS WOG"
    ],
}


def classify(text: str) -> str:
    """
    Score each category by keyword hit count and return the winner.
    Falls back to TONNAGE if no clear signal.
    """
    text_upper = text.upper()
    scores = {}
    for cat, keywords in KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_upper)
        scores[cat] = score

    best = max(scores, key=scores.get)

    # If all scores are 0, make a best-guess based on structural hints
    if scores[best] == 0:
        if "DELIVERY" in text_upper or "REDEL" in text_upper:
            return "CARGO_TC"
        if "POL" in text_upper or "POD" in text_upper:
            return "CARGO_VC"
        return "TONNAGE"

    return best
