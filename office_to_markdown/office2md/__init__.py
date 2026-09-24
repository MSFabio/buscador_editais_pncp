# -*- coding: utf-8 -*-
"""
office2md - Biblioteca para conversão de arquivos Word e Excel em Markdown (Otimizado para LLMs e Gemini).
"""

from .word import convert_word_to_markdown
from .excel import convert_excel_to_markdown
from .converter import (
    convert_file,
    convert_folder,
    OfficeConverter,
    SUPPORTED_EXTENSIONS,
    estimate_tokens,
    format_bytes
)

__version__ = "1.0.0"
__all__ = [
    "convert_word_to_markdown",
    "convert_excel_to_markdown",
    "convert_file",
    "convert_folder",
    "OfficeConverter",
    "SUPPORTED_EXTENSIONS",
    "estimate_tokens",
    "format_bytes"
]
