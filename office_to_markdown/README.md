# office2md 📄📊 ➡️ 📝

**office2md** é uma biblioteca Python e ferramenta de linha de comando (CLI) desenvolvida para converter arquivos **Microsoft Word (.docx)** e **Excel (.xlsx, .xls, .csv)** em formato **Markdown (.md)** leve, estruturado e otimizado para consumo por Inteligências Artificiais como o **Google Gemini**, Claude e GPT.

---

## 🎯 Por que converter Word e Excel para Markdown para o Gemini?

1. **Economia Massiva de Tokens (80% a 98% de redução)**:
   - Arquivos `.docx` e `.xlsx` contêm metadados XML pesados, esquemas de fontes, propriedades visuais e tabelas de estilos que gastam milhares de tokens desnecessários.
   - O Markdown entrega apenas a essência textual e estrutural dos dados.
2. **Eliminação de Alucinações em Tabelas**:
   - Planilhas e tabelas são convertidas na sintaxe padrão de tabelas Markdown (`| Coluna 1 | Coluna 2 |`), permitindo que o Gemini realize cruzamento de dados, médias e análises com máxima precisão.
3. **Múltiplas Abas do Excel Organizadas**:
   - Cada planilha da pasta de trabalho é separada com títulos semânticos (`## Planilha: NomeDaAba`), mantendo o contexto claro para a IA.
4. **Fórmulas Avaliadas**:
   - O conversor extrai os valores finais calculados pelas fórmulas das planilhas, em vez de repassar a fórmula crua como `=SOMA(...)`.

---

## 🚀 Instalação

Como a biblioteca já foi instalada no ambiente local:
```bash
pip install -e C:\Users\11429149760\.gemini\antigravity\scratch\office_to_markdown
```

Ou instale as dependências via requirements:
```bash
pip install -r requirements.txt
```

---

## 💻 Como Usar via Terminal (CLI)

A ferramenta pode ser executada diretamente pelo comando `office2md` ou via `python -m office2md`.

### 1. Modo Interativo (Arrastar e Soltar)
Basta rodar no terminal sem argumentos:
```bash
office2md
```
O terminal solicitará a pasta ou arquivo:
```text
📂 Digite ou cole o caminho da pasta ou arquivo:
```
*(Você pode simplesmente arrastar a pasta do Windows Explorer e soltá-la dentro do terminal).*

### 2. Converter todos os arquivos de uma pasta
```bash
office2md "C:\Caminho\Para\Sua\Pasta"
```
*Todos os arquivos `.docx`, `.xlsx`, `.xls` e `.csv` serão convertidos e salvos como `.md` na mesma pasta.*

### 3. Converter incluindo subpastas (Recursivo)
```bash
office2md "C:\Caminho\Para\Sua\Pasta" --recursive
```

### 4. Filtrar apenas Word ou apenas Excel
```bash
# Somente arquivos Word (.docx)
office2md "C:\Caminho\Para\Sua\Pasta" --type word

# Somente planilhas Excel (.xlsx, .xls)
office2md "C:\Caminho\Para\Sua\Pasta" --type excel
```

### 5. Converter um arquivo individual
```bash
office2md "C:\Caminho\Para\relatorio.docx"
```

---

## 🐍 Como Usar como Biblioteca Python

Você pode importar e utilizar as funções diretamente no seu código Python:

```python
from office2md import (
    convert_word_to_markdown,
    convert_excel_to_markdown,
    convert_file,
    convert_folder
)

# 1. Obter a string Markdown de um documento Word
md_texto = convert_word_to_markdown("contrato.docx")
print(md_texto)

# 2. Obter a string Markdown de uma planilha Excel
md_planilha = convert_excel_to_markdown("orcamento.xlsx")
print(md_planilha)

# 3. Converter um arquivo e salvar o .md na mesma pasta
resultado = convert_file("especificacao_tecnica.docx")
print(f"Salvo em: {resultado['md_path']} | Tokens salvos: ~{resultado['tokens']}")

# 4. Converter uma pasta inteira em lote
resultados = convert_folder("C:/MeusDocumentos", recursive=True)
for r in resultados:
    if r["status"] == "OK":
        print(f"✔ {r['file_path'].name} -> {r['md_path'].name} (-{r['reduction']:.1f}%)")
```

---

## 📋 Recursos e Formatações Preservadas

### 📄 Microsoft Word (`.docx`):
- **Títulos**: Heading 1 (`#`), Heading 2 (`##`), Heading 3 (`###`), Title e Subtitle.
- **Formatação de Texto**: Negrito (`**texto**`), Itálico (`*texto*`), Tachado (`~~texto~~`) e Código (`texto em fonte monoespaçada`).
- **Listas**: Marcadores (`- item`) e Listas Numeradas (`1. item`).
- **Citações**: Blocos de citação (`> citação`).
- **Tabelas**: Linhas e colunas completas, com cabeçalhos e quebras de linha em células preservadas via `<br>`.

### 📊 Microsoft Excel (`.xlsx`, `.xls`, `.csv`):
- **Multi-abas**: Varre todas as abas da pasta de trabalho e cria seções individuais.
- **Limpeza Inteligente de Bordas**: Remove linhas e colunas vazias em excesso para não gerar tabelas gigantes de células em branco.
- **Datas e Horas**: Formatação amigável (`YYYY-MM-DD`).
- **Fórmulas Avaliadas**: Lê os resultados numéricos calculados pelo Excel.
