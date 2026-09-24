# -*- coding: utf-8 -*-
"""
Interface de Linha de Comando (CLI) para office2md.
"""

import sys
import argparse
from pathlib import Path

# Ajuste de codificação UTF-8 para console Windows
try:
    if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

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

from .converter import convert_file, convert_folder, format_bytes, SUPPORTED_EXTENSIONS


def print_banner():
    """Exibe cabeçalho informativo no terminal."""
    msg = (
        "[bold cyan]office2md - Conversor de Word e Excel para Markdown[/bold cyan]\n"
        "[dim]Gera arquivos .md leves e estruturados na mesma pasta para máxima eficiência no Gemini[/dim]"
    )
    if RICH_AVAILABLE:
        console.print(Panel(msg, box=box.ROUNDED, expand=False, border_style="cyan"))
    else:
        print("=" * 70)
        print(" office2md - Conversor de Word e Excel para Markdown (LLM / Gemini)")
        print("=" * 70)


def main():
    parser = argparse.ArgumentParser(
        description="Converte arquivos Word (.docx) e Excel (.xlsx, .xls) para Markdown (.md) na mesma pasta."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=None,
        help="Caminho da pasta ou do arquivo individual (.docx, .xlsx, .xls, .csv)."
    )
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Buscar arquivos também dentro de todas as subpastas."
    )
    parser.add_argument(
        "--type", "-t",
        choices=["all", "word", "excel"],
        default="all",
        help="Filtrar por tipo de arquivo: 'word' (.docx), 'excel' (.xlsx, .xls) ou 'all' (padrão)."
    )

    args = parser.parse_args()
    print_banner()

    target_str = args.target
    if not target_str:
        if RICH_AVAILABLE:
            console.print("\n[yellow]Dica:[/yellow] Você pode digitar, colar ou arrastar a pasta/arquivo diretamente aqui.")
        else:
            print("\nDica: Você pode digitar ou colar o caminho diretamente abaixo.")

        try:
            target_str = input("📂 Digite ou cole o caminho da pasta ou arquivo: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOperação cancelada pelo usuário.")
            sys.exit(0)

    # Limpeza de aspas que o Windows CMD/PowerShell adiciona ao arrastar/soltar
    target_str = target_str.strip('"').strip("'").strip()
    if not target_str:
        print("[ERRO] Nenhum caminho informado.")
        sys.exit(1)

    target_path = Path(target_str)
    if not target_path.exists():
        print(f"[ERRO] Caminho inexistente: {target_path}")
        sys.exit(1)

    # Define extensões filtradas
    if args.type == "word":
        exts = [".docx"]
    elif args.type == "excel":
        exts = [".xlsx", ".xls", ".csv"]
    else:
        exts = list(SUPPORTED_EXTENSIONS.keys())

    # Processamento individual ou em lote
    if target_path.is_file():
        results = [convert_file(target_path, save_same_folder=True)]
    else:
        results = convert_folder(target_path, recursive=args.recursive, extensions=exts)

    if not results:
        msg = f"[AVISO] Nenhum arquivo compatível ({', '.join(exts)}) encontrado em: {target_path}"
        if RICH_AVAILABLE:
            console.print(f"[yellow]{msg}[/yellow]")
        else:
            print(msg)
        sys.exit(0)

    # Exibição dos resultados
    success_count = sum(1 for r in results if r["status"] == "OK")
    error_count = len(results) - success_count
    total_orig = sum(r["orig_size"] for r in results if r["status"] == "OK")
    total_new = sum(r["new_size"] for r in results if r["status"] == "OK")
    total_tokens = sum(r["tokens"] for r in results if r["status"] == "OK")

    if RICH_AVAILABLE:
        table = Table(title="📊 Resumo da Conversão Office ➡️ Markdown", box=box.SIMPLE_HEAD)
        table.add_column("Arquivo Original", style="cyan", no_wrap=False)
        table.add_column("Formato", style="dim")
        table.add_column("Tamanho Original", justify="right", style="dim")
        table.add_column("Markdown Gerado", justify="right", style="bold green")
        table.add_column("Redução", justify="right", style="bold magenta")
        table.add_column("Tokens Est.", justify="right", style="blue")
        table.add_column("Status", justify="center")

        for r in results:
            ext = r["file_path"].suffix.lower()
            tipo = SUPPORTED_EXTENSIONS.get(ext, ext)
            if r["status"] == "OK":
                table.add_row(
                    r["file_path"].name,
                    tipo,
                    format_bytes(r["orig_size"]),
                    format_bytes(r["new_size"]),
                    f"{r['reduction']:.1f}%",
                    f"{r['tokens']:,}",
                    "[green]✔ Concluído[/green]"
                )
            else:
                err_snippet = str(r["error"])[:30]
                table.add_row(
                    r["file_path"].name,
                    tipo,
                    format_bytes(r["orig_size"]),
                    "--",
                    "--",
                    "--",
                    f"[red]❌ Erro: {err_snippet}...[/red]"
                )
        console.print(table)

        total_reduction = 0.0
        if total_orig > 0:
            total_reduction = (1.0 - (float(total_new) / float(total_orig))) * 100.0

        summary = (
            f"[bold]Arquivos convertidos com sucesso:[/bold] [green]{success_count}/{len(results)}[/green]\n"
            f"[bold]Espaço original total:[/bold] {format_bytes(total_orig)}  ➡️  "
            f"[bold]Espaço em Markdown:[/bold] [green]{format_bytes(total_new)}[/green] "
            f"([bold magenta]{total_reduction:.1f}% menor[/bold magenta])\n"
            f"[bold]Total estimado de tokens para o Gemini:[/bold] [blue]{total_tokens:,} tokens[/blue]\n"
            f"[dim]Localização: os arquivos .md foram salvos na mesma pasta de cada documento.[/dim]"
        )
        if error_count > 0:
            summary += f"\n[bold red]Atenção: {error_count} arquivo(s) apresentaram erro.[/bold red]"

        console.print(Panel(summary, title="🚀 Otimizado para o Gemini", border_style="green"))
    else:
        print("\n" + "=" * 65)
        print("RESUMO DA CONVERSÃO:")
        print("=" * 65)
        for r in results:
            if r["status"] == "OK":
                print(f"✔ {r['file_path'].name}: {format_bytes(r['orig_size'])} -> {format_bytes(r['new_size'])} (-{r['reduction']:.1f}%) | ~{r['tokens']:,} tokens")
            else:
                print(f"❌ {r['file_path'].name}: Falha -> {r['error']}")
        print("-" * 65)
        print(f"Convertidos: {success_count}/{len(results)}")
        if total_orig > 0:
            tot_red = (1.0 - (float(total_new) / float(total_orig))) * 100.0
            print(f"Tamanho total: {format_bytes(total_orig)} -> {format_bytes(total_new)} (-{tot_red:.1f}%)")
        print(f"Tokens aproximados para o Gemini: ~{total_tokens:,}")


if __name__ == "__main__":
    main()
