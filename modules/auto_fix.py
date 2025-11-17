"""
Auto-fix heuristics for PCRE -> Python regex. Returns either compiled regex or substring tokens.
"""
import re

def try_compile(pat, flags=0):
    try:
        return re.compile(pat, flags)
    except re.error:
        return None

def auto_fix_pattern(pat_orig):
    """
    Attempt several safe transforms to make pattern Python-compileable.
    Returns: ('regex', compiled_re) or ('substr', [tokens])
    """
    pat = pat_orig

    # strip regex delimiters /.../
    if pat.startswith("/") and pat.endswith("/") and len(pat) > 2:
        pat = pat[1:-1]

    # unescape escaped slashes
    pat = pat.replace(r"\/", "/")

    # remove inline PCRE flags like (?i) / (?-i)
    pat = re.sub(r'\(\?[imsx-]+\)', '', pat)
    pat = re.sub(r'\(\?[:=!<>].*?\)', '', pat)  # basic removal of lookaround tokens

    # remove comment tokens (?#...)
    pat = re.sub(r'\(\?\#.*?\)', '', pat)

    # close unbalanced char-classes
    open_cls = pat.count('[') - pat.count(']')
    if open_cls > 0:
        pat += ']' * open_cls

    # balance parentheses naively
    paren_diff = pat.count('(') - pat.count(')')
    if paren_diff > 0:
        pat += ')' * paren_diff

    # remove some PCRE constructs Python doesn't support
    pat = pat.replace('(?>', '(')
    pat = re.sub(r'\\g<[^>]+>', '', pat)
    pat = pat.replace('\\Q', '').replace('\\E', '')

    # try compile
    cre = try_compile(pat)
    if cre:
        return ('regex', cre)

    # try escape and compile as literal
    try:
        cre = try_compile(re.escape(pat))
        if cre:
            return ('regex', cre)
    except Exception:
        pass

    # fallback: extract alnum tokens of length >=4 to use as substring tokens (longer first)
    tokens = re.findall(r'[A-Za-z0-9/_\.\-]{4,}', pat_orig)
    tokens = sorted(set(tokens), key=lambda x: -len(x))
    if tokens:
        return ('substr', tokens)

    # last resort: short tokens >=3
    tokens2 = re.findall(r'[A-Za-z0-9]{3,}', pat_orig)
    tokens2 = sorted(set(tokens2), key=lambda x: -len(x))
    return ('substr', tokens2)
