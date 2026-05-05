import json
from typing import Any
from anthropic import Anthropic


def run_claude_analysis(api_key: str | None, model: str, files: list[dict], static_findings: list[dict]) -> list[dict[str, Any]]:
    if not api_key:
        return []
    client = Anthropic(api_key=api_key)
    payload = {
        "contracts": files,
        "static_findings": static_findings,
        "instructions": "Professional Solidity security audit. Return only valid JSON with findings array.",
    }
    prompt = (
        "Identify missed vulnerabilities, validate false positives, explain impacts, provide recommendations and Solidity patches, "
        "detect economic/logic/centralization/rugpull/honeypot risks. Output JSON only."
    )
    msg = client.messages.create(
        model=model,
        max_tokens=3000,
        temperature=0,
        system=prompt,
        messages=[{"role": "user", "content": json.dumps(payload)}],
    )
    text = msg.content[0].text
    parsed = json.loads(text)
    return parsed.get("findings", [])
