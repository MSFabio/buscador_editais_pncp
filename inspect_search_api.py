import os
import requests
import re

local_js = 'main.js'

if not os.path.exists(local_js):
    url = 'https://pncp.gov.br/app/main.e91144c7c56704ef.js'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }
    s = requests.Session()
    r = s.get(url, headers=headers, stream=True, timeout=30)
    with open(local_js, 'wb') as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Downloaded main.js")

with open(local_js, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

print("File size:", len(text))

# Let's search for keywords like 'proposta', 'editais', 'v1/search', 'v1/contratacoes', 'q='
keywords = ['proposta', 'search', 'editais', 'contratacoes']
for kw in keywords:
    matches = [m.start() for m in re.finditer(kw, text)]
    print(f"Keyword '{kw}' found {len(matches)} times.")

# Find all HTTP GET endpoints constructed in the code
endpoints = set(re.findall(r'["\'](?:https?://[^"\']+|/[a-zA-Z0-9\-_/]+)["\']', text))
interesting = [e for e in endpoints if any(k in e for k in ['pncp', 'contratac', 'search', 'edital', 'proposta', 'consulta'])]
print("\nInteresting Endpoints Found:")
for e in sorted(interesting)[:30]:
    print(e)
