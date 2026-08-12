import json
import datetime
import os
import subprocess

json_file = r'C:\Users\11429149760\.gemini\antigravity\scratch\cybersecurity_results.json'
md_file = r'C:\Users\11429149760\.gemini\antigravity\brain\001766fb-0fab-4892-bf1e-723cc736a97c\editais_pncp_ciberseguranca_brasil.md'
html_file = r'C:\Users\11429149760\.gemini\antigravity\scratch\editais_cybersecurity.html'
pdf_file = r'C:\Users\11429149760\.gemini\antigravity\brain\001766fb-0fab-4892-bf1e-723cc736a97c\editais_pncp_ciberseguranca_brasil.pdf'

with open(json_file, 'r', encoding='utf-8') as f:
    items = json.load(f)

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

pregao_items = [i for i in items if 'pregão' in (i.get('modalidade') or '').lower() or 'pregao' in (i.get('modalidade') or '').lower()]
outros_items = [i for i in items if i not in pregao_items]

term_counts = {}
uf_counts = {}
for i in items:
    for t in i.get('matched_terms', []):
        term_counts[t] = term_counts.get(t, 0) + 1
    uf = i.get('uf') or 'DF'
    uf_counts[uf] = uf_counts.get(uf, 0) + 1

# 1. BUILD FULL MARKDOWN REPORT (ALL 400 ITEMS)
lines_md = []
lines_md.append("# 🛡️ Relatório Completo PNCP - Cibersegurança, Firewall, NDR & ZTNA (Brasil)")
lines_md.append(f"**Data da Pesquisa:** 11/08/2026  ")
lines_md.append(f"**Profundidade:** 35 Páginas por Termo de Busca (Busca Nacional Completa)  ")
lines_md.append(f"**Termos Pesquisados (10):** Cibersegurança, Segurança da Informação, Firewall, NDR, ZTNA, Zero Trust, EDR, SIEM, Gestão de Vulnerabilidades, Segurança Cibernética  ")
lines_md.append(f"**Total de Editais Únicos Renderizados:** `{len(items)}` editais (100% dos resultados)  ")
lines_md.append(f"**Editais em Pregão Eletrônico:** `{len(pregao_items)}` editais  ")
lines_md.append(f"**Editais em Outras Modalidades:** `{len(outros_items)}` editais  \n")

lines_md.append("> [!NOTE]")
lines_md.append("> Este relatório contém **TODOS os 400 editais abertos** localizados na busca, com sessão pública ou prazo de proposta agendados a partir de 11/08/2026.\n")

lines_md.append("## 📊 Resumo Executivo Nacional\n")

lines_md.append("### Distribuição por Palavra-Chave")
lines_md.append("| Palavra-Chave | Qtd Editais Abertos |")
lines_md.append("| :--- | :---: |")
for term, count in sorted(term_counts.items(), key=lambda x: x[1], reverse=True):
    lines_md.append(f"| **{term}** | `{count}` |")
lines_md.append("")

lines_md.append("### Distribuição Geográfica (UFs)")
lines_md.append("| UF | Qtd | UF | Qtd | UF | Qtd |")
lines_md.append("| :---: | :---: | :---: | :---: | :---: | :---: |")
sorted_ufs = sorted(uf_counts.items(), key=lambda x: x[1], reverse=True)
for i in range(0, len(sorted_ufs), 3):
    row = []
    for j in range(3):
        if i + j < len(sorted_ufs):
            u, c = sorted_ufs[i+j]
            row.append(f"**{u}** | `{c}`")
        else:
            row.append("- | -")
    lines_md.append(f"| {' | '.join(row)} |")

lines_md.append("\n---\n")

lines_md.append(f"## ⚡ 1. Editais em Pregão Eletrônico/Presencial ({len(pregao_items)} editais)\n")

