"""
Script Otimizado de Conversão do Processo SEI E-20/001.008552/2026 de PDF para Markdown
Extrai com alta performance e fidelidade todas as 661 páginas do processo SEI.
Gera tanto a versão individual por documento quanto o arquivo consolidado completo.
"""

import sys
import os
import re
import time
import pymupdf

sys.stdout.reconfigure(encoding='utf-8')

PDF_PATH = r"C:\Users\11429149760\Downloads\SEI_E_20_001.008552_2026.pdf"
OUTPUT_DIR = r"C:\Users\11429149760\.gemini\antigravity\scratch\analise_licitacao_telecom\markdown"

os.makedirs(OUTPUT_DIR, exist_ok=True)

SECTIONS = [
    {
        "id": "2215770",
        "file": "01_TR_2215770.md",
        "title": "Termo de Referência 2215770 (DPRJ)",
        "start": 1,
        "end": 21
    },
    {
        "id": "2219726",
        "file": "02_Proposta_GSNT_2219726.md",
        "title": "Proposta GSNT Telecom (2219726)",
        "start": 22,
        "end": 27
    },
    {
        "id": "2219727",
        "file": "03_Pregao_GO_107458_2025_2219727.md",
        "title": "Proposta Pregão 107458/2025 Secretaria Geral da Governadoria - GO (2219727)",
        "start": 28,
        "end": 111
    },
    {
        "id": "2219728",
        "file": "04_Pregao_MPES_90037_2025_2219728.md",
        "title": "Proposta Pregão 90037/2025 Ministério Público do Estado do Espírito Santo - ES (2219728)",
        "start": 112,
        "end": 183
    },
    {
        "id": "2219730",
        "file": "05_Pregao_DTI_PF_90009_2025_2219730.md",
        "title": "Proposta Pregão 90009/2025 Diretoria de Tecnologia da Informação e Inovação - PF (2219730)",
        "start": 184,
        "end": 284
    },
    {
        "id": "2219741",
        "file": "06_Pregao_MPRJ_90020_2024_2219741.md",
        "title": "Proposta Pregão 90020/2024 Ministério Público do Estado do Rio de Janeiro - RJ (2219741)",
        "start": 285,
        "end": 434
    },
    {
        "id": "2219742",
        "file": "07_Contrato_MTE_18_2024_Telebras_2219742.md",
        "title": "Proposta Contrato 18/2024 Ministério do Trabalho e Emprego / Telebras (2219742)",
        "start": 435,
        "end": 569
    },
    {
        "id": "2219745",
        "file": "08_CD_FUPESC_75_2025_2219745.md",
        "title": "Proposta CD 75/2025 Fundo Penitenciário do Estado de Santa Catarina - FUPESC (2219745)",
        "start": 570,
        "end": 603
    },
    {
        "id": "2219747",
        "file": "09_Pregao_TJMRS_2_2026_2219747.md",
        "title": "Proposta Pregão 2/2026 Justiça Militar do Estado do Rio Grande do Sul - RS (2219747)",
        "start": 604,
        "end": 655
    },
    {
        "id": "2219752",
        "file": "10_Proposta_Oi_Valor_Atual_2219752.md",
        "title": "Proposta Oi - Valor Atual Contratado DPRJ (2219752)",
        "start": 656,
        "end": 658
    },
    {
        "id": "2220599",
        "file": "11_Planilha_Orcamento_2220599.md",
        "title": "Planilha Orçamento (2220599)",
        "start": 659,
        "end": 659
    },
    {
        "id": "2220606",
        "file": "12_Despacho_2220606.md",
        "title": "Despacho da Coordenação de Planejamento e Pesquisa de Mercado (2220606)",
        "start": 660,
        "end": 661
    }
]

