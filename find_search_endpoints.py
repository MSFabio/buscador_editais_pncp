import re

with open('main.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Look for string templates or query parameter names in the angular service
for m in re.finditer(r'(/api/search/[a-zA-Z0-9\-_/]+|/api/search\?[a-zA-Z0-9\-_/=&]+|/api/search)', text):
    start = max(0, m.start() - 150)
    end = min(len(text), m.end() + 250)
    print("Match:", text[start:end])
    print("="*60)
