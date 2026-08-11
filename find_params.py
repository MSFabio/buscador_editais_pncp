import re

with open('main.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

pos = 0
while True:
    idx = text.find('tipos_documento', pos)
    if idx == -1:
        break
    print(f"=== Match at {idx} ===")
    print(text[max(0, idx-300):min(len(text), idx+500)])
    pos = idx + 1
