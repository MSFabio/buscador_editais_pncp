# 📋 PNCP Bidding Search & PDF Generator System

Sistema automatizado em Python para consulta aprofundada de editais abertos no **Portal Nacional de Contratações Públicas (PNCP)**, com suporte a busca multi-thread por palavras-chave, filtragem por data/estado (ex: Bahia) e geração automática de relatórios em Markdown e PDF vetorial de alta definição.

---

## 🚀 Funcionalidades

- **Busca Concorrente (Multi-thread):** Consulta simultânea de múltiplas páginas na API do PNCP (`/api/search/`).
- **Recuperação de Detalhes:** Busca assíncrona de metadados completos de cada edital (data da sessão pública, link do sistema de origem, valor estimado e objeto completo).
- **Filtro de Sessão Pública Futura:** Garante que apenas oportunidades abertas a partir da data atual sejam consideradas.
- **Identificação de Modalidades:** Separação e destaque visual para **Pregões Eletrônicos**, **Credenciamentos** e **Dispensas de Licitação**.
- **Geração de PDF de Alta Resolução:** Conversão automatizada para PDF vetorial via engine Chromium Headless com suporte a links clicáveis e formatação profissional.

---

## 🛠️ Palavras-Chave Suportadas

O sistema pesquisa os seguintes segmentos e termos:
1. `Buffet`
2. `Buffet para eventos`
3. `Buffet para cerimônias`
4. `Catering`
5. `Alimentação`
6. `Alimentação para eventos`
7. `Coffee Break`
8. `Lanches`
9. `Aluguel de mesas e cadeiras`
10. `Equipe de garçons e serviços correlatos`

---

## 📦 Instalação e Requisitos

### Requisitos
- Python 3.10+
- Microsoft Edge ou Google Chrome (para renderização PDF via Headless Chromium)

### Instalação de Dependências
```bash
pip install -r requirements.txt
```

---

## 🏃 Como Executar

### 1. Executar Busca no PNCP (Bahia ou Brasil)
```bash
python pncp_cli.py --uf BA --pages 25
```

### 2. Geração Manual de PDF
```bash
python pdf_generator.py
```

---

## 📊 Estrutura de Arquivos

- `pncp_cli.py`: Script principal de busca e extração paralela de dados da API PNCP.
- `pdf_generator.py`: Módulo de renderização de PDF nativo vetorial.
- `requirements.txt`: Dependências Python do projeto.
- `.gitignore`: Regras de exclusão do controle de versão Git.
- `README.md`: Documentação oficial do repositório.

---

## 📄 Licença
Licença MIT - Uso livre para consultas e automações públicas.
