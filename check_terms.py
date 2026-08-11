import json

json_file = r'C:\Users\11429149760\.gemini\antigravity\scratch\pncp_results.json'

with open(json_file, 'r', encoding='utf-8') as f:
    items = json.load(f)

terms = [
    'Buffet',
    'Buffet para eventos',
    'Buffet para cerimônias',
    'Catering',
    'Alimentação',
    'Alimentação para eventos'
]

print("=== TOTAL EDITAIS POR PALAVRA-CHAVE (BRASIL) ===")
for t in terms:
    count = sum(1 for item in items if t in item.get('matched_terms', []))
    print(f'- "{t}": {count} editais abertos')

print("\n=== EDITAIS POR PALAVRA-CHAVE (APENAS BAHIA) ===")
ba_items = [i for i in items if i.get('uf') == 'BA']
for t in terms:
    count = sum(1 for item in ba_items if t in item.get('matched_terms', []))
    print(f'- "{t}": {count} editais abertos na Bahia')
