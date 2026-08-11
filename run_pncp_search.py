import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import json
import datetime
import time

CURRENT_DATE_ISO = "2026-08-06T17:00:00"
TODAY_DATE = datetime.date(2026, 8, 6)

SEARCH_TERMS = [
    "Buffet",
    "Buffet para eventos",
    "Buffet para cerimônias",
    "Catering",
    "Alimentação",
    "Alimentação para eventos"
]

def get_session():
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': 'https://pncp.gov.br/app/editais'
    })
    return session

session = get_session()

def search_pncp(query, page=1):
    url = 'https://pncp.gov.br/api/search/'
    params = {
        'q': query,
        'tipos_documento': 'edital',
        'pagina': page,
        'status': 'recebendo_proposta'
    }
    try:
        r = session.get(url, params=params, timeout=15)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Error searching '{query}' page {page}: {e}")
    return None

def fetch_compra_detail(cnpj, ano, sequencial):
    url = f'https://pncp.gov.br/api/consulta/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}'
    try:
        r = session.get(url, timeout=12)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        print(f"Error detail {cnpj}/{ano}/{sequencial}: {e}")
    return None

def parse_date(date_str):
    if not date_str:
        return None
    try:
        # e.g. 2026-08-19T09:00:00 or 2026-08-19
        clean_str = date_str.split('.')[0]
        if 'T' in clean_str:
            dt = datetime.datetime.strptime(clean_str, "%Y-%m-%dT%H:%M:%S")
        else:
            dt = datetime.datetime.strptime(clean_str, "%Y-%m-%d")
        return dt
    except Exception as e:
        return None

def main():
    results_by_control = {}
    term_matches = {} # control_number -> list of terms

    print(f"--- Starting PNCP search for {len(SEARCH_TERMS)} terms ---")

    for term in SEARCH_TERMS:
        print(f"\nSearching term: '{term}'...")
        # Check first 3 pages (up to 30 items per term)
        for page in range(1, 4):
            data = search_pncp(term, page=page)
            if not data or not data.get('items'):
                break
            
            items = data['items']
            print(f"  Page {page}: found {len(items)} items (total query matches: {data.get('total')})")
            
            for item in items:
                control_num = item.get('numero_controle_pncp')
                if not control_num:
                    continue

                if control_num not in term_matches:
                    term_matches[control_num] = []
                term_matches[control_num].append(term)

                if control_num in results_by_control:
                    continue

                # Parse basic info
                cnpj = item.get('orgao_cnpj')
                ano = item.get('ano')
                seq = item.get('numero_sequencial')

                # Fetch details
                detail = None
                if cnpj and ano and seq:
                    detail = fetch_compra_detail(cnpj, ano, seq)
                    time.sleep(0.1) # polite delay

                data_enc = detail.get('dataEncerramentoProposta') if detail else item.get('data_fim_vigencia')
                data_abert = detail.get('dataAberturaProposta') if detail else item.get('data_inicio_vigencia')
                
                enc_dt = parse_date(data_enc)
                abert_dt = parse_date(data_abert)

                # Filter: check if enc_dt or abert_dt is in the future (> TODAY_DATE)
                # If neither date is parsed or available, we keep it if status is 'recebendo_proposta'
                is_future = False
                if enc_dt and enc_dt.date() >= TODAY_DATE:
                    is_future = True
                elif abert_dt and abert_dt.date() >= TODAY_DATE:
                    is_future = True
                elif not enc_dt and not abert_dt:
                    is_future = True # fallback

                if not is_future:
                    continue

                # Build record
                pncp_link = f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}" if (cnpj and ano and seq) else f"https://pncp.gov.br{item.get('item_url', '')}"
                
                results_by_control[control_num] = {
                    'control_num': control_num,
                    'title': item.get('title'),
                    'orgao': item.get('orgao_nome'),
                    'unidade': item.get('unidade_nome'),
                    'uf': item.get('uf'),
                    'municipio': item.get('municipio_nome'),
                    'modalidade': item.get('modalidade_licitacao_nome'),
                    'objeto': detail.get('objetoCompra') if detail else item.get('description'),
                    'valor_estimado': detail.get('valorTotalEstimado') if detail else item.get('valor_global'),
                    'data_publicacao': item.get('data_publicacao_pncp'),
                    'data_abertura_proposta': data_abert,
                    'data_encerramento_proposta': data_enc,
                    'link_pncp': pncp_link,
                    'link_origem': detail.get('linkSistemaOrigem') if detail else None,
                    'detail_raw': detail
                }

    print(f"\nTotal unique open future editais collected: {len(results_by_control)}")

    # Attach matched terms
    final_list = []
    for ctrl, res in results_by_control.items():
        res['matched_terms'] = sorted(list(set(term_matches[ctrl])))
        final_list.append(res)

    # Sort by proposal closing date ascending
    def sort_key(x):
        dt = parse_date(x['data_encerramento_proposta']) or parse_date(x['data_abertura_proposta'])
        return dt if dt else datetime.datetime(2099, 1, 1)

    final_list.sort(key=sort_key)

    with open('pncp_results.json', 'w', encoding='utf-8') as f:
        json.dump(final_list, f, indent=2, ensure_ascii=False)

    print("Saved results to pncp_results.json")

if __name__ == '__main__':
    main()
