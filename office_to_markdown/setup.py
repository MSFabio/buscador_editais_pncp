from setuptools import setup, find_packages

setup(
    name="office2md",
    version="1.0.0",
    description="Biblioteca para transformar arquivos Word (.docx) e Excel (.xlsx, .xls) em Markdown limpo para LLMs e Gemini.",
    author="Antigravity",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "python-docx>=1.1.0",
        "openpyxl>=3.1.0",
        "pandas>=2.0.0",
        "xlrd>=2.0.0",
        "mammoth>=1.8.0",
        "markdownify>=0.12.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "office2md=office2md.cli:main",
        ],
    },
)
