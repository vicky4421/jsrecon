#!/usr/bin/env python3
"""
Main entry for jsrecon (Option B modular package).
Usage:
  python3 jsrecon/main.py file.js
  curl -s URL | python3 jsrecon/main.py URL
  python3 jsrecon/main.py file.js --modules gf,entropy,urls
"""
import argparse
import sys
import os
from pathlib import Path
from modules.utils import Color

# silence DeprecationWarnings created when parsing patterns
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

from modules import gf_engine, entropy, graphql, urls, sinks, secrets, utils

parser = argparse.ArgumentParser(description="jsrecon - modular JS reconnaissance")
parser.add_argument("input", nargs="?", help="local JS file path, or (when piped) optional URL for naming")
parser.add_argument("--dump", "-d", default="gf_patterns_dump.txt", help="gf_patterns_dump.txt path or leave default to auto-locate (~/.gf/)")
parser.add_argument("--out", "-o", default="js_recon_output", help="root output directory")
parser.add_argument("--modules", "-m", default="gf,entropy,urls,domains,graphql,sinks,secrets", help="comma-separated modules to run")
parser.add_argument("--no-split", action="store_true", help="disable safe splitting")
parser.add_argument("--silent", action="store_true", help="less verbose output")
args = parser.parse_args()

# determine piped input
piped = not sys.stdin.isatty()
input_arg = args.input if args.input else None

# locate dump (delegated to gf_engine)
dump_path = gf_engine.locate_dump(Path(args.dump))

# determine base name & save_name
if piped:
    if input_arg:
        save_name = gf_engine.extract_filename_from_url(input_arg) or "piped_input.js"
        base = Path(save_name).stem
    else:
        save_name = "piped_input.js"
        base = "stdin_input"
else:
    if not input_arg:
        parser.print_help()
        sys.exit(1)
    if not Path(input_arg).is_file():
        print(Color.RED(f"[-] Local file not found: {input_arg}"))
        sys.exit(1)
    save_name = Path(input_arg).name
    base = Path(input_arg).stem

out_root = Path(args.out)
out_dir = out_root / base
out_dir.mkdir(parents=True, exist_ok=True)
print(Color.BLUE(f"[*] Output directory: {out_dir}"))

# read JS (from stdin or file)
if piped:
    js_raw = sys.stdin.read()
    src_path = out_dir / save_name
    src_path.write_text(js_raw, encoding="utf-8", errors="ignore")
    js_input_path = str(src_path)
else:
    js_input_path = input_arg

# prepare data (safe splitting by default)
print(Color.YELLOW("[*] Preparing JS for scanning (safe splitting)..."))
with open(js_input_path, "r", encoding="utf-8", errors="ignore") as f:
    raw = f.read()

if args.no_split:
    data = raw
else:
    data = utils.safe_split(raw)

# save readable.js
(readable := out_dir / "readable.js").write_text(data, encoding="utf-8", errors="ignore")

# build list of modules to run
mods = [m.strip().lower() for m in args.modules.split(",") if m.strip()]
# ensure gf runs first (since others may want gf outputs)
if "gf" in mods:
    # run GF engine
    print(Color.YELLOW("[*] Running GF engine..."))
    gf_engine.run_gf_pipeline(data, out_dir, dump_path, silent=args.silent)
# run other modules if requested
if "entropy" in mods:
    print(Color.YELLOW("[*] Running entropy-based secret detector..."))
    entropy.run_entropy(data, out_dir, silent=args.silent)
if "graphql" in mods:
    print(Color.YELLOW("[*] Extracting GraphQL queries..."))
    graphql.run_graphql(data, out_dir, silent=args.silent)
if "urls" in mods or "domains" in mods:
    print(Color.YELLOW("[*] Extracting URLs and domains..."))
    urls.run_urls(data, out_dir, include_domains=("domains" in mods), silent=args.silent)
if "sinks" in mods:
    print(Color.YELLOW("[*] Detecting JS sinks (XSS candidates)..."))
    sinks.run_sinks(data, out_dir, silent=args.silent)
if "secrets" in mods:
    print(Color.YELLOW("[*] Running unprefixed API key detector..."))
    secrets.run_unprefixed(data, out_dir, silent=args.silent)

print(Color.BLUE(f"\n[✔] Done. Results: {out_dir}"))
