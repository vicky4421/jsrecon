"""
Find JS sinks (DOM XSS candidates)
"""
import re
from pathlib import Path
from modules.utils import Color

SINKS = [
    r'innerHTML', r'outerHTML', r'document\.write', r'insertAdjacentHTML',
    r'new Function\(', r'eval\(', r'setTimeout\(', r'setInterval\(',
    r'innerText', r'open\(', r'location\.href', r'window\.location'
]

def run_sinks(data: str, out_dir: Path, silent=False):
    found = set()
    for s in SINKS:
        for m in re.finditer(s, data, flags=re.IGNORECASE):
            # return the line snippet around match
            span = m.span()
            start = max(0, span[0]-80)
            end = min(len(data), span[1]+80)
            found.add(data[start:end].replace("\n","\\n"))
    if found:
        base = out_dir / "regex_results"
        base.mkdir(parents=True, exist_ok=True)
        with open(base / "js_sinks_advanced.txt", "w", encoding="utf-8") as fh:
            fh.write("\n\n".join(sorted(found)))
        if not silent:
            print(Color.GREEN(f"[+] js_sinks_advanced -> {len(found)} matches"))
    else:
        if not silent:
            print(Color.RED("[-] No JS sinks found"))
