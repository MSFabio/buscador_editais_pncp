# -*- coding: utf-8 -*-
"""
Conversor Central Unificado de Arquivos Office (Word e Excel) para Markdown.
"""

from pathlib import Path
from typing import Union, List, Optional, Dict, Any
import time

from .word import convert_word_to_markdown
from .excel import convert_excel_to_markdown

SUPPORTED_EXTENSIONS = {
    ".docx": "Word (.docx)",
    ".xlsx": "Excel (.xlsx)",
    ".xls": "Excel Legado (.xls)",
    ".csv": "Planilha CSV (.csv)"
}


def estimate_tokens(text: str) -> int:
    """Estimativa de tokens para modelos de LLM (regra prática de 1 token ~ 4 caracteres)."""
    return max(1, len(text) // 4)


def format_bytes(size: float) -> str:
    """Formata bytes para exibição legível."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def convert_file(
    file_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    save_same_folder: bool = True
) -> Dict[str, Any]:
    """
    Converte um arquivo Word (.docx) ou Excel (.xlsx, .xls, .csv) para Markdown (.md).
    Por padrão, salva o novo arquivo .md na mesma pasta com o mesmo nome.

    Args:
        file_path: Caminho do arquivo de origem
        output_path: Caminho customizado para salvar o .md (opcional)
        save_same_folder: Se True e output_path não for informado, salva na mesma pasta

    Returns:
        Dicionário com status, métricas e o texto markdown gerado.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Extensão não suportada: {ext}. Formatos aceitos: {list(SUPPORTED_EXTENSIONS.keys())}")

    orig_size = path.stat().st_size
    start_t = time.perf_counter()

    try:
        if ext == ".docx":
            md_content = convert_word_to_markdown(path)
        elif ext in [".xlsx", ".xls", ".csv"]:
            md_content = convert_excel_to_markdown(path)
        else:
            raise ValueError(f"Tipo não implementado: {ext}")

        # Determina o caminho de saída
        if output_path:
            target_md = Path(output_path)
        elif save_same_folder:
            target_md = path.with_suffix(".md")
        else:
            target_md = None

        new_size = 0
        if target_md:
            target_md.write_text(md_content, encoding="utf-8")
            new_size = target_md.stat().st_size

        elapsed = time.perf_counter() - start_t
        reduction = max(0.0, (1.0 - (float(new_size) / float(orig_size))) * 100.0) if orig_size > 0 else 0.0

        return {
            "status": "OK",
            "file_path": path,
            "md_path": target_md,
            "orig_size": orig_size,
            "new_size": new_size,
            "reduction": reduction,
            "tokens": estimate_tokens(md_content),
            "elapsed": elapsed,
            "content": md_content,
            "error": None
        }

    except Exception as e:
        elapsed = time.perf_counter() - start_t
        return {
            "status": "ERROR",
            "file_path": path,
            "md_path": None,
            "orig_size": orig_size,
            "new_size": 0,
            "reduction": 0.0,
            "tokens": 0,
            "elapsed": elapsed,
            "content": "",
            "error": str(e)
        }


def convert_folder(
    folder_path: Union[str, Path],
    recursive: bool = False,
    extensions: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Localiza e converte todos os arquivos Word e Excel de uma pasta para Markdown,
    salvando os arquivos .md gerados na mesma pasta de cada arquivo de origem.

    Args:
        folder_path: Caminho da pasta
        recursive: Se True, varre também subdiretórios
        extensions: Lista de extensões filtradas (padrão: ['.docx', '.xlsx', '.xls', '.csv'])

    Returns:
        Lista com o resultado da conversão de cada arquivo
    """
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise NotADirectoryError(f"Diretório inválido: {folder}")

    if not extensions:
        extensions = list(SUPPORTED_EXTENSIONS.keys())
    else:
        extensions = [e.lower() if e.startswith(".") else f".{e.lower()}" for e in extensions]

    files_to_process = []
    for ext in extensions:
        pattern = f"*{ext}"
        if recursive:
            files_to_process.extend(folder.rglob(pattern))
            files_to_process.extend(folder.rglob(pattern.upper()))
        else:
            files_to_process.extend(folder.glob(pattern))
            files_to_process.extend(folder.glob(pattern.upper()))

    # Remove duplicados preservando a ordem
    unique_files = sorted(list(dict.fromkeys(files_to_process)))

    results = []
    for f in unique_files:
        res = convert_file(f, save_same_folder=True)
        results.append(res)

    return results


class OfficeConverter:
    """Classe controladora para conversões personalizadas e integração em pipelines."""

    def __init__(self, save_same_folder: bool = True):
        self.save_same_folder = save_same_folder

    def convert(self, file_or_folder: Union[str, Path], recursive: bool = False):
        p = Path(file_or_folder)
        if p.is_dir():
            return convert_folder(p, recursive=recursive)
        return convert_file(p, save_same_folder=self.save_same_folder)
