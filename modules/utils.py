# utility helpers
import re
from urllib.parse import urlparse
from pathlib import Path

def extract_filename_from_url(url):
    try:
        path = urlparse(url).path
        name = Path(path).name
        if name and "." in name:
            return name
    except:
        pass
    return None

def safe_split(txt: str) -> str:
    """
    Insert safe newlines to break minified JS into smaller lines for regex scanning.
    This does NOT change program semantics; it only inserts '\n' at statement boundaries.
    """
    s = txt
    s = s.replace(";", ";\n")
    s = s.replace("{", "{\n")
    s = s.replace("}", "}\n")
    s = s.replace("),", "),\n")
    s = s.replace("],", "],\n")
    # create boundaries before keywords
    for tok in ["return ", "const ", "let ", "var ", "function ", "class ", "import ", "export "]:
        s = s.replace(tok, "\n" + tok.strip() + " ")
    # collapse multiple blank lines
    s = re.sub(r'\n{2,}', '\n', s)
    return s
