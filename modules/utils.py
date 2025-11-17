# utility helpers
import re
from urllib.parse import urlparse
from pathlib import Path

class Color:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"

    @staticmethod
    def red(t): return f"{Color.RED}{t}{Color.RESET}"
    @staticmethod
    def green(t): return f"{Color.GREEN}{t}{Color.RESET}"
    @staticmethod
    def yellow(t): return f"{Color.YELLOW}{t}{Color.RESET}"
    @staticmethod
    def blue(t): return f"{Color.BLUE}{t}{Color.RESET}"


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
