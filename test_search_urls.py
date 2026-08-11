import requests

s = requests.Session()
s.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'Referer': 'https://pncp.gov.br/app/editais'
})

test_urls = [
    'https://pncp.gov.br/api/search/v1/contratacoes?q=buffet',
    'https://pncp.gov.br/api/search/v1/editais?q=buffet',
    'https://pncp.gov.br/api/search/v1/publicacoes?q=buffet',
    'https://pncp.gov.br/api/pncp/v1/contratacoes?q=buffet',
    'https://pncp.gov.br/api/consulta/v1/contratacoes?q=buffet',
    'https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao?dataInicial=20260801&dataFinal=20260810&pagina=1&q=buffet'
]

for url in test_urls:
    try:
        r = s.get(url, timeout=10)
        print(f"{url} -> status: {r.status_code}, len: {len(r.content)}")
        if r.status_code == 200:
            print("Response preview:", r.text[:300])
    except Exception as e:
        print(f"{url} -> error: {e}")
