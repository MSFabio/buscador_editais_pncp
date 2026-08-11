import json
import datetime
import os

json_file = r'C:\Users\11429149760\.gemini\antigravity\scratch\pncp_results.json'
artifact_file = r'C:\Users\11429149760\.gemini\antigravity\brain\001766fb-0fab-4892-bf1e-723cc736a97c\editais_pncp_abertos.md'

with open(json_file, 'r', encoding='utf-8') as f:
    items = json.load(f)

def fmt_date(dt_str):
    if not dt_str:
        return "Não informada"
    try:
        clean = dt_str.split('.')[0]
        if 'T' in clean:
            dt = datetime.datetime.strptime(clean, "%Y-%m-%dT%H:%M:%S")
            return dt.strftime("%d/%m/%Y às %H:%H")
        else:
            dt = datetime.datetime.strptime(clean, "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
    except Exception:
        return dt_str

def fmt_currency(val):
    if val is None or val == 0:
        return "Não informado / Sigiloso"
    try:
        val_f = float(val)
        return f"R$ {val_f:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(val)

# Stats
total_items = len(items)

term_counts = {}
uf_counts = {}
for item in items:
    for t in item.get('matched_terms', []):
        term_counts[t] = term_counts.get(t, 0) + 1
    uf = item.get('uf') or 'Outros'
    uf_counts[uf] = uf_counts.get(uf, 0) + 1

lines = []
lines.append("# 📋 Editais Abertos PNCP - Serviços de Buffet e Alimentação")
lines.append(f"**Data da Pesquisa:** 06/08/2026  ")
lines.append(f"**Fonte de Dados:** Portal Nacional de Contratações Públicas (https://pncp.gov.br/app/editais)  ")
lines.append(f"**Filtro Aplicado:** Editais Abertos / Recebendo Propostas com Sessão Pública / Encerramento em Datas Futuras  ")
lines.append(f"**Total de Editais Encontrados:** `{total_items}` editais únicos\n")

lines.append("> [!NOTE]")
lines.append("> Todos os editais listados abaixo possuem prazo de recebimento de propostas ou sessão pública aberta para datas futuras a partir de hoje (06/08/2026).\n")

lines.append("## 📊 Resumo Executivo\n")

lines.append("### Distribuição por Termos de Busca")
lines.append("| Termo de Busca | Editais Encontrados |")
lines.append("| :--- | :---: |")
for term, count in sorted(term_counts.items(), key=lambda x: x[1], reverse=True):
    lines.append(f"| **{term}** | `{count}` |")
lines.append("")

lines.append("### Distribuição Geográfica (UF)")
lines.append("| UF | Qtd Editais | UF | Qtd Editais |")
lines.append("| :---: | :---: | :---: | :---: |")
sorted_ufs = sorted(uf_counts.items(), key=lambda x: x[1], reverse=True)
for i in range(0, len(sorted_ufs), 2):
    uf1, c1 = sorted_ufs[i]
    if i + 1 < len(sorted_ufs):
        uf2, c2 = sorted_ufs[i+1]
        lines.append(f"| **{uf1}** | `{c1}` | **{uf2}** | `{c2}` |")
    else:
        lines.append(f"| **{uf1}** | `{c1}` | - | - |")
lines.append("\n---\n")

lines.append("## 📜 Lista Completa de Editais Abertos\n")

for idx, item in enumerate(items, 1):
    orgao = item.get('orgao') or 'Não informado'
    unidade = item.get('unidade') or ''
    uf = item.get('uf') or ''
    muni = item.get('municipio') or ''
    loc = f"{muni} - {uf}" if muni and uf else (uf or muni or "Brasil")
    
    title = item.get('title') or f"Edital {item.get('control_num')}"
    modalidade = item.get('modalidade') or 'Pregão / Concorrência'
    objeto = (item.get('objeto') or 'Sem descrição do objeto.').strip()
    
    val = fmt_currency(item.get('valor_estimado'))
    dt_pub = fmt_date(item.get('data_publicacao'))
    dt_abert = fmt_date(item.get('data_abertura_proposta'))
    dt_enc = fmt_date(item.get('data_encerramento_proposta'))
    
    terms_str = ", ".join([f"`{t}`" for t in item.get('matched_terms', [])])
    
    link_pncp = item.get('link_pncp')
    link_origem = item.get('link_origem')
    
    lines.append(f"### {idx}. {title} — {orgao} ({uf})")
    lines.append(f"- **Órgão / Entidade:** {orgao}")
    if unidade and unidade != orgao:
        lines.append(f"- **Unidade:** {unidade}")
    lines.append(f"- **Localização:** {loc}")
    lines.append(f"- **Modalidade:** {modalidade}")
    lines.append(f"- **Termos Relacionados:** {terms_str}")
    lines.append(f"- **Valor Estimado:** `{val}`")
    lines.append(f"- **Data de Publicação:** {dt_pub}")
    lines.append(f"- **Abertura das Propostas:** {dt_abert}")
    lines.append(f"- **Encerramento / Sessão Pública:** **{dt_enc}**")
    lines.append(f"- **Objeto:** {objeto}")
    
    links_md = []
    if link_pncp:
        links_md.append(f"[🔗 Ver no PNCP]({link_pncp})")
    if link_origem:
        links_md.append(f"[🌐 Acessar Sistema de Origem]({link_origem})")
    
    lines.append(f"- **Links:** {' | '.join(links_md)}")
    lines.append("\n---\n")

report_content = "\n".join(lines)

with open(artifact_file, 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"Report generated successfully at {artifact_file}")
