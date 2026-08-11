import re

with open('main.js', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Let's find how searchURL or search parameters are built in Angular services
matches = [m.start() for m in re.finditer(r'searchURL', text)]
print(f"searchURL occurrences: {len(matches)}")
for idx in matches:
    print(f"=== match at {idx} ===")
    print(text[max(0, idx-200):min(len(text), idx+300)])

# Let's find all occurrences of '/v1/'
matches_v1 = [m.start() for m in re.finditer(r'/v1/', text)]
print(f"\n/v1/ occurrences: {len(matches_v1)}")
v1_strings = set()
for idx in matches_v1:
    s = text[max(0, idx-50):min(len(text), idx+100)]
    # find quotation marks around /v1/
    q_matches = re.findall(r'["\'][^"\']*/v1/[^"\']*["\']', s)
    for qm in q_matches:
        v1_strings.add(qm)

for v in sorted(v1_strings):
    print("v1 string:", v)
