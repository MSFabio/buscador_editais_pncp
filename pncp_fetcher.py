import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import json
import time

def get_pncp_session():
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

session = get_pncp_session()

def fetch_search(query, status='recebendo_proposta', page=1):
    url = 'https://pncp.gov.br/api/search/'
    params = {
        'q': query,
        'tipos_documento': 'edital',
        'pagina': page,
        'status': status
    }
    try:
        res = session.get(url, params=params, timeout=15)
        if res.status_code == 200:
            return res.json()
        else:
            print(f"Status {res.status_code} for query '{query}': {res.text[:200]}")
            return None
    except Exception as e:
        print(f"Error fetching '{query}': {e}")
        return None

if __name__ == '__main__':
    data = fetch_search('buffet', status='recebendo_proposta', page=1)
    if data:
        print("Total found:", data.get('total'))
        print("Items count:", len(data.get('items', [])))
        if data.get('items'):
            print("Sample item 0:", json.dumps(data['items'][0], indent=2, ensure_ascii=False))
