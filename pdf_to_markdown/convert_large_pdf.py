# -*- coding: utf-8 -*-
"""
Conversor Robusto para PDFs Grandes (com Processamento em Lotes e OCR)
"""

import os
import sys
import time
from pathlib import Path

# Configuração de encoding para UTF-8 no Windows
try:
    if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

import pymupdf
import pymupdf4llm

def format_bytes(size: float) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def main():
    pdf_path = Path(r"C:\Users\11429149760\Desktop\pregões - pesquisa de preços - renovação K2\SEI_E_20_001.001992_2024.pdf")
    md_path = pdf_path.with_suffix(".md")

    if not pdf_path.exists():
        print(f"Erro: Arquivo não encontrado: {pdf_path}")
        sys.exit(1)

    orig_size = pdf_path.stat().st_size
    doc = pymupdf.open(str(pdf_path))
    total_pages = len(doc)
    doc.close()

    print(f"\n=======================================================")
    print(f" Início da conversão de PDF Grande")
    print(f" Arquivo: {pdf_path.name}")
    print(f" Total de páginas: {total_pages}")
    print(f" Tamanho original: {format_bytes(orig_size)}")
    print(f" Destino: {md_path.name}")
    print(f"=======================================================\n")

    chunk_size = 50
    start_total = time.time()
    
    # Inicia ou limpa o arquivo Markdown
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(f"# Processo Administrativo SEI: {pdf_path.stem}\n\n")
        f.write(f"> Documento original com {total_pages} páginas convertido para Markdown para uso com Gemini.\n\n---\n\n")

    total_chunks = (total_pages + chunk_size - 1) // chunk_size

    for chunk_idx in range(total_chunks):
        start_page = chunk_idx * chunk_size
        end_page = min(start_page + chunk_size, total_pages)
        pages_to_extract = list(range(start_page, end_page))

        t0 = time.time()
        print(f"[{chunk_idx + 1}/{total_chunks}] Processando páginas {start_page + 1} até {end_page} ({end_page}/{total_pages} - {end_page*100/total_pages:.1f}%)...", flush=True)

        try:
            chunk_md = pymupdf4llm.to_markdown(str(pdf_path), pages=pages_to_extract)
            with open(md_path, 'a', encoding='utf-8') as f:
                f.write(f"\n\n<!-- PÁGINAS {start_page + 1} A {end_page} -->\n\n")
                f.write(chunk_md)
            
            elapsed_chunk = time.time() - t0
            current_md_size = md_path.stat().st_size
            print(f"    ✔ Lote concluído em {elapsed_chunk:.1f}s | Tamanho acumulado MD: {format_bytes(current_md_size)}", flush=True)
        except Exception as e:
            print(f"    ❌ Erro no lote {start_page + 1}-{end_page}: {e}", flush=True)
            with open(md_path, 'a', encoding='utf-8') as f:
                f.write(f"\n\n<!-- AVISO: Erro na conversão das páginas {start_page + 1} a {end_page}: {e} -->\n\n")

    total_time = time.time() - start_total
    final_size = md_path.stat().st_size
    reduction = max(0.0, (1.0 - (final_size / orig_size)) * 100.0)

    # Estimativa de tokens
    tokens_est = final_size // 4

    print(f"\n=======================================================")
    print(f" CONVERSÃO FINALIZADA COM SUCESSO!")
    print(f" Tempo total: {total_time/60:.1f} minutos ({total_time:.1f}s)")
    print(f" Tamanho original: {format_bytes(orig_size)}")
    print(f" Tamanho final Markdown: {format_bytes(final_size)} ({reduction:.1f}% menor)")
    print(f" Tokens estimados para o Gemini: ~{tokens_est:,} tokens")
    print(f" Arquivo salvo em: {md_path}")
    print(f"=======================================================\n")

if __name__ == '__main__':
    main()
