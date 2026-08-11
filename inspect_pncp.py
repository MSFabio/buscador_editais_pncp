import requests
import re

url = 'https://pncp.gov.br/app/main.e91144c7c56704ef.js'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

r = requests.get(url, headers=headers, timeout=15)
print('Status:', r.status_code, 'len:', len(r.text))

# Look for search endpoints in JS
print("\n--- Matching /api/ or /pncp ---")
matches = set(re.findall(r'https?://[a-zA-Z0-9\.\-\/]+|/(?:pncp-|api/|v1/)[a-zA-Z0-9\-_/]+', r.text))
for m in sorted(matches):
    if any(k in m.lower() for k in ['search', 'edital', 'contrata', 'proposta', 'publicac']):
        print(m)

print("\n--- Searching for query params / endpoints ---")
for line in r.text.split(';'):
    if 'contratacoes' in line or 'editais' in line or 'proposta' in line:
        if len(line) < 300:
            print(line)