for idx, item in enumerate(pregao_items, 1):
    orgao = item.get('orgao') or 'Não informado'
    unidade = item.get('unidade') or ''
    uf = item.get('uf') or 'DF'
    muni = item.get('municipio') or uf
    loc = f"{muni} - {uf}"
    title = item.get('title') or f"Edital {item.get('control_num')}"
    modalidade = item.get('modalidade') or 'Pregão Eletrônico'
    objeto = (item.get('objeto') or 'Sem descrição.').strip()
    val = fmt_currency(item.get('valor_estimado'))
    dt_pub = fmt_date(item.get('data_publicacao'))
    dt_enc = fmt_date(item.get('data_encerramento_proposta'))
    terms_str = ", ".join([f"`{t}`" for t in item.get('matched_terms', [])])
    link_pncp = item.get('link_pncp')
    link_origem = item.get('link_origem')

    lines_md.append(f"### {idx}. {title} — {orgao} ({uf})")
    lines_md.append(f"- **Órgão / Entidade:** {orgao}")
    if unidade and unidade != orgao:
        lines_md.append(f"- **Unidade:** {unidade}")
    lines_md.append(f"- **Localização:** {loc}")
    lines_md.append(f"- **Modalidade:** **{modalidade}**")
    lines_md.append(f"- **Termos Relacionados:** {terms_str}")
    lines_md.append(f"- **Valor Estimado:** `{val}`")
    lines_md.append(f"- **Data de Publicação:** {dt_pub}")
    lines_md.append(f"- **Encerramento / Sessão Pública:** **{dt_enc}**")
    lines_md.append(f"- **Objeto:** {objeto}")
    links_arr = []
    if link_pncp:
        links_arr.append(f"[🔗 Ver no PNCP]({link_pncp})")
    if link_origem:
        links_arr.append(f"[🌐 Sistema de Origem]({link_origem})")
    lines_md.append(f"- **Links:** {' | '.join(links_arr)}")
    lines_md.append("\n---\n")

lines_md.append(f"## 📜 2. Demais Modalidades ({len(outros_items)} editais)\n")

for idx, item in enumerate(outros_items, 1):
    orgao = item.get('orgao') or 'Não informado'
    unidade = item.get('unidade') or ''
    uf = item.get('uf') or 'DF'
    muni = item.get('municipio') or uf
    loc = f"{muni} - {uf}"
    title = item.get('title') or f"Edital {item.get('control_num')}"
    modalidade = item.get('modalidade') or 'Concorrência / Credenciamento'
    objeto = (item.get('objeto') or 'Sem descrição.').strip()
    val = fmt_currency(item.get('valor_estimado'))
    dt_pub = fmt_date(item.get('data_publicacao'))
    dt_enc = fmt_date(item.get('data_encerramento_proposta'))
    terms_str = ", ".join([f"`{t}`" for t in item.get('matched_terms', [])])
    link_pncp = item.get('link_pncp')
    link_origem = item.get('link_origem')

    lines_md.append(f"### {idx}. {title} — {orgao} ({uf})")
    lines_md.append(f"- **Órgão / Entidade:** {orgao}")
    if unidade and unidade != orgao:
        lines_md.append(f"- **Unidade:** {unidade}")
    lines_md.append(f"- **Localização:** {loc}")
    lines_md.append(f"- **Modalidade:** `{modalidade}`")
    lines_md.append(f"- **Termos Relacionados:** {terms_str}")
    lines_md.append(f"- **Valor Estimado:** `{val}`")
    lines_md.append(f"- **Data de Publicação:** {dt_pub}")
    lines_md.append(f"- **Encerramento / Sessão Pública:** **{dt_enc}**")
    lines_md.append(f"- **Objeto:** {objeto}")
    links_arr = []
    if link_pncp:
        links_arr.append(f"[🔗 Ver no PNCP]({link_pncp})")
    if link_origem:
        links_arr.append(f"[🌐 Sistema de Origem]({link_origem})")
    lines_md.append(f"- **Links:** {' | '.join(links_arr)}")
    lines_md.append("\n---\n")

with open(md_file, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines_md))

print(f"Full Markdown generated: {len(items)} items at {md_file}")

