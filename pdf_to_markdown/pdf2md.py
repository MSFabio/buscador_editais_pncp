# -*- coding: utf-8 -*-
"""
Conversor de PDF para Markdown com Suporte a OCR (Otimizado para Gemini e LLMs)

Transforma arquivos PDF (nativos e escaneados) em documentos Markdown (.md) leves,
estruturados e ideais para consumo por modelos de IA como o Google Gemini.
"""

import os
import sys
import time
import argparse
from pathlib import Path

# Ajustar encoding do terminal Windows para UTF-8 seguro
try:
    if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# Tentativa de importar Rich para interface rica no terminal
try:
    from rich.console import Console
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
    from rich.panel import Panel
    from rich import box
    RICH_AVAILABLE = True
    console = Console(force_terminal=True, legacy_windows=False)
except ImportError:
    RICH_AVAILABLE = False
    console = None

try:
    import pymupdf4llm
except ImportError:
    print("\n[ERRO CRÍTICO] A biblioteca 'pymupdf4llm' não está instalada.")
    print("Por favor, execute: pip install pymupdf4llm rapidocr-onnxruntime rich\n")
    sys.exit(1)


def format_bytes(size_in_bytes: int) -> str:
    """Formata bytes em unidades legíveis (B, KB, MB, GB)."""
    val = float(size_in_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if val < 1024.0:
            return f"{val:.1f} {unit}"
        val /= 1024.0
    return f"{val:.1f} TB"


def estimate_tokens(text: str) -> int:
    """Estimativa aproximada de tokens para LLMs (1 token ~ 4 caracteres)."""
    return max(1, len(text) // 4)


def convert_single_pdf(pdf_path: Path, force_ocr: bool = False, extract_images: bool = False) -> dict:
    """
    Converte um único arquivo PDF em Markdown e salva na mesma pasta.
    Retorna métricas de conversão.
    """
    md_path = pdf_path.with_suffix('.md')
    orig_size = pdf_path.stat().st_size
    start_t = time.perf_counter()
    
    try:
        img_folder = ""
        if extract_images:
            img_folder = str(pdf_path.parent / f"{pdf_path.stem}_images")

        # pymupdf4llm usa o backend RapidOCR automaticamente se o PDF for escaneado/imagem
        md_text = pymupdf4llm.to_markdown(
            str(pdf_path),
            force_ocr=force_ocr,
            write_images=extract_images,
            image_path=img_folder,
        )
        
        # Garante escrita estrita em UTF-8 para preservar acentos e caracteres especiais
        md_path.write_text(md_text, encoding='utf-8')
        elapsed = time.perf_counter() - start_t
        new_size = md_path.stat().st_size
        
        reduction = 0.0
        if orig_size > 0:
            reduction = max(0.0, (1.0 - (float(new_size) / float(orig_size))) * 100.0)
            
        return {
            'status': 'OK',
            'pdf_path': pdf_path,
            'md_path': md_path,
            'orig_size': orig_size,
            'new_size': new_size,
            'reduction': reduction,
            'tokens': estimate_tokens(md_text),
            'elapsed': elapsed,
            'error': None
        }
    except Exception as e:
        elapsed = time.perf_counter() - start_t
        return {
            'status': 'ERROR',
            'pdf_path': pdf_path,
            'md_path': md_path,
            'orig_size': orig_size,
            'new_size': 0,
            'reduction': 0.0,
            'tokens': 0,
            'elapsed': elapsed,
            'error': str(e)
        }


def print_banner():
    """Exibe cabeçalho no terminal."""
    title_text = (
        "[bold cyan]Conversor Inteligente de PDF para Markdown (OCR + LLM Ready)[/bold cyan]\n"
        "[dim]Gera arquivos .md leves e estruturados na mesma pasta para máxima eficiência no Gemini[/dim]"
    )
    if RICH_AVAILABLE:
        console.print(Panel(title_text, box=box.ROUNDED, expand=False, border_style="cyan"))
    else:
        print("=" * 70)
        print(" Conversor Inteligente de PDF para Markdown (OCR + LLM Ready)")
        print(" Gera arquivos .md leves na mesma pasta para uso eficiente com Gemini")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Converte PDFs de uma pasta para formato Markdown (.md) na mesma pasta com suporte a OCR."
    )
    parser.add_argument(
        "folder",
        nargs="?",
        default=None,
        help="Caminho da pasta que contém os arquivos PDF (ex: 'C:\\documentos')."
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Buscar arquivos PDF também dentro de todas as subpastas."
    )
    parser.add_argument(
        "--force-ocr",
        action="store_true",
        help="Forçar OCR em todas as páginas (mesmo com texto vetorial já presente)."
    )
    parser.add_argument(
        "--extract-images", "-i",
        action="store_true",
        help="Extrair e salvar imagens dos PDFs em pastas separadas."
    )

    args = parser.parse_args()
    print_banner()

    folder_str = args.folder
    if not folder_str:
        if RICH_AVAILABLE:
            console.print("\nDica: Você pode digitar, colar ou arrastar a pasta diretamente aqui no terminal.")
        else:
            print("\nDica: Você pode digitar ou colar o caminho da pasta diretamente abaixo.")
        
        try:
            folder_str = input("Pasta com os PDFs: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOperação cancelada pelo usuário.")
            sys.exit(0)

    # Limpeza de aspas que o Windows CMD/PowerShell adiciona ao arrastar/soltar
    folder_str = folder_str.strip('"').strip("'").strip()

    if not folder_str:
        if RICH_AVAILABLE:
            console.print("[bold red][ERRO][/bold red] Nenhum caminho foi informado.")
        else:
            print("[ERRO] Nenhum caminho foi informado.")
        sys.exit(1)

    folder = Path(folder_str)

    if not folder.exists():
        msg = f"[ERRO] A pasta informada não existe: {folder}"
        if RICH_AVAILABLE:
            console.print(f"[bold red]{msg}[/bold red]")
        else:
            print(msg)
        sys.exit(1)

    if not folder.is_dir():
        msg = f"[ERRO] O caminho informado não é um diretório: {folder}"
        if RICH_AVAILABLE:
            console.print(f"[bold red]{msg}[/bold red]")
        else:
            print(msg)
        sys.exit(1)

    # Busca de PDFs (maiúsculas e minúsculas)
    if args.recursive:
        found = list(folder.rglob("*.pdf")) + list(folder.rglob("*.PDF"))
    else:
        found = list(folder.glob("*.pdf")) + list(folder.glob("*.PDF"))

    # Remove duplicidades preservando a ordem
    pdf_files = list(dict.fromkeys(found))

    if not pdf_files:
        msg = f"[AVISO] Nenhum arquivo .pdf encontrado em: {folder}"
        if RICH_AVAILABLE:
            console.print(f"[yellow]{msg}[/yellow]")
        else:
            print(msg)
        sys.exit(0)

    if RICH_AVAILABLE:
        console.print(f"\n[bold green]Encontrado(s) {len(pdf_files)} arquivo(s) PDF para conversão.[/bold green]")
        console.print("[dim]Destino: os arquivos .md serão gerados na mesma pasta de origem.[/dim]\n")
    else:
        print(f"\nEncontrado(s) {len(pdf_files)} arquivo(s) PDF para conversão.")
        print("Destino: os arquivos .md serão gerados na mesma pasta de origem.\n")

    results = []

    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Processando documentos...", total=len(pdf_files))
            for pdf in pdf_files:
                progress.update(task, description=f"[cyan]Convertendo:[/] [yellow]{pdf.name}[/]")
                res = convert_single_pdf(pdf, force_ocr=args.force_ocr, extract_images=args.extract_images)
                results.append(res)
                progress.advance(task)
    else:
        for idx, pdf in enumerate(pdf_files, 1):
            print(f"[{idx}/{len(pdf_files)}] Convertendo: {pdf.name}...")
            res = convert_single_pdf(pdf, force_ocr=args.force_ocr, extract_images=args.extract_images)
            results.append(res)

    # Estatísticas
    success_count = sum(1 for r in results if r['status'] == 'OK')
    error_count = len(results) - success_count
    total_orig = sum(r['orig_size'] for r in results if r['status'] == 'OK')
    total_new = sum(r['new_size'] for r in results if r['status'] == 'OK')
    total_tokens = sum(r['tokens'] for r in results if r['status'] == 'OK')

    if RICH_AVAILABLE:
        table = Table(title="Resumo da Conversão de Arquivos", box=box.SIMPLE_HEAD)
        table.add_column("Arquivo PDF", style="cyan", no_wrap=False)
        table.add_column("Tam. PDF", justify="right", style="dim")
        table.add_column("Tam. Markdown", justify="right", style="bold green")
        table.add_column("Redução", justify="right", style="bold magenta")
        table.add_column("Tokens Est.", justify="right", style="blue")
        table.add_column("Status", justify="center")

        for r in results:
            if r['status'] == 'OK':
                table.add_row(
                    r['pdf_path'].name,
                    format_bytes(r['orig_size']),
                    format_bytes(r['new_size']),
                    f"{r['reduction']:.1f}%",
                    f"{r['tokens']:,}",
                    "[green][OK][/green]"
                )
            else:
                err_snippet = str(r['error'])[:30]
                table.add_row(
                    r['pdf_path'].name,
                    format_bytes(r['orig_size']),
                    "--",
                    "--",
                    "--",
                    f"[red][ERRO] {err_snippet}...[/red]"
                )
        console.print(table)

        total_reduction = 0.0
        if total_orig > 0:
            total_reduction = (1.0 - (float(total_new) / float(total_orig))) * 100.0

        summary = (
            f"[bold]Arquivos convertidos com sucesso:[/bold] [green]{success_count}/{len(results)}[/green]\n"
            f"[bold]Espaço original total:[/bold] {format_bytes(total_orig)}  ->  "
            f"[bold]Espaço em Markdown:[/bold] [green]{format_bytes(total_new)}[/green] "
            f"([bold magenta]{total_reduction:.1f}% menor[/bold magenta])\n"
            f"[bold]Total estimado de tokens para o Gemini:[/bold] [blue]{total_tokens:,} tokens[/blue]\n"
            f"[dim]Localização: salvos na mesma pasta de cada arquivo PDF correspondente.[/dim]"
        )
        if error_count > 0:
            summary += f"\n[bold red]Atenção: {error_count} arquivo(s) apresentaram erro durante a conversão.[/bold red]"

        console.print(Panel(summary, title="Otimizado para o Gemini", border_style="green"))
    else:
        print("\n" + "=" * 65)
        print("RESUMO DA CONVERSÃO:")
        print("=" * 65)
        for r in results:
            if r['status'] == 'OK':
                print(f"[OK] {r['pdf_path'].name}: {format_bytes(r['orig_size'])} -> {format_bytes(r['new_size'])} (-{r['reduction']:.1f}%) | ~{r['tokens']:,} tokens")
            else:
                print(f"[ERRO] {r['pdf_path'].name}: Falha -> {r['error']}")
        print("-" * 65)
        print(f"Convertidos: {success_count}/{len(results)}")
        if total_orig > 0:
            tot_red = (1.0 - (float(total_new) / float(total_orig))) * 100.0
            print(f"Tamanho total: {format_bytes(total_orig)} -> {format_bytes(total_new)} (-{tot_red:.1f}%)")
        print(f"Tokens aproximados para o Gemini: {total_tokens:,}")


if __name__ == '__main__':
    main()
