"""
Unprefixed API key detection: heuristic search for tokens in contexts like "key": "...."
"""
import re
from pathlib import Path

def run_unprefixed(data: str, out_dir: Path, silent=False):
    # look for JSON-like assignments where value is long and looks like a key
    matches = set()
    # "key": "SOMELONGSTRING..."
    for m in re.finditer(r'["\']([A-Za-z0-9_\-]{8,64})["\']\s*:\s*["\']([A-Za-z0-9_\-\/+]{8,128})["\']', data):
        # group1=keyname group2=value
        k = m.group(1)
        v = m.group(2)
        matches.add(f"{k}: {v}")
    # also look for assignment patterns like var API_KEY = "...."
    for m in re.finditer(r'\b([A-Za-z0-9_]{3,40})\s*=\s*["\']([A-Za-z0-9_\-\/+]{16,128})["\']', data):
        matches.add(f"{m.group(1)} = {m.group(2)}")
    if matches:
        base = out_dir / "regex_results"
        base.mkdir(parents=True, exist_ok=True)
        with open(base / "unprefixed_api_keys.txt", "w", encoding="utf-8") as fh:
            fh.write("\n".join(sorted(matches)))
        if not silent:
            print(f"[+] unprefixed_api_keys -> {len(matches)} matches")
    else:
        if not silent:
            print("[-] No unprefixed API keys found")
