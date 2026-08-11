import json

with open(r'C:\Users\11429149760\.gemini\antigravity\scratch\new_keywords_results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

ba_items = data.get('bahia', [])
print(f"Total BA: {len(ba_items)}")
for idx, item in enumerate(ba_items, 1):
    print(f"{idx}. {item.get('title')} | {item.get('orgao')} ({item.get('municipio')})")
    print(f"   Modalidade: {item.get('modalidade')} | Encerramento: {item.get('data_encerramento_proposta')}")
    print(f"   Termos: {item.get('matched_terms')}")
    print(f"   Objeto: {(item.get('objeto') or '')[:140]}...")
    print('-'*50)
