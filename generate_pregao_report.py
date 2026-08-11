import json
import datetime

json_file = r'C:\Users\11429149760\.gemini\antigravity\scratch\ba_pregao_search.json'
artifact_file = r'C:\Users\11429149760\.gemini\antigravity\brain\001766fb-0fab-4892-bf1e-723cc736a97c\editais_pregao_eletronico_bahia.md'

with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

pregao_items = data.get('pregao_eletronico', [])
all_ba_items = data.get('todos_ba', [])

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

lines = []
lines.append("# ⚡ Editais Abertos de Pregão Eletrônico - Bahia (BA)")
lines.append(f"**Data da Busca Aprofundada:** 06/08/2026  ")
lines.append(f"**Escopo:** Estado da Bahia (BA) | Modalidade: Pregão Eletrônico | Status: Editais Abertos com Sessão Pública Futura  ")
lines.append(f"**Resultados Encontrados em Pregão Eletrônico:** `{len(pregao_items)}` editais  ")
lines.append(f"**Total de Oportunidades Mapeadas na BA (Todas Modalidades):** `{len(all_ba_items)}` editais\n")

lines.append("> [!NOTE]")
lines.append("> Foi realizada uma varredura aprofundada no PNCP até 9 páginas por palavra-chave para localizar especificamente editais na modalidade **Pregão Eletrônico** na Bahia.\n")

lines.append("## 📌 Editais em Pregão Eletrônico na Bahia\n")

if not pregao_items:
    lines.append("_Nenhum edital aberto na modalidade Pregão Eletrônico especificamente foi encontrado para estas palavras-chave no momento._\n")
else:
    for idx, item in enumerate(pregao_items, 1):
        orgao = item.get('orgao') or 'Não informado'
        unidade = item.get('unidade') or ''
        muni = item.get('municipio') or 'Bahia'
        loc = f"{muni} - BA"
        
        title = item.get('title') or f"Edital {item.get('control_num')}"
        modalidade = item.get('modalidade') or 'Pregão Eletrônico'
        objeto = (item.get('objeto') or 'Sem descrição do objeto.').strip()
        
        val = fmt_currency(item.get('valor_estimado'))
        dt_pub = fmt_date(item.get('data_publicacao'))
        dt_abert = fmt_date(item.get('data_abertura_proposta'))
        dt_enc = fmt_date(item.get('data_encerramento_proposta'))
        
        terms_str = ", ".join([f"`{t}`" for t in item.get('matched_terms', [])])
        
        link_pncp = item.get('link_pncp')
        link_origem = item.get('link_origem')
        
        lines.append(f"### {idx}. {title} — {orgao}")
        lines.append(f"- **Órgão / Entidade:** {orgao}")
        if unidade and unidade != orgao:
            lines.append(f"- **Unidade:** {unidade}")
        lines.append(f"- **Município / UF:** {loc}")
        lines.append(f"- **Modalidade:** **{modalidade}**")
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

lines.append("## 📊 Distribuição Completa por Modalidade na Bahia (BA)\n")
modalidade_counts = {}
for item in all_ba_items:
    mod = item.get('modalidade') or 'Outras / Não especificada'
    modalidade_counts[mod] = modalidade_counts.get(mod, 0) + 1

lines.append("| Modalidade de Licitação | Qtd Editais Abertos |")
lines.append("| :--- | :---: |")
for mod, count in sorted(modalidade_counts.items(), key=lambda x: x[1], reverse=True):
    lines.append(f"| **{mod}** | `{count}` |")

lines.append("\n---\n")

lines.append("## 📜 Panorama Geral de Todas as Oportunidades na Bahia\n")

for idx, item in enumerate(all_ba_items, 1):
    orgao = item.get('orgao') or 'Não informado'
    muni = item.get('municipio') or 'Bahia'
    title = item.get('title') or f"Edital {item.get('control_num')}"
    modalidade = item.get('modalidade') or 'Não informada'
    dt_enc = fmt_date(item.get('data_encerramento_proposta'))
    link_pncp = item.get('link_pncp')
    
    lines.append(f"{idx}. **[{title}]({link_pncp})** — {orgao} ({muni}/BA)")
    lines.append(f"   - **Modalidade:** `{modalidade}` | **Sessão Pública:** **{dt_enc}**")
    lines.append(f"   - **Objeto:** {(item.get('objeto') or '')[:180]}...")

report_content = "\n".join(lines)

with open(artifact_file, 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"Pregão report generated at {artifact_file}")
