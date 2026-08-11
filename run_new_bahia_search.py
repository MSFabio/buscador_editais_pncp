import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import datetime
import os
import subprocess

TODAY_DATE = datetime.date(2026, 8, 7)

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

def main():
    print(f"--- Starting New Bahia Search (25 pages x {len(SEARCH_TERMS)} terms) ---", flush=True)

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

    print(f"Search complete. Found {len(term_items)} total candidate editais across Brazil. Fetching details...", flush=True)

    detailed_results = {}
    with ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(fetch_detail, item) for item in term_items.values()]
        for f in as_completed(futures):
            item, detail = f.result()
            ctrl = item.get('numero_controle_pncp')
            
            # Filter specifically for Bahia (BA)
            uf = item.get('uf')
            if uf != 'BA':
                continue

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
                'uf': 'BA',
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

    ba_list = list(detailed_results.values())

    # Sort by closing date ascending
    def sort_key(x):
        dt = parse_date(x['data_encerramento_proposta']) or parse_date(x['data_abertura_proposta'])
        return dt if dt else datetime.datetime(2099, 1, 1)

    ba_list.sort(key=sort_key)

    ba_pregao = [i for i in ba_list if 'pregão' in (i.get('modalidade') or '').lower() or 'pregao' in (i.get('modalidade') or '').lower()]

    print(f"\n==========================================", flush=True)
    print(f"NEW BAHIA SEARCH RESULTS (07/08/2026):", flush=True)
    print(f"Total Unique Open Future Editais (Bahia): {len(ba_list)}", flush=True)
    print(f"Pregões Eletrônicos/Presenciais na Bahia: {len(ba_pregao)}", flush=True)
    print(f"==========================================", flush=True)

    json_out = r'C:\Users\11429149760\.gemini\antigravity\scratch\new_bahia_results.json'
    with open(json_out, 'w', encoding='utf-8') as f:
        json.dump(ba_list, f, indent=2, ensure_ascii=False)

    print(f"Saved results to {json_out}", flush=True)

if __name__ == '__main__':
    main()
