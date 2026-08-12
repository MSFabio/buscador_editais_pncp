import json

with open(r'C:\Users\11429149760\.gemini\antigravity\scratch\cybersecurity_results.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

term_counts = {}
uf_counts = {}
for i in items:
    for t in i.get('matched_terms', []):
        term_counts[t] = term_counts.get(t, 0) + 1
    uf = i.get('uf') or 'DF'
    uf_counts[uf] = uf_counts.get(uf, 0) + 1

print("=== DISTRIBUIÇÃO POR TERMO DE BUSCA ===")
for t, c in sorted(term_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"- {t}: {c} editais abertos")

print("\n=== DISTRIBUIÇÃO POR UF (TOP 10 ESTADOS) ===")
for u, c in sorted(uf_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
    print(f"- {u}: {c} editais")

pregao_items = [i for i in items if 'pregão' in (i.get('modalidade') or '').lower() or 'pregao' in (i.get('modalidade') or '').lower()]

print(f"\n=== AMOSTRA DE PREGÕES ELETRÔNICOS (TOTAL: {len(pregao_items)}) ===")
for idx, item in enumerate(pregao_items[:5], 1):
    print(f"{idx}. {item.get('title')} | {item.get('orgao')} ({item.get('uf')})")
    print(f"   Sessão Pública: {item.get('data_encerramento_proposta')}")
    print(f"   Termos: {item.get('matched_terms')}")
    print(f"   Objeto: {(item.get('objeto') or '')[:140]}...")
    print(f"   Link: {item.get('link_pncp')}")
    print('-'*50)
