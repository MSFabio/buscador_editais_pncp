import re

with open('main.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Let's search for query string parameters like q= or pagina= or status=
for m in re.finditer(r'q\s*:\s*|q\s*=\s*|status\s*:\s*|status\s*=\s*|pagina\s*:\s*|tam\s*:\s*', text):
    idx = m.start()
    print(f"=== Match at {idx} ===")
    print(text[max(0, idx-100):min(len(text), idx+200)])
