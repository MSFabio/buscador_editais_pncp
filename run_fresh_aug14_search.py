import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import datetime
import os
import subprocess

TODAY_DATE = datetime.date(2026, 8, 14) # Today: August 14, 2026

SEARCH_TERMS = [
    "Buffet",
    "Buffet para eventos",
    "Buffet para cerimônias",
    "Catering",
    "Alimentação",
    "Alimentação para eventos",
    "Coffee Break",
    "Lanches"
]

NUM_PAGES = 25

SCRATCH_DIR = r'C:\Users\11429149760\.gemini\antigravity\scratch'
BRAIN_DIR = r'C:\Users\11429149760\.gemini\antigravity\brain\001766fb-0fab-4892-bf1e-723cc736a97c'

def get_session():
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries, pool_connections=30, pool_maxsize=30)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://pncp.gov.br/app/editais'
    })
    return session

session = get_session()

def search_term_page(args):
    term, page = args
    url = 'https://pncp.gov.br/api/search/'
    params = {
        'q': term,
        'tipos_documento': 'edital',
        'pagina': page,
        'status': 'recebendo_proposta'
    }
    try:
        r = session.get(url, params=params, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return term, page, data.get('items', [])
    except Exception:
        pass
    return term, page, []

def fetch_detail(item):
    cnpj = item.get('orgao_cnpj')
    ano = item.get('ano')
    seq = item.get('numero_sequencial')
    if not (cnpj and ano and seq):
        return item, None
    url = f'https://pncp.gov.br/api/consulta/v1/orgaos/{cnpj}/compras/{ano}/{seq}'
    try:
        r = session.get(url, timeout=8)
        if r.status_code == 200:
            return item, r.json()
    except Exception:
        pass
    return item, None

def parse_date(date_str):
    if not date_str:
        return None
    try:
        clean_str = date_str.split('.')[0]
        if 'T' in clean_str:
            return datetime.datetime.strptime(clean_str, "%Y-%m-%dT%H:%M:%S")
        else:
            return datetime.datetime.strptime(clean_str, "%Y-%m-%d")
    except Exception:
        return None

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

def main():
    print(f"--- PNCP Search for 14/08/2026 ({NUM_PAGES} pages x {len(SEARCH_TERMS)} terms) ---", flush=True)

    tasks = []
    for term in SEARCH_TERMS:
        for page in range(1, NUM_PAGES + 1):
            tasks.append((term, page))

    term_items = {}
    term_matches = {}

    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(search_term_page, t) for t in tasks]
        for f in as_completed(futures):
            term, page, items = f.result()
            for item in items:
                ctrl = item.get('numero_controle_pncp')
                if not ctrl:
                    continue
                if ctrl not in term_matches:
                    term_matches[ctrl] = []
                term_matches[ctrl].append(term)
                if ctrl not in term_items:
                    term_items[ctrl] = item

    print(f"Search complete. Found {len(term_items)} candidate editais across Brazil. Fetching details...", flush=True)

    detailed_results = {}
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(fetch_detail, item) for item in term_items.values()]
        for f in as_completed(futures):
            item, detail = f.result()
            ctrl = item.get('numero_controle_pncp')

            data_enc = detail.get('dataEncerramentoProposta') if detail else item.get('data_fim_vigencia')
            data_abert = detail.get('dataAberturaProposta') if detail else item.get('data_inicio_vigencia')
            
            enc_dt = parse_date(data_enc)
            abert_dt = parse_date(data_abert)

            is_future = False
            if enc_dt and enc_dt.date() >= TODAY_DATE:
                is_future = True
            elif abert_dt and abert_dt.date() >= TODAY_DATE:
                is_future = True
            elif not enc_dt and not abert_dt:
                is_future = True

            if not is_future:
                continue

            cnpj = item.get('orgao_cnpj')
            ano = item.get('ano')
            seq = item.get('numero_sequencial')
            pncp_link = f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}" if (cnpj and ano and seq) else f"https://pncp.gov.br{item.get('item_url', '')}"

            detailed_results[ctrl] = {
                'control_num': ctrl,
                'title': item.get('title'),
                'orgao': item.get('orgao_nome'),
                'unidade': item.get('unidade_nome'),
                'uf': item.get('uf') or 'DF',
                'municipio': item.get('municipio_nome'),
                'modalidade': item.get('modalidade_licitacao_nome'),
                'objeto': detail.get('objetoCompra') if detail else item.get('description'),
                'valor_estimado': detail.get('valorTotalEstimado') if detail else item.get('valor_global'),
                'data_publicacao': item.get('data_publicacao_pncp'),
                'data_abertura_proposta': data_abert,
                'data_encerramento_proposta': data_enc,
                'link_pncp': pncp_link,
                'link_origem': detail.get('linkSistemaOrigem') if detail else None,
                'matched_terms': sorted(list(set(term_matches.get(ctrl, []))))
            }

    all_list = list(detailed_results.values())
    ba_list = [i for i in all_list if i.get('uf') == 'BA']

    def sort_key(x):
        dt = parse_date(x['data_encerramento_proposta']) or parse_date(x['data_abertura_proposta'])
        return dt if dt else datetime.datetime(2099, 1, 1)

    all_list.sort(key=sort_key)
    ba_list.sort(key=sort_key)

    ba_pregao = [i for i in ba_list if 'pregão' in (i.get('modalidade') or '').lower() or 'pregao' in (i.get('modalidade') or '').lower()]
    ba_outros = [i for i in ba_list if i not in ba_pregao]

    print(f"\n==========================================", flush=True)
    print(f"NEW PNCP SEARCH RESULTS (14/08/2026):", flush=True)
    print(f"Total Editais Brasil: {len(all_list)}", flush=True)
    print(f"Total Editais Bahia: {len(ba_list)}", flush=True)
    print(f"Pregões na Bahia: {len(ba_pregao)}", flush=True)
    print(f"==========================================", flush=True)

    # Generate Markdown for Bahia
    md_file = os.path.join(BRAIN_DIR, 'editais_pncp_25paginas_bahia.md')
    lines_md = []
    lines_md.append(f"# 📍 Editais Abertos PNCP - Bahia (BA) [Atualizado em {TODAY_DATE.strftime('%d/%m/%Y')}]")
    lines_md.append(f"**Data da Pesquisa:** {TODAY_DATE.strftime('%d/%m/%Y')}  ")
    lines_md.append(f"**Profundidade:** {NUM_PAGES} Páginas por Termo de Busca (Busca Completa)  ")
    lines_md.append(f"**Termos Pesquisados (8):** {', '.join(SEARCH_TERMS)}  ")
    lines_md.append(f"**Total de Editais Abertos na Bahia:** `{len(ba_list)}` editais  ")
    lines_md.append(f"**Editais na Modalidade Pregão na Bahia:** `{len(ba_pregao)}` editais  \n")

    lines_md.append("> [!NOTE]")
    lines_md.append("> Todos os editais listados abaixo possuem prazo de envio de propostas ou sessão pública agendada para datas futuras a partir de 14/08/2026.\n")

    lines_md.append("## ⚡ 1. Editais na Modalidade Pregão na Bahia (BA)\n")
    for idx, item in enumerate(ba_pregao, 1):
        orgao = item.get('orgao') or 'Não informado'
        muni = item.get('municipio') or 'Bahia'
        title = item.get('title') or f"Edital {item.get('control_num')}"
        modalidade = item.get('modalidade') or 'Pregão Eletrônico'
        objeto = (item.get('objeto') or 'Sem descrição.').strip()
        val = fmt_currency(item.get('valor_estimado'))
        dt_pub = fmt_date(item.get('data_publicacao'))
        dt_enc = fmt_date(item.get('data_encerramento_proposta'))
        terms_str = ", ".join([f"`{t}`" for t in item.get('matched_terms', [])])
        link_pncp = item.get('link_pncp')
        link_origem = item.get('link_origem')

        lines_md.append(f"### {idx}. {title} — {orgao}")
        lines_md.append(f"- **Órgão:** {orgao}")
        lines_md.append(f"- **Município / UF:** {muni} - BA")
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

    lines_md.append(f"## 📜 2. Demais Editais Abertos na Bahia ({len(ba_outros)})\n")
    for idx, item in enumerate(ba_outros, 1):
        orgao = item.get('orgao') or 'Não informado'
        muni = item.get('municipio') or 'Bahia'
        title = item.get('title') or f"Edital {item.get('control_num')}"
        modalidade = item.get('modalidade') or 'Credenciamento'
        objeto = (item.get('objeto') or 'Sem descrição.').strip()
        val = fmt_currency(item.get('valor_estimado'))
        dt_pub = fmt_date(item.get('data_publicacao'))
        dt_enc = fmt_date(item.get('data_encerramento_proposta'))
        terms_str = ", ".join([f"`{t}`" for t in item.get('matched_terms', [])])
        link_pncp = item.get('link_pncp')
        link_origem = item.get('link_origem')

        lines_md.append(f"### {idx}. {title} — {orgao}")
        lines_md.append(f"- **Órgão:** {orgao}")
        lines_md.append(f"- **Município / UF:** {muni} - BA")
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

    # Generate HTML & PDF via Edge Headless
    html_file = os.path.join(SCRATCH_DIR, 'editais_bahia.html')
    pdf_file = os.path.join(BRAIN_DIR, 'editais_pncp_25paginas_bahia.pdf')

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>PNCP - Editais Abertos na Bahia</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    @page {{ size: A4; margin: 12mm; }}
    body {{ font-family: 'Inter', -apple-system, sans-serif; color: #0f172a; background: #ffffff; font-size: 12px; line-height: 1.45; margin: 0; padding: 0; }}
    header {{ border-bottom: 2px solid #1e40af; padding-bottom: 10px; margin-bottom: 14px; }}
    h1 {{ color: #1e40af; font-size: 20px; margin: 0 0 6px 0; font-weight: 700; }}
    .meta-bar {{ font-size: 11px; color: #475569; margin-bottom: 10px; }}
    .summary-box {{ background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 6px; padding: 10px 14px; margin-bottom: 16px; display: flex; justify-content: space-around; }}
    .stat-item {{ text-align: center; }}
    .stat-val {{ font-size: 20px; font-weight: 700; color: #0369a1; }}
    .stat-lbl {{ font-size: 11px; color: #0369a1; font-weight: 500; }}
    h2 {{ font-size: 14px; color: #0f172a; border-left: 4px solid #1e40af; padding-left: 8px; margin: 20px 0 10px 0; font-weight: 700; }}
    .card {{ background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 10px 12px; margin-bottom: 10px; page-break-inside: avoid; }}
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
    <h1>📋 PNCP - Editais Abertos na Bahia</h1>
    <div class="meta-bar">
        <b>Data da Pesquisa:</b> {TODAY_DATE.strftime('%d/%m/%Y')} &nbsp;|&nbsp;
        <b>Profundidade:</b> {NUM_PAGES} Páginas por Termo de Busca &nbsp;|&nbsp;
        <b>Fonte:</b> Portal Nacional de Contratações Públicas
    </div>
    <div class="summary-box">
        <div class="stat-item"><div class="stat-val">{len(ba_list)}</div><div class="stat-lbl">Total Editais em BA</div></div>
        <div class="stat-item"><div class="stat-val" style="color: #dc2626;">{len(ba_pregao)}</div><div class="stat-lbl" style="color: #dc2626;">Pregão Eletrônico</div></div>
        <div class="stat-item"><div class="stat-val" style="color: #475569;">{len(ba_outros)}</div><div class="stat-lbl" style="color: #475569;">Credenciamento & Dispensa</div></div>
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
                <div><span class="info-label">Município:</span> {muni} - BA</div>
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

    html_content += f"<h2>📜 2. Demais Editais Abertos na Bahia ({len(ba_outros)})</h2>"

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
                <div><span class="info-label">Município:</span> {muni} - BA</div>
                <div><span class="info-label">Sessão / Encerramento:</span> <span class="enc-date">{dt_enc}</span></div>
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
        f'--print-to-pdf={pdf_file}',
        f'file:///{html_file.replace("\\", "/")}'
    ]

    subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(pdf_file):
        print(f"SUCCESS: PDF generated at {pdf_file}, Size: {os.path.getsize(pdf_file)/1024:.2f} KB")

if __name__ == '__main__':
    main()