def format_table_as_markdown(table_data):
    if not table_data or len(table_data) == 0:
        return ""
    cleaned_rows = []
    for row in table_data:
        cleaned_row = []
        for cell in row:
            val = str(cell).strip().replace("\n", " ") if cell is not None else ""
            cleaned_row.append(val)
        cleaned_rows.append(cleaned_row)
    max_cols = max(len(r) for r in cleaned_rows)
    if max_cols == 0:
        return ""
    for r in cleaned_rows:
        while len(r) < max_cols:
            r.append("")
    header = cleaned_rows[0]
    separator = ["---"] * max_cols
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(separator) + " |"
    ]
    for row in cleaned_rows[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return "\n" + "\n".join(lines) + "\n"

def page_to_markdown_fast(page, page_num):
    """Converte página rapidamente preservando blocos de texto e tabelas críticas."""
    md_chunks = [f"\n\n<!-- Página {page_num} -->\n\n"]
    
    # Se for a página da planilha orçamentária ou se houver tabelas explícitas chave
    if page_num == 659 or page_num in [13, 14, 15, 23, 24, 657]:
        try:
            tabs = page.find_tables()
            if tabs and len(tabs.tables) > 0:
                for t in tabs.tables:
                    md_chunks.append(format_table_as_markdown(t.extract()))
                return "".join(md_chunks)
        except Exception:
            pass
            
    blocks = page.get_text("blocks")
    for b in blocks:
        if len(b) >= 5:
            text = b[4].strip()
            if not text:
                continue
            
            # Remover carimbo repetitivo SEI do rodapé
            if re.match(r"^SEI\s+E-20/001\.008552/2026\s*/\s*pg\.\s*\d+$", text):
                continue
                
            # Formatar títulos
            if re.match(r"^[0-9]+(\.[0-9]+)*\s+[A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇ\s\-–\(\)/]{4,}$", text):
                md_chunks.append(f"\n### {text}\n")
            elif re.match(r"^[A-ZÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇ\s\-–\(\)/]{5,}$", text) and len(text) < 70 and "\n" not in text:
                md_chunks.append(f"\n#### {text}\n")
            else:
                md_chunks.append(f"\n{text}\n")
                
    return "".join(md_chunks)

def run_conversion():
    t_start = time.time()
    print(f"Abrindo documento: {PDF_PATH}", flush=True)
    doc = pymupdf.open(PDF_PATH)
    total_pages = len(doc)
    print(f"Total de páginas no documento: {total_pages}", flush=True)
    
    consolidated_path = os.path.join(OUTPUT_DIR, "00_SEI_E_20_001.008552_2026_COMPLETO.md")
    all_md_parts = [
        f"# PROCESSO ADMINISTRATIVO SEI E-20/001.008552/2026\n\n",
        f"**Defensoria Pública do Estado do Rio de Janeiro - DPRJ**\n\n",
        f"**Total de Páginas**: {total_pages}\n\n",
        f"**Data de Conversão**: 2026-09-22\n\n",
        "---\n\n"
    ]
    
    for sec in SECTIONS:
        sec_title = sec["title"]
        sec_file = sec["file"]
        sec_id = sec["id"]
        start_p = sec["start"]
        end_p = sec["end"]
        
        t_sec = time.time()
        print(f"Processando [{sec_id}] {sec_title} (Páginas {start_p} a {end_p})...", end="", flush=True)
        sec_md = [
            f"# {sec_title}\n",
            f"**Identificador SEI**: {sec_id}\n",
            f"**Intervalo de Páginas no Processo**: {start_p} a {end_p} (Total: {end_p - start_p + 1} páginas)\n",
            f"**Órgão / Origem**: Processo E-20/001.008552/2026 - DPRJ\n\n---\n"
        ]
        
        for p_idx in range(start_p - 1, end_p):
            p = doc[p_idx]
            page_md = page_to_markdown_fast(p, p_idx + 1)
            sec_md.append(page_md)
            
        full_sec_text = "".join(sec_md)
        
        out_file_path = os.path.join(OUTPUT_DIR, sec_file)
        with open(out_file_path, "w", encoding="utf-8") as f:
            f.write(full_sec_text)
            
        dt = time.time() - t_sec
        print(f" OK ({len(full_sec_text):,} chars em {dt:.2f}s)", flush=True)
        
        all_md_parts.append(f"\n\n\n# ========================================================\n")
        all_md_parts.append(f"# SEÇÃO SEI: {sec_title}\n")
        all_md_parts.append(f"# ========================================================\n\n")
        all_md_parts.append(full_sec_text)
        
    print(f"\nSalvando arquivo consolidado completo...", flush=True)
    with open(consolidated_path, "w", encoding="utf-8") as f:
        f.write("".join(all_md_parts))
        
    total_time = time.time() - t_start
    print(f"\n Conversão de todas as 661 páginas concluída em {total_time:.2f} segundos!", flush=True)
    print(f"Arquivo mestre: {consolidated_path} ({os.path.getsize(consolidated_path):,} bytes)", flush=True)

if __name__ == "__main__":
    run_conversion()
