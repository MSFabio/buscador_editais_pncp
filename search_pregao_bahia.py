import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import json
import datetime
import time

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

def search_pncp(query, page=1, uf=None):
    url = 'https://pncp.gov.br/api/search/'
    params = {
        'q': query,
        'tipos_documento': 'edital',
        'pagina': page,
        'status': 'recebendo_proposta'
    }
    if uf:
        params['uf'] = uf
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
        clean_str = date_str.split('.')[0]
        if 'T' in clean_str:
            dt = datetime.datetime.strptime(clean_str, "%Y-%m-%dT%H:%M:%S")
        else:
            dt = datetime.datetime.strptime(clean_str, "%Y-%m-%d")
        return dt
    except Exception as e:
        return None

def main():
    results = {}
    term_matches = {}

    print("--- Searching PNCP for Pregão Eletrônico in Bahia (BA) ---")

    for term in SEARCH_TERMS:
        print(f"\nSearching term: '{term}' with UF=BA...")
        for page in range(1, 10): # search up to 10 pages per term
            data = search_pncp(term, page=page, uf='BA')
            if not data or not data.get('items'):
                # Try without UF param in API and filter manually if API ignores uf param
                data_no_uf = search_pncp(term, page=page)
                if not data_no_uf or not data_no_uf.get('items'):
                    break
                items = [it for it in data_no_uf['items'] if it.get('uf') == 'BA']
            else:
                items = data['items']

            print(f"  Page {page}: found {len(items)} BA items")
            if not items:
                continue

            for item in items:
                uf = item.get('uf')
                if uf != 'BA':
                    continue

                modalidade = item.get('modalidade_licitacao_nome') or ''
                # We want Pregão Eletrônico / Pregão
                
                control_num = item.get('numero_controle_pncp')
                if not control_num:
                    continue

                if control_num not in term_matches:
                    term_matches[control_num] = []
                term_matches[control_num].append(term)

                if control_num in results:
                    continue

                cnpj = item.get('orgao_cnpj')
                ano = item.get('ano')
                seq = item.get('numero_sequencial')

                detail = None
                if cnpj and ano and seq:
                    detail = fetch_compra_detail(cnpj, ano, seq)
                    time.sleep(0.1)

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

                pncp_link = f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}" if (cnpj and ano and seq) else f"https://pncp.gov.br{item.get('item_url', '')}"
                
                results[control_num] = {
                    'control_num': control_num,
                    'title': item.get('title'),
                    'orgao': item.get('orgao_nome'),
                    'unidade': item.get('unidade_nome'),
                    'uf': item.get('uf'),
                    'municipio': item.get('municipio_nome'),
                    'modalidade': modalidade,
                    'objeto': detail.get('objetoCompra') if detail else item.get('description'),
                    'valor_estimado': detail.get('valorTotalEstimado') if detail else item.get('valor_global'),
                    'data_publicacao': item.get('data_publicacao_pncp'),
                    'data_abertura_proposta': data_abert,
                    'data_encerramento_proposta': data_enc,
                    'link_pncp': pncp_link,
                    'link_origem': detail.get('linkSistemaOrigem') if detail else None,
                    'detail_raw': detail
                }

    print(f"\nTotal unique open editais in BA collected: {len(results)}")
    
    pregao_eletronico_results = []
    other_pregao_results = []
    all_ba_results = []

    for ctrl, res in results.items():
        res['matched_terms'] = sorted(list(set(term_matches[ctrl])))
        all_ba_results.append(res)
        mod_lower = (res['modalidade'] or '').lower()
        if 'pregão' in mod_lower or 'pregao' in mod_lower:
            if 'eletrônico' in mod_lower or 'eletronico' in mod_lower:
                pregao_eletronico_results.append(res)
            else:
                other_pregao_results.append(res)

    print(f"Pregão Eletrônico em BA: {len(pregao_eletronico_results)}")
    print(f"Outros Pregões em BA: {len(other_pregao_results)}")

    with open('ba_pregao_search.json', 'w', encoding='utf-8') as f:
        json.dump({
            'pregao_eletronico': pregao_eletronico_results,
            'outros_pregoes': other_pregao_results,
            'todos_ba': all_ba_results
        }, f, indent=2, ensure_ascii=False)

if __name__ == '__main__':
    main()
