import json
import datetime

json_file = r'C:\Users\11429149760\.gemini\antigravity\scratch\expanded_25pages_results.json'

with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

all_items = data.get('all_brazil', [])
ba_items = data.get('bahia', [])

def fmt_date(dt_str):
    if not dt_str:
        return "Não informada"
    try:
        clean = dt_str.split('.')[0]
        if 'T' in clean:
            dt = datetime.datetime.strptime(clean, "%Y-%m-%dT%H:%M:%S")
            return dt.strftime("%d/%m/%Y às %H:%M")
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

# Generate Bahia Report
ba_artifact = r'C:\Users\11429149760\.gemini\antigravity\brain\001766fb-0fab-4892-bf1e-723cc736a97c\editais_pncp_25paginas_bahia.md'

ba_pregao = [i for i in ba_items if 'pregão' in (i.get('modalidade') or '').lower() or 'pregao' in (i.get('modalidade') or '').lower()]
ba_outros = [i for i in ba_items if i not in ba_pregao]

lines_ba = []
lines_ba.append("# 📍 Editais Abertos PNCP - Bahia (BA) [Busca Expandida - 25 Páginas]")
lines_ba.append(f"**Data da Busca:** 06/08/2026  ")
lines_ba.append(f"**Profundidade de Pesquisa:** 25 páginas por palavra-chave  ")
lines_ba.append(f"**Termos Pesquisados:** Buffet, Buffet para eventos, Buffet para cerimônias, Catering, Alimentação, Alimentação para eventos, Coffee Break, Lanches  ")
lines_ba.append(f"**Total de Editais Encontrados na Bahia:** `{len(ba_items)}` editais  ")
lines_ba.append(f"**Editais na Modalidade Pregão na Bahia:** `{len(ba_pregao)}` editais  \n")

lines_ba.append("> [!NOTE]")
lines_ba.append("> Esta busca aprofundada percorreu 25 páginas por termo de busca, identificando todas as oportunidades abertas na Bahia com sessão pública a ser realizada a partir de 06/08/2026.\n")

lines_ba.append("## ⚡ Editais na Modalidade Pregão na Bahia (BA)\n")

for idx, item in enumerate(ba_pregao, 1):
    orgao = item.get('orgao') or 'Não informado'
    unidade = item.get('unidade') or ''
    muni = item.get('municipio') or 'Bahia'
    title = item.get('title') or f"Edital {item.get('control_num')}"
    modalidade = item.get('modalidade') or 'Pregão Eletrônico'
    objeto = (item.get('objeto') or 'Sem descrição.').strip()
    val = fmt_currency(item.get('valor_estimado'))
    dt_pub = fmt_date(item.get('data_publicacao'))
    dt_abert = fmt_date(item.get('data_abertura_proposta'))
    dt_enc = fmt_date(item.get('data_encerramento_proposta'))
    terms_str = ", ".join([f"`{t}`" for t in item.get('matched_terms', [])])
    link_pncp = item.get('link_pncp')
    link_origem = item.get('link_origem')

    lines_ba.append(f"### {idx}. {title} — {orgao}")
    lines_ba.append(f"- **Órgão:** {orgao}")
    if unidade and unidade != orgao:
        lines_ba.append(f"- **Unidade:** {unidade}")
    lines_ba.append(f"- **Município / UF:** {muni} - BA")
    lines_ba.append(f"- **Modalidade:** **{modalidade}**")
    lines_ba.append(f"- **Termos Relacionados:** {terms_str}")
    lines_ba.append(f"- **Valor Estimado:** `{val}`")
    lines_ba.append(f"- **Data de Publicação:** {dt_pub}")
    lines_ba.append(f"- **Abertura de Propostas:** {dt_abert}")
    lines_ba.append(f"- **Encerramento / Sessão Pública:** **{dt_enc}**")
    lines_ba.append(f"- **Objeto:** {objeto}")
    links_md = []
    if link_pncp:
        links_md.append(f"[🔗 Ver no PNCP]({link_pncp})")
    if link_origem:
        links_md.append(f"[🌐 Sistema de Origem]({link_origem})")
    lines_ba.append(f"- **Links:** {' | '.join(links_md)}")
    lines_ba.append("\n---\n")

lines_ba.append("## 📜 Demais Editais Abertos na Bahia (Credenciamento, Dispensa e Outras)\n")

