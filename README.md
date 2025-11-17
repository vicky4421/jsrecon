# Requirements
- To run the script you must need 'gf' tool to be installed.(https://github.com/tomnomnom/gf)
- The patterns are taken from the gf tools
# How to Run
- python3 js-recon-initial.py
- curl -s | python3 js-recon-initial.py
- Required File: GF Dump  
``` ~/.gf/gf_patterns_dump.txt ```
- Generate it once:
```
cd ~/.gf
rm -f ~/gf_patterns_dump.txt

for f in *.json; do
  echo "###FILE: $f" >> ~/gf_patterns_dump.txt
  cat "$f" >> ~/gf_patterns_dump.txt
  echo "" >> ~/gf_patterns_dump.txt
done
```
jsrecon will auto-detect it from:

- --dump path

- ./gf_patterns_dump.txt

- ~/.gf/gf_patterns_dump.txt

# Usage Examples
### Basic
```
python3 jsrecon/main.py script.js
```
### Pipe remote JS via curl
```
curl -s https://cdn.com/main.js | python3 jsrecon/main.py https://cdn.com/main.js
```
### Use only selected modules
```
python3 jsrecon/main.py app.js --modules gf,urls,graphql
```
### Disable safe splitting (raw JS)
```
python3 jsrecon/main.py app.js --no-split
```
### Specify dump location manually
```
python3 jsrecon/main.py app.js --dump /custom/path/gf_dump.txt
```
# Modules Available
| Module    | Description                                    |
| --------- | ---------------------------------------------- |
| `gf`      | GF++ engine, PCRE auto-fix, substring fallback |
| `entropy` | Shannon entropy secret detection               |
| `urls`    | HTTP/HTTPS URLs, relative API endpoints        |
| `domains` | Extract domain names from URLs                 |
| `graphql` | GQL queries, mutations, fragments              |
| `sinks`   | DOM sinks (XSS vectors)                        |
| `secrets` | Unprefixed API key detection                   |
| `all`     | Run everything (default)                       |
# Output Structure
```
js_recon_output/
└─ <filename>/
    ├─ readable.js
    └─ regex_results/
         ├─ gf pattern outputs...
         ├─ urls.txt
         ├─ endpoints.txt
         ├─ domains.txt
         ├─ graphql_queries.txt
         ├─ entropy_secrets.txt
         ├─ unprefixed_api_keys.txt
         ├─ js_sinks_advanced.txt
         └─ ...more files depending on modules
```
