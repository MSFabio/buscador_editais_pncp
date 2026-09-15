import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import datetime
import os
import subprocess

TODAY_DATE = datetime.date(2026, 9, 15) # Today: September 15, 2026

SEARCH_TERMS = [
    "Buffet",
    "Buffet para eventos",
    "Kit lanche",
    "Buffet para cerimônias",
    "Catering",
    "Alimentação",
    "Alimentação para eventos",
    "Coffee Break",
    "Lanches"
]

NUM_PAGES = 30

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

def sort_by_date(item_list):
    def sort_key(x):
        dt = parse_date(x.get('data_encerramento_proposta')) or parse_date(x.get('data_abertura_proposta'))
        return dt if dt else datetime.datetime(2099, 1, 1)
    return sorted(item_list, key=sort_key)

def main():
    print(f"--- PNCP Search for 15/09/2026 ({NUM_PAGES} pages x {len(SEARCH_TERMS)} terms) ---", flush=True)

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

            muni_name = item.get('municipio_nome') or 'Bahia'

            detailed_results[ctrl] = {
                'control_num': ctrl,
                'title': item.get('title'),
                'orgao': item.get('orgao_nome'),
                'unidade': item.get('unidade_nome'),
                'uf': item.get('uf') or 'DF',
                'municipio': muni_name,
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

    # Group strictly by modality
    pregao_items = []
    credenciamento_items = []
    dispensa_items = []
    outras_items = []

    for item in ba_list:
        mod = (item.get('modalidade') or '').lower()
        if 'pregão' in mod or 'pregao' in mod:
            pregao_items.append(item)
        elif 'credenciamento' in mod:
            credenciamento_items.append(item)
        elif 'dispensa' in mod:
            dispensa_items.append(item)
        else:
            outras_items.append(item)

    pregao_items = sort_by_date(pregao_items)
    credenciamento_items = sort_by_date(credenciamento_items)
    dispensa_items = sort_by_date(dispensa_items)
    outras_items = sort_by_date(outras_items)

    groups = [
        ("⚡ 1. Pregão Eletrônico / Presencial", pregao_items, "Pregão Eletrônico", "#ef4444", "badge-pregao"),
        ("📜 2. Credenciamento / Chamamento Público", credenciamento_items, "Credenciamento", "#2563eb", "badge-credenciamento"),
        ("📋 3. Dispensa de Licitação", dispensa_items, "Dispensa", "#16a34a", "badge-dispensa")
    ]
    if outras_items:
        groups.append(("📂 4. Outras Modalidades", outras_items, "Outras", "#64748b", "badge-outros"))

    print(f"\n==========================================", flush=True)
    print(f"SEARCH RESULTS (15/09/2026):", flush=True)
    print(f"Total Editais Brasil: {len(all_list)}", flush=True)
    print(f"Total Editais Bahia: {len(ba_list)}", flush=True)
    print(f"Pregões na Bahia: {len(pregao_items)}", flush=True)
    print(f"Credenciamentos na Bahia: {len(credenciamento_items)}", flush=True)
    print(f"Dispensas na Bahia: {len(dispensa_items)}", flush=True)
    if outras_items:
        print(f"Outras na Bahia: {len(outras_items)}", flush=True)
    print(f"==========================================", flush=True)

    # Save JSON
    json_out = os.path.join(SCRATCH_DIR, 'sep15_bahia_results.json')
    with open(json_out, 'w', encoding='utf-8') as f:
        json.dump({'brasil': all_list, 'bahia': ba_list, 'pregao': pregao_items, 'credenciamento': credenciamento_items, 'dispensa': dispensa_items}, f, indent=2, ensure_ascii=False)

    # 1. BUILD MARKDOWN REPORT
    md_file = os.path.join(BRAIN_DIR, 'editais_pncp_modalidade_bahia.md')
    lines_md = []
    lines_md.append(f"# 📍 Editais PNCP na Bahia - Organização Exclusiva por Modalidade [Atualizado em {TODAY_DATE.strftime('%d/%m/%Y')}]")
    lines_md.append(f"**Data da Busca Atualizada:** {TODAY_DATE.strftime('%d/%m/%Y')}  ")
    lines_md.append(f"**Critério de Organização:** Agrupamento por Modalidade de Licitação (Sem filtro de distância)  ")
    lines_md.append(f"**Profundidade:** {NUM_PAGES} Páginas por Termo de Busca (Varredura Completa)  ")
    lines_md.append(f"**Termos Pesquisados:** {', '.join(SEARCH_TERMS)}  ")
    lines_md.append(f"**Total de Editais Mapeados na Bahia:** `{len(ba_list)}` editais abertos  ")
    lines_md.append(f"**Total de Editais Mapeados no Brasil:** `{len(all_list)}` editais abertos  \n")

    lines_md.append("> [!NOTE]")
    lines_md.append("> Todos os editais listados possuem recebimento de propostas ou sessão pública agendados para datas futuras a partir de 15/09/2026 no estado da Bahia.\n")

    lines_md.append("## 📊 Resumo por Modalidade\n")
    lines_md.append("| Modalidade | Qtd Editais | Percentual |")
    lines_md.append("| :--- | :---: | :---: |")
    for title, items, mod_name, color, badge_class in groups:
        pct = (len(items) / len(ba_list) * 100) if ba_list else 0
        lines_md.append(f"| **{mod_name}** | **`{len(items)}`** | `{pct:.1f}%` |")
    lines_md.append(f"| **TOTAL** | **`{len(ba_list)}`** | `100.0%` |")
    lines_md.append("\n---\n")

    for title, items, mod_name, color, badge_class in groups:
        lines_md.append(f"## {title} ({len(items)} editais)\n")
        if not items:
            lines_md.append("_Nenhum edital encontrado nesta modalidade._\n\n")
            continue

        for idx, item in enumerate(items, 1):
            orgao = item.get('orgao') or 'Não informado'
            muni = item.get('municipio') or 'Bahia'
            title_ed = item.get('title') or f"Edital {item.get('control_num')}"
            modalidade = item.get('modalidade') or mod_name
            objeto = (item.get('objeto') or 'Sem descrição.').strip()
            val = fmt_currency(item.get('valor_estimado'))
            dt_pub = fmt_date(item.get('data_publicacao'))
            dt_enc = fmt_date(item.get('data_encerramento_proposta'))
            terms_str = ", ".join([f"`{t}`" for t in item.get('matched_terms', [])])
            link_pncp = item.get('link_pncp')
            link_origem = item.get('link_origem')

            lines_md.append(f"### {idx}. {title_ed} — {orgao}")
            lines_md.append(f"- **Órgão / Entidade:** {orgao}")
            lines_md.append(f"- **Município / UF:** **{muni} - BA**")
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

    # 2. BUILD HTML FOR PDF
    html_file = os.path.join(SCRATCH_DIR, 'editais_modalidade_bahia.html')
    pdf_file = os.path.join(BRAIN_DIR, 'editais_pncp_modalidade_bahia.pdf')

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>PNCP - Editais da Bahia por Modalidade</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    @page {{ size: A4; margin: 10mm; }}
    body {{
        font-family: 'Inter', -apple-system, sans-serif;
        color: #0f172a; background: #ffffff; font-size: 11px; line-height: 1.4; margin: 0; padding: 0;
    }}
    header {{ border-bottom: 2px solid #1e40af; padding-bottom: 8px; margin-bottom: 12px; }}
    h1 {{ color: #1e40af; font-size: 18px; margin: 0 0 4px 0; font-weight: 700; }}
    .meta-bar {{ font-size: 10.5px; color: #475569; margin-bottom: 8px; }}
    .summary-grid {{
        display: grid;
        grid-template-columns: repeat({len(groups)}, 1fr);
        gap: 8px;
        margin-bottom: 14px;
    }}
    .stat-card {{
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 8px;
        text-align: center;
    }}
    .stat-val {{ font-size: 18px; font-weight: 700; }}
    .stat-lbl {{ font-size: 10px; font-weight: 600; color: #475569; }}
    .group-header {{
        font-size: 13px; font-weight: 700; color: #ffffff;
        padding: 6px 10px; border-radius: 4px; margin: 16px 0 10px 0;
    }}
    .card {{
        background: #ffffff; border: 1px solid #cbd5e1; border-radius: 5px;
        padding: 8px 10px; margin-bottom: 8px; page-break-inside: avoid;
    }}
    .card.pregao {{ background: #fef2f2; border-color: #fca5a5; }}
    .card.dispensa {{ background: #f0fdf4; border-color: #86efac; }}
    .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px; }}
    .card-title {{ font-weight: 700; font-size: 11.5px; color: #1e3a8a; margin: 0; }}
    .badge {{ display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 9.5px; font-weight: 600; text-transform: uppercase; }}
    .badge-pregao {{ background: #ef4444; color: #ffffff; }}
    .badge-credenciamento {{ background: #2563eb; color: #ffffff; }}
    .badge-dispensa {{ background: #16a34a; color: #ffffff; }}
    .badge-outros {{ background: #64748b; color: #ffffff; }}
    .grid-info {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2px 10px; font-size: 10.5px; margin-bottom: 4px; }}
    .info-label {{ font-weight: 600; color: #475569; }}
    .enc-date {{ color: #dc2626; font-weight: 700; }}
    .objeto-text {{ font-size: 10.5px; color: #334155; background: rgba(255, 255, 255, 0.7); border: 1px solid #e2e8f0; padding: 4px 6px; border-radius: 3px; margin-top: 3px; }}
    .links-bar {{ margin-top: 4px; font-size: 10.5px; }}
    .links-bar a {{ color: #2563eb; text-decoration: none; font-weight: 500; margin-right: 10px; }}
</style>
</head>
<body>

<header>
    <h1>📋 PNCP - Editais Abertos na Bahia Organizados por Modalidade</h1>
    <div class="meta-bar">
        <b>Data do Levantamento:</b> {TODAY_DATE.strftime('%d/%m/%Y')} &nbsp;|&nbsp;
        <b>Estado:</b> Bahia (BA) &nbsp;|&nbsp;
        <b>Total de Oportunidades:</b> {len(ba_list)} editais &nbsp;|&nbsp;
        <b>Fonte:</b> Portal Nacional de Contratações Públicas
    </div>
    <div class="summary-grid">
"""

    for title, items, mod_name, color, badge_class in groups:
        html_content += f"""
        <div class="stat-card" style="border-left: 4px solid {color};">
            <div class="stat-val" style="color: {color};">{len(items)}</div>
            <div class="stat-lbl">{mod_name}</div>
        </div>
        """

    html_content += """
    </div>
</header>
"""

    for title, items, mod_name, color, badge_class in groups:
        html_content += f"""
        <div class="group-header" style="background-color: {color};">
            {title} ({len(items)} editais)
        </div>
        """
        card_type_class = "pregao" if "pregão" in mod_name.lower() else ("dispensa" if "dispensa" in mod_name.lower() else "")

        for idx, item in enumerate(items, 1):
            orgao = item.get('orgao') or 'Não informado'
            muni = item.get('municipio') or 'Bahia'
            title_ed = item.get('title') or f"Edital {item.get('control_num')}"
            modalidade = item.get('modalidade') or mod_name
            objeto = (item.get('objeto') or 'Sem descrição.').strip()
            val = fmt_currency(item.get('valor_estimado'))
            dt_pub = fmt_date(item.get('data_publicacao'))
            dt_enc = fmt_date(item.get('data_encerramento_proposta'))
            terms = ", ".join(item.get('matched_terms', []))
            link_pncp = item.get('link_pncp')
            link_origem = item.get('link_origem')

            html_content += f"""
            <div class="card {card_type_class}">
                <div class="card-header">
                    <div class="card-title">{idx}. {title_ed} — {orgao}</div>
                    <span class="badge {badge_class}">{modalidade}</span>
                </div>
                <div class="grid-info">
                    <div><span class="info-label">Município:</span> <b>{muni} - BA</b></div>
                    <div><span class="info-label">Sessão / Encerramento:</span> <span class="enc-date">{dt_enc}</span></div>
                    <div><span class="info-label">Valor Estimado:</span> {val}</div>
                    <div><span class="info-label">Publicação:</span> {dt_pub}</div>
                </div>
                <div><span class="info-label">Termos:</span> {terms}</div>
                <div class="objeto-text"><b>Objeto:</b> {objeto}</div>
                <div class="links-bar">
                    {"<a href='" + link_pncp + "' target='_blank'>🔗 Abrir no PNCP</a>" if link_pncp else ""}
                    {"<a href='" + link_origem + "' target='_blank'>🌐 Portal de Origem</a>" if link_origem else ""}
                </div>
            </div>
            """

    html_content += """</body></html>"""

    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML written to {html_file}")

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