for idx, item in enumerate(ba_outros, 1):
    orgao = item.get('orgao') or 'Não informado'
    unidade = item.get('unidade') or ''
    muni = item.get('municipio') or 'Bahia'
    title = item.get('title') or f"Edital {item.get('control_num')}"
    modalidade = item.get('modalidade') or 'Credenciamento / Dispensa'
    objeto = (item.get('objeto') or 'Sem descrição.').strip()
    val = fmt_currency(item.get('valor_estimado'))
    dt_pub = fmt_date(item.get('data_publicacao'))
    dt_abert = fmt_date(item.get('data_abertura_proposta'))
    dt_enc = fmt_date(item.get('data_encerramento_proposta'))
    terms_str = ", ".join([f"`{t}`" for t in item.get('matched_terms', [])])
    link_pncp = item.get('link_pncp')
    link_origem = item.get('link_origem')

    lines_ba.append(f"### {idx}. {title} — {orgao}")
    lines_ba.append(f"- **Órgão:** {orgao}")
    if unidade and unidade != orgao:
        lines_ba.append(f"- **Unidade:** {unidade}")
    lines_ba.append(f"- **Município / UF:** {muni} - BA")
    lines_ba.append(f"- **Modalidade:** `{modalidade}`")
    lines_ba.append(f"- **Termos Relacionados:** {terms_str}")
    lines_ba.append(f"- **Valor Estimado:** `{val}`")
    lines_ba.append(f"- **Data de Publicação:** {dt_pub}")
    lines_ba.append(f"- **Abertura de Propostas:** {dt_abert}")
    lines_ba.append(f"- **Encerramento / Sessão Pública:** **{dt_enc}**")
    lines_ba.append(f"- **Objeto:** {objeto}")
    links_md = []
    if link_pncp:
        links_md.append(f"[🔗 Ver no PNCP]({link_pncp})")
    if link_origem:
        links_md.append(f"[🌐 Sistema de Origem]({link_origem})")
    lines_ba.append(f"- **Links:** {' | '.join(links_md)}")
    lines_ba.append("\n---\n")

with open(ba_artifact, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines_ba))

print(f"Generated Bahia report: {ba_artifact}")

# Generate Brazil Report
br_artifact = r'C:\Users\11429149760\.gemini\antigravity\brain\001766fb-0fab-4892-bf1e-723cc736a97c\editais_pncp_25paginas_brasil.md'

term_counts = {}
uf_counts = {}
mod_counts = {}
for item in all_items:
    for t in item.get('matched_terms', []):
        term_counts[t] = term_counts.get(t, 0) + 1
    uf = item.get('uf') or 'Outros'
    uf_counts[uf] = uf_counts.get(uf, 0) + 1
    mod = item.get('modalidade') or 'Outras'
    mod_counts[mod] = mod_counts.get(mod, 0) + 1

lines_br = []
lines_br.append("# 📋 Editais Abertos PNCP - Brasil (Busca Expandida 25 Páginas)")
lines_br.append(f"**Data da Pesquisa:** 06/08/2026  ")
lines_br.append(f"**Profundidade:** 25 páginas por termo de busca  ")
lines_br.append(f"**Termos Pesquisados (8):** Buffet, Buffet para eventos, Buffet para cerimônias, Catering, Alimentação, Alimentação para eventos, Coffee Break, Lanches  ")
lines_br.append(f"**Total de Editais Únicos no Brasil:** `{len(all_items)}` editais  \n")

lines_br.append("## 📊 Resumo Executivo Nacional\n")

lines_br.append("### Distribuição por Palavras-Chave")
lines_br.append("| Palavra-Chave | Qtd Editais Encontrados |")
lines_br.append("| :--- | :---: |")
for term, count in sorted(term_counts.items(), key=lambda x: x[1], reverse=True):
    lines_br.append(f"| **{term}** | `{count}` |")
lines_br.append("")

lines_br.append("### Distribuição por Modalidade de Licitação")
lines_br.append("| Modalidade | Qtd Editais |")
lines_br.append("| :--- | :---: |")
for mod, count in sorted(mod_counts.items(), key=lambda x: x[1], reverse=True):
    lines_br.append(f"| **{mod}** | `{count}` |")
lines_br.append("")

lines_br.append("### Distribuição por UF")
lines_br.append("| UF | Qtd | UF | Qtd | UF | Qtd |")
lines_br.append("| :---: | :---: | :---: | :---: | :---: | :---: |")
sorted_ufs = sorted(uf_counts.items(), key=lambda x: x[1], reverse=True)
for i in range(0, len(sorted_ufs), 3):
    row = []
    for j in range(3):
        if i + j < len(sorted_ufs):
            u, c = sorted_ufs[i+j]
            row.append(f"**{u}** | `{c}`")
        else:
            row.append("- | -")
    lines_br.append(f"| {' | '.join(row)} |")

lines_br.append("\n---\n")

lines_br.append("## 📜 Amostra Selecionada de Editais de Pregão Eletrônico (Brasil)\n")

br_pregao = [i for i in all_items if 'pregão' in (i.get('modalidade') or '').lower() or 'pregao' in (i.get('modalidade') or '').lower()]
lines_br.append(f"Total de Pregões no Brasil nesta amostragem: `{len(br_pregao)}` editais.\n")

for idx, item in enumerate(br_pregao[:50], 1):
    orgao = item.get('orgao') or 'Não informado'
    uf = item.get('uf') or ''
    muni = item.get('municipio') or ''
    title = item.get('title') or f"Edital {item.get('control_num')}"
    modalidade = item.get('modalidade') or 'Pregão Eletrônico'
    dt_enc = fmt_date(item.get('data_encerramento_proposta'))
    link_pncp = item.get('link_pncp')
    terms_str = ", ".join([f"`{t}`" for t in item.get('matched_terms', [])])
    
    lines_br.append(f"### {idx}. [{title}]({link_pncp}) — {orgao} ({muni}/{uf})")
    lines_br.append(f"- **Modalidade:** `{modalidade}` | **Sessão Pública:** **{dt_enc}**")
    lines_br.append(f"- **Termos:** {terms_str}")
    lines_br.append(f"- **Objeto:** {(item.get('objeto') or '')[:200]}...")
    lines_br.append("")

with open(br_artifact, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines_br))

print(f"Generated Brazil report: {br_artifact}")
