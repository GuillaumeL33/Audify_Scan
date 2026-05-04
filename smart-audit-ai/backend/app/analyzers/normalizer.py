def normalize_and_dedup(findings: list[dict]) -> list[dict]:
    normalized = []
    seen = set()
    for f in findings:
        key = (f.get("title"), f.get("file"), f.get("line"))
        if key in seen:
            continue
        seen.add(key)
        f.setdefault("severity", "Medium")
        f.setdefault("status", "open")
        normalized.append(f)
    return normalized
