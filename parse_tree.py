import sys, json, re
sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\11429149760\.gemini\antigravity\brain\39837c6c-21ca-4f11-8996-c4b3a6b82e98\.system_generated\steps\63\output.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

if '```json' in text:
    json_str = text.split('```json')[1].split('```')[0].strip()
    data = json.loads(json_str)
    for idx, item in enumerate(data, 1):
        href = item.get('href', '')
        m = re.search(r'id_documento=(\d+)', href)
        doc_id = m.group(1) if m else 'N/A'
        print(f"{idx:2d}. {item.get('text')} | id_documento={doc_id} | href={href}")
