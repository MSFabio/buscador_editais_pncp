import json
import datetime
import os
import subprocess

json_file = r'C:\Users\11429149760\.gemini\antigravity\scratch\expanded_25pages_results.json'
html_file = r'C:\Users\11429149760\.gemini\antigravity\scratch\editais_bahia.html'
pdf_file = r'C:\Users\11429149760\.gemini\antigravity\brain\001766fb-0fab-4892-bf1e-723cc736a97c\editais_pncp_25paginas_bahia.pdf'

with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

ba_items = data.get('bahia', [])
ba_pregao = [i for i in ba_items if 'pregão' in (i.get('modalidade') or '').lower() or 'pregao' in (i.get('modalidade') or '').lower()]
ba_outros = [i for i in ba_items if i not in ba_pregao]

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

html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>PNCP - Editais Abertos na Bahia</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    @page {{
        size: A4;
        margin: 12mm 12mm 15mm 12mm;
    }}
    
    body {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: #0f172a;
        background-color: #ffffff;
        margin: 0;
        padding: 0;
        font-size: 13px;
        line-height: 1.5;
    }}
    
    header {{
        border-bottom: 2px solid #1e40af;
        padding-bottom: 12px;
        margin-bottom: 16px;
    }}
    
    h1 {{
        color: #1e40af;
        font-size: 22px;
        margin: 0 0 6px 0;
        font-weight: 700;
    }}
    
    .meta-bar {{
        font-size: 11px;
        color: #475569;
        margin-bottom: 12px;
    }}
    
    .meta-bar span {{
        font-weight: 600;
        color: #0f172a;
    }}
    
    .summary-box {{
        background: #f0f9ff;
        border: 1px solid #bae6fd;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-around;
    }}
    
    .stat-item {{
        text-align: center;
    }}
    
    .stat-val {{
        font-size: 20px;
        font-weight: 700;
        color: #0369a1;
    }}
    
    .stat-lbl {{
        font-size: 11px;
        color: #0369a1;
        font-weight: 500;
    }}
    
    h2 {{
        font-size: 15px;
        color: #0f172a;
        border-left: 4px solid #1e40af;
        padding-left: 8px;
        margin: 22px 0 12px 0;
        font-weight: 700;
    }}
    
    .card {{
        background: #ffffff;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 12px 14px;
        margin-bottom: 12px;
        page-break-inside: avoid;
    }}
    
    .card.pregao {{
        background: #fef2f2;
        border-color: #fca5a5;
    }}
    
    .card-header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 6px;
    }}
    
    .card-title {{
        font-weight: 700;
        font-size: 13px;
        color: #1e3a8a;
        margin: 0;
    }}
    
    .badge {{
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: 600;
        text-transform: uppercase;
    }}
    
    .badge-pregao {{
        background: #ef4444;
        color: #ffffff;
    }}
    
    .badge-outros {{
        background: #e2e8f0;
        color: #334155;
    }}
    
    .grid-info {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 4px 12px;
        font-size: 11px;
        margin-bottom: 6px;
    }}
    
    .info-row {{
        margin-bottom: 2px;
    }}
    
    .info-label {{
        font-weight: 600;
        color: #475569;
    }}
    
    .enc-date {{
        color: #dc2626;
        font-weight: 700;
    }}
    
    .objeto-text {{
        font-size: 11px;
        color: #334155;
        background: rgba(255, 255, 255, 0.7);
        border: 1px solid #e2e8f0;
        padding: 6px 8px;
        border-radius: 4px;
        margin-top: 6px;
    }}
    
    .links-bar {{
        margin-top: 8px;
        font-size: 11px;
    }}
    
    .links-bar a {{
        color: #2563eb;
        text-decoration: none;
        font-weight: 500;
        margin-right: 12px;
    }}
    
    .links-bar a:hover {{
        text-decoration: underline;
    }}
</style>
</head>
<body>

