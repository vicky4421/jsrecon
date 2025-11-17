"""
Entropy-based secret detection
- Scans for base64-like or alnum blobs and uses Shannon entropy threshold
"""
import re, math
from pathlib import Path
from modules.utils import Color

def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    probs = [float(s.count(c)) / len(s) for c in set(s)]
    return - sum(p * math.log2(p) for p in probs)

def candidate_blobs(text: str):
    # base64-like long strings (>=32 chars), or hex blobs, or mixed alnum dots/underscores
    blobs = set()
    # base64-like (A-Za-z0-9+/=) length >= 32
    for m in re.finditer(r'([A-Za-z0-9\-_+/]{32,})', text):
        blobs.add(m.group(1))
    # hex-like length >= 32
    for m in re.finditer(r'\b([0-9a-fA-F]{32,})\b', text):
        blobs.add(m.group(1))
    # alnum with special allowed chars length >=32
    for m in re.finditer(r'([A-Za-z0-9_\-]{32,})', text):
        blobs.add(m.group(1))
    return blobs

def run_entropy(data: str, out_dir: Path, silent=False, entropy_threshold=4.2):
    blobs = candidate_blobs(data)
    found = []
    for b in blobs:
        e = shannon_entropy(b)
        if e >= entropy_threshold:
            found.append((b, round(e,3)))
    if found:
        out = out_dir / "regex_results" / "entropy_secrets.txt"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            fh.write("# blob | entropy\n")
            for b,e in sorted(found, key=lambda x:-x[1]):
                fh.write(f"{b} | {e}\n")
        if not silent:
            print(Color.GREEN(f"[+] entropy_secrets -> {len(found)} matches"))
    else:
        if not silent:
            print(Color.RED("[-] No entropy secrets found"))
