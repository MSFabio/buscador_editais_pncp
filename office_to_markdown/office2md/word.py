# -*- coding: utf-8 -*-
"""
Módulo de Conversão de Documentos Word (.docx) para Markdown.
"""

from pathlib import Path
from typing import Union, Optional
import docx
from docx.text.paragraph import Paragraph
from docx.table import Table


def _format_run(run) -> str:
    """Formata um trecho de texto (Run) aplicando negrito, itálico, tachado e código."""
    text = run.text
    if not text:
        return ""
    
    # Preserva espaços externos para não colar palavras
    leading_space = " " if text.startswith(" ") and not text.isspace() else ""
    trailing_space = " " if text.endswith(" ") and not text.isspace() else ""
    stripped = text.strip()
    if not stripped:
        return text

    # Formatação de código / fonte monoespaçada
    font_name = (run.font.name or "").lower()
    if any(m in font_name for m in ["consolas", "courier", "monospace", "code"]):
        stripped = f"`{stripped}`"

    # Negrito e Itálico
    if run.bold and run.italic:
        stripped = f"***{stripped}***"
    elif run.bold:
        stripped = f"**{stripped}**"
    elif run.italic:
        stripped = f"*{stripped}*"

    # Tachado (strikethrough)
    if getattr(run.font, "strike", False):
        stripped = f"~~{stripped}~~"

    return f"{leading_space}{stripped}{trailing_space}"


def _format_paragraph(p: Paragraph) -> str:
    """Converte um parágrafo do Word em linha formatada em Markdown."""
    style_name = p.style.name.lower() if p.style and p.style.name else ""
    
    # Processa os runs com formatação
    parts = []
    for run in p.runs:
        parts.append(_format_run(run))
    text = "".join(parts).strip()

    if not text:
        return ""

    # Mapeamento de Títulos / Headings
    if "title" in style_name and "sub" not in style_name:
        return f"# {text}\n"
    elif "subtitle" in style_name:
        return f"## {text}\n"
    elif "heading 1" in style_name or "título 1" in style_name:
        return f"# {text}\n"
    elif "heading 2" in style_name or "título 2" in style_name:
        return f"## {text}\n"
    elif "heading 3" in style_name or "título 3" in style_name:
        return f"### {text}\n"
    elif "heading 4" in style_name or "título 4" in style_name:
        return f"#### {text}\n"
    elif "heading 5" in style_name or "título 5" in style_name:
        return f"##### {text}\n"
    
    # Listas
    if "list bullet" in style_name or "marcador" in style_name:
        return f"- {text}"
    elif "list number" in style_name or "número" in style_name or "numerada" in style_name:
        return f"1. {text}"
    elif "quote" in style_name or "citação" in style_name:
        return f"> {text}"

    return text


def _clean_cell_text(text: str) -> str:
    """Limpa e escapa o texto de uma célula de tabela para Markdown."""
    if not text:
        return ""
    # Quebras de linha internas são convertidas para <br>
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    cleaned = "<br>".join(lines)
    # Escapa pipes | que quebrariam a tabela Markdown
    cleaned = cleaned.replace("|", "\\|")
    return cleaned.strip()


def _format_table(table: Table) -> str:
    """Converte uma tabela Word em tabela Markdown formatada."""
    if not table.rows:
        return ""

    rows_data = []
    max_cols = max(len(row.cells) for row in table.rows)

    for row in table.rows:
        row_cells = [_clean_cell_text(cell.text) for cell in row.cells]
        # Preenche se alguma linha tiver menos células
        while len(row_cells) < max_cols:
            row_cells.append("")
        rows_data.append(row_cells)

    if not rows_data:
        return ""

    # Cabeçalho da tabela (primeira linha)
    headers = rows_data[0]
    # Se todos os cabeçalhos forem vazios, preenche com Coluna 1, Coluna 2...
    if all(not h for h in headers):
        headers = [f"Coluna {i+1}" for i in range(len(headers))]

    md_lines = []
    md_lines.append("| " + " | ".join(headers) + " |")
    md_lines.append("| " + " | ".join([":---"] * len(headers)) + " |")

    # Linhas de dados
    for row in rows_data[1:]:
        md_lines.append("| " + " | ".join(row) + " |")

    return "\n".join(md_lines) + "\n"


def convert_word_native(file_path: Union[str, Path]) -> str:
    """Converte DOCX usando o motor nativo python-docx com preservação de fluxo."""
    doc = docx.Document(str(file_path))
    md_parts = []

    for item in doc.iter_inner_content():
        if isinstance(item, Paragraph):
            line = _format_paragraph(item)
            if line:
                md_parts.append(line)
        elif isinstance(item, Table):
            tbl_md = _format_table(item)
            if tbl_md:
                md_parts.append(tbl_md)

    return "\n\n".join(md_parts).strip() + "\n"


def convert_word_mammoth(file_path: Union[str, Path]) -> str:
    """Converte DOCX via Mammoth + Markdownify (excelente para HTML semântico)."""
    import mammoth
    import markdownify
    with open(str(file_path), "rb") as f:
        html_result = mammoth.convert_to_html(f)
        return markdownify.markdownify(html_result.value, heading_style="ATX").strip() + "\n"


def convert_word_to_markdown(
    file_path: Union[str, Path],
    engine: str = "native"
) -> str:
    """
    Converte um arquivo Word (.docx) para Markdown (.md).
    
    Args:
        file_path: Caminho do arquivo .docx
        engine: 'native' (python-docx, recomendado) ou 'mammoth'
        
    Returns:
        String contendo o texto em formato Markdown
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Arquivo Word não encontrado: {path}")

    ext = path.suffix.lower()
    if ext not in [".docx", ".doc"]:
        raise ValueError(f"Extensão não suportada para Word: {ext}. Utilize .docx")

    if ext == ".doc":
        raise NotImplementedError(
            "Arquivos no formato legado .doc (Word 97-2003) devem ser salvos como .docx antes da conversão."
        )

    if engine == "mammoth":
        return convert_word_mammoth(path)
    else:
        try:
            return convert_word_native(path)
        except Exception:
            # Fallback automático para mammoth
            return convert_word_mammoth(path)