<header>
    <h1>📋 PNCP - Editais Abertos no Estado da Bahia (BA)</h1>
    <div class="meta-bar">
        <span>Data do Relatório:</span> 06/08/2026 &nbsp;|&nbsp;
        <span>Profundidade:</span> 25 Páginas por Termo de Busca &nbsp;|&nbsp;
        <span>Fonte:</span> Portal Nacional de Contratações Públicas
    </div>
    <div class="summary-box">
        <div class="stat-item">
            <div class="stat-val">{len(ba_items)}</div>
            <div class="stat-lbl">Total Editais em BA</div>
        </div>
        <div class="stat-item">
            <div class="stat-val" style="color: #dc2626;">{len(ba_pregao)}</div>
            <div class="stat-lbl" style="color: #dc2626;">Pregão Eletrônico / Presencial</div>
        </div>
        <div class="stat-item">
            <div class="stat-val" style="color: #475569;">{len(ba_outros)}</div>
            <div class="stat-lbl" style="color: #475569;">Credenciamento & Dispensa</div>
        </div>
    </div>
</header>

<h2>⚡ 1. Editais na Modalidade Pregão na Bahia ({len(ba_pregao)})</h2>
"""

for idx, item in enumerate(ba_pregao, 1):
    orgao = item.get('orgao') or 'Não informado'
    muni = item.get('municipio') or 'Bahia'
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
            <div class="info-row"><span class="info-label">Município:</span> {muni} - BA</div>
            <div class="info-row"><span class="info-label">Sessão Pública:</span> <span class="enc-date">{dt_enc}</span></div>
            <div class="info-row"><span class="info-label">Valor Estimado:</span> {val}</div>
            <div class="info-row"><span class="info-label">Publicação:</span> {dt_pub}</div>
        </div>
        <div class="info-row"><span class="info-label">Termos Relacionados:</span> {terms}</div>
        <div class="objeto-text"><b>Objeto:</b> {objeto}</div>
        <div class="links-bar">
            {"<a href='" + link_pncp + "' target='_blank'>🔗 Abrir Edital no PNCP</a>" if link_pncp else ""}
            {"<a href='" + link_origem + "' target='_blank'>🌐 Portal de Origem</a>" if link_origem else ""}
        </div>
    </div>
    """

html_content += f"""
<h2>📜 2. Demais Editais Abertos na Bahia - Credenciamento & Dispensa ({len(ba_outros)})</h2>
"""

for idx, item in enumerate(ba_outros, 1):
    orgao = item.get('orgao') or 'Não informado'
    muni = item.get('municipio') or 'Bahia'
    title = item.get('title') or f"Edital {item.get('control_num')}"
    modalidade = item.get('modalidade') or 'Credenciamento'
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
            <div class="info-row"><span class="info-label">Município:</span> {muni} - BA</div>
            <div class="info-row"><span class="info-label">Sessão / Encerramento:</span> <span class="enc-date">{dt_enc}</span></div>
            <div class="info-row"><span class="info-label">Valor Estimado:</span> {val}</div>
            <div class="info-row"><span class="info-label">Publicação:</span> {dt_pub}</div>
        </div>
        <div class="info-row"><span class="info-label">Termos Relacionados:</span> {terms}</div>
        <div class="objeto-text"><b>Objeto:</b> {objeto}</div>
        <div class="links-bar">
            {"<a href='" + link_pncp + "' target='_blank'>🔗 Abrir Edital no PNCP</a>" if link_pncp else ""}
            {"<a href='" + link_origem + "' target='_blank'>🌐 Portal de Origem</a>" if link_origem else ""}
        </div>
    </div>
    """

html_content += """
</body>
</html>
"""

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Generated HTML at {html_file}")

# Convert to PDF via MS Edge Headless
edge_bin = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'

cmd = [
    edge_bin,
    '--headless',
    '--disable-gpu',
    '--no-pdf-header-footer',
    f'--print-to-pdf={pdf_file}',
    f'file:///{html_file.replace("\\", "/")}'
]

print("Running Edge PDF generation command...")
res = subprocess.run(cmd, capture_output=True, text=True)
print("Return code:", res.returncode)
print("Stdout:", res.stdout)
print("Stderr:", res.stderr)

if os.path.exists(pdf_file):
    print(f"SUCCESS: PDF generated at {pdf_file}, Size: {os.path.getsize(pdf_file)/1024:.2f} KB")
else:
    print("ERROR: PDF was not generated.")
