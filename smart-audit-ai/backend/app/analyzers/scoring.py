WEIGHTS = {"Critical": 20, "High": 12, "Medium": 7, "Low": 3, "Informational": 1}


def calculate_score(findings: list[dict]) -> tuple[int, str]:
    score = 100
    for f in findings:
        score -= WEIGHTS.get(f.get("severity", "Low"), 2)
    score = max(0, score)
    if score >= 90:
        level = "Excellent"
    elif score >= 75:
        level = "Good"
    elif score >= 50:
        level = "Moderate"
    elif score >= 25:
        level = "Risky"
    else:
        level = "Critical Risk"
    return score, level
