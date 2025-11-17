"""
GF engine: loads gf_patterns_dump.txt, extracts patterns, auto-fix and runs them.
"""
from pathlib import Path
import re
from . import auto_fix, utils
from modules.utils import Color

def locate_dump(user_path: Path):
    user = Path(user_path)
    local = Path("gf_patterns_dump.txt")
    home = Path.home() / ".gf" / "gf_patterns_dump.txt"
    if user.exists():
        return user
    if local.exists():
        return local
    if home.exists():
        return home
    raise FileNotFoundError("gf_patterns_dump.txt not found. Generate and place at ~/.gf/gf_patterns_dump.txt or in pwd.")

def extract_filename_from_url(url):
    return utils.extract_filename_from_url(url)

def parse_dump(dump_path: Path):
    txt = dump_path.read_text(encoding="utf-8", errors="ignore")
    blocks = []
    cur = None
    cur_lines = []
    for line in txt.splitlines():
        if line.strip().startswith("###FILE:"):
            if cur:
                blocks.append((cur, "\n".join(cur_lines)))
            cur = line.split("###FILE:",1)[1].strip()
            cur_lines = []
        else:
            if cur is not None:
                cur_lines.append(line)
    if cur:
        blocks.append((cur, "\n".join(cur_lines)))
    return blocks

def extract_patterns_from_block(block_text):
    pats = []
    flags = ""
    m = re.search(r'"flags"\s*:\s*"([^"]+)"', block_text)
    if m:
        flags = m.group(1)
    for m in re.finditer(r'"pattern"\s*:\s*"((?:\\.|[^"\\])*)"', block_text):
        s = m.group(1)
        try:
            s = bytes(s, "utf-8").decode("unicode_escape")
        except Exception:
            pass
        pats.append(s)
    arr = re.search(r'"patterns"\s*:\s*\[([^\]]+)\]', block_text, re.DOTALL)
    if arr:
        inner = arr.group(1)
        for m in re.finditer(r'"((?:\\.|[^"\\])*)"', inner):
            s = m.group(1)
            try:
                s = bytes(s, "utf-8").decode("unicode_escape")
            except Exception:
                pass
            pats.append(s)
    # fallback single-quoted
    for m in re.finditer(r"'((?:\\.|[^'\\])*)'", block_text):
        s = m.group(1)
        try:
            s = bytes(s, "utf-8").decode("unicode_escape")
        except Exception:
            pass
        if s not in pats:
            pats.append(s)
    return pats, flags

def run_gf_pipeline(data: str, out_dir: Path, dump_path: Path, silent=False):
    blocks = parse_dump(dump_path)
    if not silent:
        print(Color.YELLOW(f"[*] Parsed {len(blocks)} GF blocks"))
    # prepare compiled dict
    compiled_map = {}  # name -> list of (mode, compiled_or_tokens, orig_pat, flags)
    for name, block in blocks:
        pats, flags = extract_patterns_from_block(block)
        if not pats:
            continue
        compiled_map[name] = []
        for pat in pats:
            # try compile as-is with flags mapping (best-effort attempt)
            re_flags = 0
            if flags:
                if 'i' in flags.lower():
                    re_flags |= re.IGNORECASE
                if 'm' in flags.lower():
                    re_flags |= re.MULTILINE
                if 's' in flags.lower():
                    re_flags |= re.DOTALL
            try:
                cre = re.compile(pat, re_flags)
                compiled_map[name].append(('regex', cre, pat, flags))
                continue
            except re.error:
                # try auto-fix
                mode, compiled = auto_fix.auto_fix_pattern(pat)
                if mode == 'regex' and compiled:
                    compiled_map[name].append(('regex', compiled, pat, flags))
                elif mode == 'substr' and compiled:
                    compiled_map[name].append(('substr', compiled, pat, flags))
                else:
                    # nothing usable - skip
                    pass
    # now run compiled_map over data
    results_dir = out_dir / "regex_results"
    any_found = False
    for name, items in compiled_map.items():
        matches = []
        for mode, obj, orig, flags in items:
            if mode == 'regex':
                try:
                    found = obj.findall(data)
                except Exception:
                    found = []
                for f in found:
                    if isinstance(f, tuple):
                        sel = next((x for x in f if x), None)
                        if sel:
                            matches.append(str(sel))
                    else:
                        matches.append(str(f))
            elif mode == 'substr':
                for tok in obj:
                    if tok and tok in data:
                        matches.append(tok)
        cleaned = sorted({m.strip() for m in matches if m and str(m).strip()})
        if cleaned:
            any_found = True
            results_dir.mkdir(parents=True, exist_ok=True)
            out_file = results_dir / f"{name}.txt"
            with open(out_file, "w", encoding="utf-8", errors="ignore") as fh:
                fh.write("# source_gf_file: " + name + "\n")
                for mode, obj, orig, flags in items:
                    fh.write(f"# mode={mode} flags={flags} original={orig}\n")
                fh.write("\n")
                fh.write("\n".join(cleaned))
            if not silent:
                print(Color.GREEN(f"[+] {name} -> {len(cleaned)} matches"))
    if not any_found and not silent:
        print(Color.RED("[-] No gf matches found"))
