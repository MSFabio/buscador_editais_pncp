import sys
import os
import json
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add directory to sys.path
CRAWLER_DIR = Path(r"C:\Users\11429149760\.gemini\antigravity\scratch\salesforce_tr_crawler")
sys.path.insert(0, str(CRAWLER_DIR))

from salesforce_tr_search import fetch_all_salesforce_processes, get_pncp_session
from tr_downloader_extractor import process_item_downloads_and_extraction
from tr_analyzer import analyze_salesforce_tr
from generate_tr_report import generate_html_report, generate_markdown_summary

def process_single_item(args):
    item, session = args
    extraction_res = process_item_downloads_and_extraction(session, item)
    analysis_res = analyze_salesforce_tr(item, extraction_res)
    
    if not analysis_res:
        return None # Rejected false positive (e.g. Adobe Creative Cloud)
        
    return {
        'id': item.get('id'),
        'title': item.get('title'),
        'orgao_nome': item.get('orgao_nome'),
        'orgao_cnpj': item.get('orgao_cnpj'),
        'uf': item.get('uf'),
        'municipio_nome': item.get('municipio_nome'),
        'description': item.get('description'),
        'numero_controle_pncp': item.get('numero_controle_pncp'),
        'data_publicacao_pncp': item.get('data_publicacao_pncp'),
        'matched_terms': item.get('matched_terms', []),
        'extraction': extraction_res,
        'analysis': analysis_res
    }

def main():
    print("=" * 60)
    print("      INICIANDO VARREDURA REFINADA (ESTRITA SALESFORCE)      ")
    print("=" * 60)
    
    # 1. Fetch search processes
    processes = fetch_all_salesforce_processes()
    print(f"\n[OK] Mapeados {len(processes)} candidatos iniciais no PNCP.")
    
    session = get_pncp_session()
    consolidated_data = []
    
    # Filter processes (last 3 years: 2023 - 2026)
    filtered_processes = []
    for item in processes:
        dt = item.get('data_publicacao_pncp') or ""
        year = item.get('ano')
        if year and int(year) >= 2023:
            filtered_processes.append(item)
        elif dt and any(y in dt for y in ['2023', '2024', '2025', '2026']):
            filtered_processes.append(item)
        elif not year and not dt:
            filtered_processes.append(item)
            
    print(f"[FILTRO 3 ANOS] {len(filtered_processes)} processos selecionados para análise profunda (2023-2026).")
    
    # 2. Multi-threaded Download & Extract with Strict Salesforce Filtering
    print(f"\n[EXECUÇÃO PARALELA E FILTRAGEM] Baixando, analisando e filtrando apenas SALESFORCE...")
    tasks = [(item, session) for item in filtered_processes]
    
    rejected_count = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_single_item, t) for t in tasks]
        for future in as_completed(futures):
            try:
                res = future.result()
                if res:
                    consolidated_data.append(res)
                    print(f" -> [SALESFORCE VALIDADO] {res['title']} | {res['orgao_nome']}")
                else:
                    rejected_count += 1
            except Exception as e:
                print(f" -> Erro no processamento de item: {e}")
                
    print(f"\n[RESULTADO FILTRAGEM] {len(consolidated_data)} processos validados como SALESFORCE estrito ({rejected_count} falsos positivos ignorados).")
    
    # Sort by date descending
    consolidated_data.sort(key=lambda x: x.get('data_publicacao_pncp') or "", reverse=True)
    
    # 3. Save JSON
    json_path = CRAWLER_DIR / "salesforce_tr_data.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(consolidated_data, f, ensure_ascii=False, indent=2)
        
    print(f"\n[OK] Dados consolidados salvos em: {json_path}")
    
    # 4. Generate HTML and Markdown Reports
    html_path = CRAWLER_DIR / "salesforce_tr_report.html"
    md_path = CRAWLER_DIR / "salesforce_tr_summary.md"
    
    generate_html_report(consolidated_data, html_path)
    generate_markdown_summary(consolidated_data, md_path)
    
    print("\n" + "=" * 60)
    print(f"   VARREDURA REFINADA DE {len(consolidated_data)} PROCESSOS SALESFORCE CONCLUÍDA!   ")
    print("=" * 60)

if __name__ == '__main__':
    main()
