import os
import json
import datetime
import subprocess

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

def generate_pdf_report(data_items, output_pdf_path, uf_filter="BA"):
    html_file = output_pdf_path.replace('.pdf', '_temp.html')
    
    pregao_items = [i for i in data_items if 'pregão' in (i.get('modalidade') or '').lower() or 'pregao' in (i.get('modalidade') or '').lower()]
    outros_items = [i for i in data_items if i not in pregao_items]

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>PNCP - Relatório de Editais Abertos ({uf_filter})</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    @page {{ size: A4; margin: 12mm; }}
    body {{
        font-family: 'Inter', -apple-system, sans-serif;
        color: #0f172a;
        background: #ffffff;
        font-size: 12px;
        line-height: 1.45;
        margin: 0; padding: 0;
    }}
    header {{ border-bottom: 2px solid #1e40af; padding-bottom: 10px; margin-bottom: 14px; }}
    h1 {{ color: #1e40af; font-size: 20px; margin: 0 0 6px 0; font-weight: 700; }}
    .meta-bar {{ font-size: 11px; color: #475569; margin-bottom: 10px; }}
    .summary-box {{
        background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 6px;
        padding: 10px 14px; margin-bottom: 16px; display: flex; justify-content: space-around;
    }}
    .stat-item {{ text-align: center; }}
    .stat-val {{ font-size: 20px; font-weight: 700; color: #0369a1; }}
    .stat-lbl {{ font-size: 11px; color: #0369a1; font-weight: 500; }}
    h2 {{ font-size: 14px; color: #0f172a; border-left: 4px solid #1e40af; padding-left: 8px; margin: 20px 0 10px 0; font-weight: 700; }}
    .card {{
        background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px;
        padding: 10px 12px; margin-bottom: 10px; page-break-inside: avoid;
    }}
    .card.pregao {{ background: #fef2f2; border-color: #fca5a5; }}
    .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; }}
    .card-title {{ font-weight: 700; font-size: 12px; color: #1e3a8a; margin: 0; }}
    .badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; text-transform: uppercase; }}
    .badge-pregao {{ background: #ef4444; color: #ffffff; }}
    .badge-outros {{ background: #e2e8f0; color: #334155; }}
    .grid-info {{ display: grid; grid-template-columns: 1fr 1fr; gap: 4px 12px; font-size: 11px; margin-bottom: 6px; }}
    .info-label {{ font-weight: 600; color: #475569; }}
    .enc-date {{ color: #dc2626; font-weight: 700; }}
    .objeto-text {{ font-size: 11px; color: #334155; background: rgba(255, 255, 255, 0.7); border: 1px solid #e2e8f0; padding: 6px 8px; border-radius: 4px; margin-top: 4px; }}
    .links-bar {{ margin-top: 6px; font-size: 11px; }}
    .links-bar a {{ color: #2563eb; text-decoration: none; font-weight: 500; margin-right: 12px; }}
</style>
</head>
<body>
<header>
    <h1>📋 PNCP - Editais Abertos ({uf_filter})</h1>
    <div class="meta-bar">
        <b>Data do Relatório:</b> {datetime.date.today().strftime('%d/%m/%Y')} &nbsp;|&nbsp;
        <b>Fonte:</b> Portal Nacional de Contratações Públicas (PNCP)
    </div>
    <div class="summary-box">
        <div class="stat-item"><div class="stat-val">{len(data_items)}</div><div class="stat-lbl">Total Editais</div></div>
        <div class="stat-item"><div class="stat-val" style="color: #dc2626;">{len(pregao_items)}</div><div class="stat-lbl" style="color: #dc2626;">Pregão Eletrônico</div></div>
        <div class="stat-item"><div class="stat-val" style="color: #475569;">{len(outros_items)}</div><div class="stat-lbl" style="color: #475569;">Outras Modalidades</div></div>
    </div>
</header>

<h2>⚡ 1. Editais na Modalidade Pregão ({len(pregao_items)})</h2>
"""
    for idx, item in enumerate(pregao_items, 1):
        orgao = item.get('orgao') or 'Não informado'
        muni = item.get('municipio') or uf_filter
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
                <div><span class="info-label">Município:</span> {muni} - {uf_filter}</div>
                <div><span class="info-label">Sessão Pública:</span> <span class="enc-date">{dt_enc}</span></div>
                <div><span class="info-label">Valor Estimado:</span> {val}</div>
                <div><span class="info-label">Publicação:</span> {dt_pub}</div>
            </div>
            <div><span class="info-label">Termos Relacionados:</span> {terms}</div>
            <div class="objeto-text"><b>Objeto:</b> {objeto}</div>
            <div class="links-bar">
                {"<a href='" + link_pncp + "' target='_blank'>🔗 Ver no PNCP</a>" if link_pncp else ""}
                {"<a href='" + link_origem + "' target='_blank'>🌐 Sistema de Origem</a>" if link_origem else ""}
            </div>
        </div>
        """

    html_content += f"<h2>📜 2. Demais Modalidades ({len(outros_items)})</h2>"

    for idx, item in enumerate(outros_items, 1):
        orgao = item.get('orgao') or 'Não informado'
        muni = item.get('municipio') or uf_filter
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
                <div><span class="info-label">Município:</span> {muni} - {uf_filter}</div>
                <div><span class="info-label">Sessão / Encerramento:</span> <span class="enc-date">{dt_enc}</span></div>
                <div><span class="info-label">Valor Estimado:</span> {val}</div>
                <div><span class="info-label">Publicação:</span> {dt_pub}</div>
            </div>
            <div><span class="info-label">Termos Relacionados:</span> {terms}</div>
            <div class="objeto-text"><b>Objeto:</b> {objeto}</div>
            <div class="links-bar">
                {"<a href='" + link_pncp + "' target='_blank'>🔗 Ver no PNCP</a>" if link_pncp else ""}
                {"<a href='" + link_origem + "' target='_blank'>🌐 Sistema de Origem</a>" if link_origem else ""}
            </div>
        </div>
        """

    html_content += "</body></html>"

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    edge_bin = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    if not os.path.exists(edge_bin):
        edge_bin = r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'

    cmd = [
        edge_bin,
        '--headless',
        '--disable-gpu',
        '--no-pdf-header-footer',
        f'--print-to-pdf={output_pdf_path}',
        f'file:///{html_file.replace("\\", "/")}'
    ]

    subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(html_file):
        os.remove(html_file)
    print(f"PDF generated: {output_pdf_path}")