# 2. BUILD FULL HTML DOCUMENT (ALL 400 ITEMS) FOR PDF
html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>PNCP - Todos os 400 Editais de Cibersegurança</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    @page {{ size: A4; margin: 10mm; }}
    body {{
        font-family: 'Inter', -apple-system, sans-serif;
        color: #0f172a; background: #ffffff; font-size: 11px; line-height: 1.4; margin: 0; padding: 0;
    }}
    header {{ border-bottom: 2px solid #0284c7; padding-bottom: 8px; margin-bottom: 12px; }}
    h1 {{ color: #0284c7; font-size: 18px; margin: 0 0 4px 0; font-weight: 700; }}
    .meta-bar {{ font-size: 10.5px; color: #475569; margin-bottom: 8px; }}
    .summary-box {{
        background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 6px;
        padding: 8px 12px; margin-bottom: 14px; display: flex; justify-content: space-around;
    }}
    .stat-item {{ text-align: center; }}
    .stat-val {{ font-size: 18px; font-weight: 700; color: #0369a1; }}
    .stat-lbl {{ font-size: 10.5px; color: #0369a1; font-weight: 500; }}
    h2 {{ font-size: 13px; color: #0f172a; border-left: 4px solid #0284c7; padding-left: 6px; margin: 16px 0 8px 0; font-weight: 700; }}
    .card {{
        background: #ffffff; border: 1px solid #cbd5e1; border-radius: 5px;
        padding: 8px 10px; margin-bottom: 8px; page-break-inside: avoid;
    }}
    .card.pregao {{ background: #f0fdf4; border-color: #86efac; }}
    .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px; }}
    .card-title {{ font-weight: 700; font-size: 11.5px; color: #0f172a; margin: 0; }}
    .badge {{ display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 9.5px; font-weight: 600; text-transform: uppercase; }}
    .badge-pregao {{ background: #16a34a; color: #ffffff; }}
    .badge-outros {{ background: #e2e8f0; color: #334155; }}
    .grid-info {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2px 10px; font-size: 10.5px; margin-bottom: 4px; }}
    .info-label {{ font-weight: 600; color: #475569; }}
    .enc-date {{ color: #dc2626; font-weight: 700; }}
    .objeto-text {{ font-size: 10.5px; color: #334155; background: rgba(255, 255, 255, 0.7); border: 1px solid #e2e8f0; padding: 4px 6px; border-radius: 3px; margin-top: 3px; }}
    .links-bar {{ margin-top: 4px; font-size: 10.5px; }}
    .links-bar a {{ color: #0284c7; text-decoration: none; font-weight: 500; margin-right: 10px; }}
</style>
</head>
<body>

<header>
    <h1>🛡️ PNCP - Catálogo Completo de Cibersegurança & TI (Brasil)</h1>
    <div class="meta-bar">
        <b>Data da Busca:</b> 11/08/2026 &nbsp;|&nbsp;
        <b>Profundidade:</b> 35 Páginas por Termo &nbsp;|&nbsp;
        <b>Total Renderizado:</b> 100% ({len(items)} editais)
    </div>
    <div class="summary-box">
        <div class="stat-item"><div class="stat-val">{len(items)}</div><div class="stat-lbl">Total Editais Catalogados</div></div>
        <div class="stat-item"><div class="stat-val" style="color: #16a34a;">{len(pregao_items)}</div><div class="stat-lbl" style="color: #16a34a;">Pregão Eletrônico</div></div>
        <div class="stat-item"><div class="stat-val" style="color: #475569;">{len(outros_items)}</div><div class="stat-lbl" style="color: #475569;">Outras Modalidades</div></div>
    </div>
</header>

<h2>⚡ 1. Editais em Pregão Eletrônico ({len(pregao_items)} Editais Renders)</h2>
"""

for idx, item in enumerate(pregao_items, 1):
    orgao = item.get('orgao') or 'Não informado'
    uf = item.get('uf') or 'DF'
    muni = item.get('municipio') or uf
    title = item.get('title') or f"Edital {item.get('control_num')}"
    modalidade = item.get('modalidade') or 'Pregão Eletrônico'
    objeto = (item.get('objeto') or 'Sem descrição.').strip()
    val = fmt_currency(item.get('valor_estimado'))
    dt_pub = fmt_date(item.get('data_publicacao'))
    dt_enc = fmt_date(item.get('data_encerramento_proposta'))
    terms = ", ".join(item.get('matched_terms', []))
    link_pncp = item.get('link_pncp')
    link_origem = item.get('link_origem')

    html_content += f"""
    <div class="card pregao">
        <div class="card-header">
            <div class="card-title">{idx}. {title} — {orgao}</div>
            <span class="badge badge-pregao">{modalidade}</span>
        </div>
        <div class="grid-info">
            <div><span class="info-label">Localização:</span> {muni} - {uf}</div>
            <div><span class="info-label">Sessão Pública:</span> <span class="enc-date">{dt_enc}</span></div>
            <div><span class="info-label">Valor Estimado:</span> {val}</div>
            <div><span class="info-label">Publicação:</span> {dt_pub}</div>
        </div>
        <div><span class="info-label">Termos Relacionados:</span> {terms}</div>
        <div class="objeto-text"><b>Objeto:</b> {objeto}</div>
        <div class="links-bar">
            {"<a href='" + link_pncp + "' target='_blank'>🔗 Abrir Edital no PNCP</a>" if link_pncp else ""}
            {"<a href='" + link_origem + "' target='_blank'>🌐 Portal de Origem</a>" if link_origem else ""}
        </div>
    </div>
    """

html_content += f"""
<h2>📜 2. Demais Modalidades ({len(outros_items)} Editais Renderizados)</h2>
"""

for idx, item in enumerate(outros_items, 1):
    orgao = item.get('orgao') or 'Não informado'
    uf = item.get('uf') or 'DF'
    muni = item.get('municipio') or uf
    title = item.get('title') or f"Edital {item.get('control_num')}"
    modalidade = item.get('modalidade') or 'Concorrência / Credenciamento'
    objeto = (item.get('objeto') or 'Sem descrição.').strip()
    val = fmt_currency(item.get('valor_estimado'))
    dt_pub = fmt_date(item.get('data_publicacao'))
    dt_enc = fmt_date(item.get('data_encerramento_proposta'))
    terms = ", ".join(item.get('matched_terms', []))
    link_pncp = item.get('link_pncp')
    link_origem = item.get('link_origem')

    html_content += f"""
    <div class="card">
        <div class="card-header">
            <div class="card-title">{idx}. {title} — {orgao}</div>
            <span class="badge badge-outros">{modalidade}</span>
        </div>
        <div class="grid-info">
            <div><span class="info-label">Localização:</span> {muni} - {uf}</div>
            <div><span class="info-label">Sessão Pública:</span> <span class="enc-date">{dt_enc}</span></div>
            <div><span class="info-label">Valor Estimado:</span> {val}</div>
            <div><span class="info-label">Publicação:</span> {dt_pub}</div>
        </div>
        <div><span class="info-label">Termos Relacionados:</span> {terms}</div>
        <div class="objeto-text"><b>Objeto:</b> {objeto}</div>
        <div class="links-bar">
            {"<a href='" + link_pncp + "' target='_blank'>🔗 Abrir Edital no PNCP</a>" if link_pncp else ""}
            {"<a href='" + link_origem + "' target='_blank'>🌐 Portal de Origem</a>" if link_origem else ""}
        </div>
    </div>
    """

html_content += """</body></html>"""

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Full HTML created at {html_file}")

edge_bin = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
cmd = [
    edge_bin,
    '--headless',
    '--disable-gpu',
    '--no-pdf-header-footer',
    f'--print-to-pdf={pdf_file}',
    f'file:///{html_file.replace("\\", "/")}'
]

print("Rendering full PDF via Edge Headless...")
subprocess.run(cmd, capture_output=True, text=True)
if os.path.exists(pdf_file):
    print(f"SUCCESS: Full PDF generated at {pdf_file}, Size: {os.path.getsize(pdf_file)/1024:.2f} KB")
