import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import json
import time
import os
import sys

def get_pncp_session():
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=0.5,
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

def fetch_pncp_search_page(session, query, page=1, status=''):
    url = 'https://pncp.gov.br/api/search/'
    params = {
        'q': query,
        'tipos_documento': 'edital',
        'pagina': page
    }
    if status:
        params['status'] = status
        
    try:
        res = session.get(url, params=params, timeout=15)
        if res.status_code == 200:
            return res.json()
        else:
            print(f"[SEARCH ERROR] Status {res.status_code} for '{query}' (page {page})")
            return None
    except Exception as e:
        print(f"[SEARCH EXCEPTION] Query '{query}' page {page}: {e}")
        return None

def fetch_all_salesforce_processes(search_terms=None):
    if search_terms is None:
        search_terms = [
            "Salesforce",
            "Government Cloud",
            "Service Cloud",
            "Sales Cloud",
            "Marketing Cloud",
            "Experience Cloud",
            "CRM Salesforce",
            "Salesforce CRM",
            "Agentforce",
            "Slack",
            "Customer 360",
            "Data 360",
            "Headless 360",
            "MuleSoft",
            "Tableau"
        ]
        
    session = get_pncp_session()
    all_processes = {} # key: process id / control number
    
    print(f"=== Iniciando Varredura REFINADA no PNCP para {len(search_terms)} Termos Salesforce (incluindo Government Cloud) ===")
    
    for term in search_terms:
        print(f"\n[BUSCA REFINADA] Termo: '{term}'")
        first_page = fetch_pncp_search_page(session, term, page=1)
        if not first_page:
            continue
            
        total = first_page.get('total', 0)
        total_pages = first_page.get('total_paginas', 1) or 1
        items = first_page.get('items', [])
        
        print(f" -> Encontrados {total} resultados em {total_pages} páginas")
        
        for item in items:
            item_id = item.get('id') or item.get('numero_controle_pncp')
            if item_id and item_id not in all_processes:
                item['matched_terms'] = [term]
                all_processes[item_id] = item
            elif item_id and term not in all_processes[item_id]['matched_terms']:
                all_processes[item_id]['matched_terms'].append(term)
                
        # Paginate if more than 1 page
        max_p = 3 if term in ["Service Cloud", "Data 360"] else min(total_pages + 1, 5)
        for p in range(2, max_p + 1):
            page_data = fetch_pncp_search_page(session, term, page=p)
            if page_data:
                p_items = page_data.get('items', [])
                for item in p_items:
                    item_id = item.get('id') or item.get('numero_controle_pncp')
                    if item_id and item_id not in all_processes:
                        item['matched_terms'] = [term]
                        all_processes[item_id] = item
                    elif item_id and term not in all_processes[item_id]['matched_terms']:
                        all_processes[item_id]['matched_terms'].append(term)
                        
    result_list = list(all_processes.values())
    print(f"\n=== Varredura Concluída: {len(result_list)} processos mapeados ===")
    return result_list

if __name__ == '__main__':
    procs = fetch_all_salesforce_processes()
    print(f"Amostra do primeiro processo: {procs[0].get('title') if procs else 'Nenhum'}")
