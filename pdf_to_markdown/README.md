# Conversor de PDF para Markdown com Suporte a OCR (Otimizado para Gemini)

Esta aplicação converte em lote arquivos PDF (tanto com texto nativo quanto digitalizados/escaneados via OCR) para o formato Markdown (`.md`), salvando os arquivos gerados diretamente na mesma pasta de origem.

---

## 🎯 Por que converter PDF em Markdown para o Gemini?

1. **Economia Massiva de Tokens (90% a 99% de redução)**:
   - O Gemini processa PDFs brutos como páginas renderizadas em imagem (centenas ou milhares de tokens por página).
   - O Markdown é texto puro sem metadados binários ou overhead visual.
2. **Preservação de Estrutura Semântica**:
   - Títulos (`#`, `##`), tabelas estruturadas em Markdown (`| Coluna 1 | Coluna 2 |`), listas e negritos são preservados com precisão.
3. **Velocidade e Custo**:
   - Respostas do modelo mais rápidas, menor latência e menor risco de atingir limites de taxa (rate limits).

---

## 🛠️ Bibliotecas Utilizadas

- **`pymupdf4llm`**: Criada pelo time do PyMuPDF especificamente para converter documentos para RAG e LLMs, preservando títulos, tabelas estruturadas e fluxo de leitura.
- **`rapidocr-onnxruntime`**: Motor de OCR 100% autônomo baseado em ONNX Runtime. Converte PDFs escaneados ou imagens sem precisar de binários externos ou instaladores de C++ (como o Tesseract).
- **`rich`**: Interface de terminal com barras de progresso, tabelas de status e métricas de redução.

---

## 🚀 Como Usar

### 1. Instalação das Dependências
No seu terminal ou PowerShell:
```bash
pip install -r requirements.txt
```

### 2. Executando a Conversão

#### Opção A: Modo Interativo (Basta rodar e colar a pasta)
```bash
python pdf2md.py
```
O terminal solicitará:
```text
📂 Digite ou cole o caminho da pasta com os PDFs:
```
*(Você pode simplesmente arrastar a pasta do Windows Explorer e soltá-la dentro do terminal).*

#### Opção B: Passando o caminho diretamente como argumento
```bash
python pdf2md.py "C:\Caminho\Para\Sua\Pasta"
```

#### Opção C: Incluir subpastas (Recursivo)
```bash
python pdf2md.py "C:\Caminho\Para\Sua\Pasta" --recursive
```

#### Opção D: Forçar OCR em todas as páginas
```bash
python pdf2md.py "C:\Caminho\Para\Sua\Pasta" --force-ocr
```

---

## 📁 Onde os arquivos são salvos?
Os novos arquivos `.md` são salvos **na mesma pasta** de cada arquivo `.pdf`, com o mesmo nome:
- `relatorio_anual.pdf` ➡️ `relatorio_anual.md`
- `contrato.pdf` ➡️ `contrato.md`

