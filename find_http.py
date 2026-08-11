import re

with open('main.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Let's search for HTTP calls (get/post) that format query parameters
http_calls = re.findall(r'\.get\([^\)]+\)|\.post\([^\)]+\)', text)
print(f"Total http calls found: {len(http_calls)}")
for c in http_calls:
    if any(k in c for k in ['search', 'edital', 'contrata', 'pncp', 'v1', 'q=']):
        print(c[:200])
