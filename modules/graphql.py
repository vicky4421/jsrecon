"""
Simple GraphQL extractor:
- finds `gql` template strings, `query` / `mutation` strings and inline docstrings
"""
import re
from pathlib import Path

def run_graphql(data: str, out_dir: Path, silent=False):
    queries = set()
    # gql`...` template literals
    for m in re.finditer(r'gql`([\s\S]{10,3000}?)`', data):
        queries.add(m.group(1).strip())
    # fetch('...graphql', { body: `query ...` })
    for m in re.finditer(r'(["\'`])((query|mutation)\s+[^{]+{[\s\S]{4,2000}?})\1', data, flags=re.IGNORECASE):
        queries.add(m.group(2).strip())
    # generic: look for "query { ... }" single-line or multi-line
    for m in re.finditer(r'(query|mutation|fragment)\s+[^{]*\{[\s\S]{10,4000}?\}', data, flags=re.IGNORECASE):
        queries.add(m.group(0).strip())
    if queries:
        out = out_dir / "regex_results" / "graphql_queries.txt"
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            for q in queries:
                fh.write(q + "\n\n---\n\n")
        if not silent:
            print(f"[+] graphql_queries -> {len(queries)} found")
    else:
        if not silent:
            print("[-] No graphql queries found")
