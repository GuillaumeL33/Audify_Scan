import re


def extract_lines(code: str, pattern: str) -> list[int]:
    return [idx + 1 for idx, line in enumerate(code.splitlines()) if re.search(pattern, line)]
