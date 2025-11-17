"""
Extract URLs and (optionally) domains.
"""
import re
from urllib.parse import urlparse
from pathlib import Path
from modules.utils import Color

def run_urls(data: str, out_dir: Path, include_domains=False, silent=False):
    urls = set(re.findall(r'https?://[^\s"\'<>]+', data))
    # also capture /api/ endpoints
    endpoints = set(re.findall(r'\/api\/[A-Za-z0-9_/\-\{\}]+', data))
    if urls or endpoints:
        base = out_dir / "regex_results"
        base.mkdir(parents=True, exist_ok=True)
        if urls:
            with open(base / "urls.txt", "w", encoding="utf-8") as fh:
                fh.write("\n".join(sorted(urls)))
        if endpoints:
            with open(base / "endpoints.txt", "w", encoding="utf-8") as fh:
                fh.write("\n".join(sorted(endpoints)))
        if include_domains and urls:
            domains = set()
            for u in urls:
                try:
                    domains.add(urlparse(u).netloc)
                except:
                    pass
            with open(base / "domains.txt", "w", encoding="utf-8") as fh:
                fh.write("\n".join(sorted(domains)))
        if not silent:
            print(Color.GREEN(f"[+] urls -> {len(urls)} urls, {len(endpoints)} endpoints"))
    else:
        if not silent:
            print(Color.RED("[-] No URLs or endpoints found"))
