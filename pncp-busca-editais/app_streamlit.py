import os
import json
import time
import logging
from datetime import datetime
import streamlit as st

# Configurações do Streamlit (deve ser a primeira chamada)
st.set_page_config(
    page_title="PNCP Monitor - Busca Vetorial",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização básica via CSS
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 50px;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #764ba2, #667eea);
        color: white;
    }
    .edital-card {
        background-color: #1a1c23;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 5px solid #667eea;
    }
    .score-badge {
        background-color: #2e7d32;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

from pncp_client import PNCPClient
from vector_search import VectorSearch

CONFIG_FILE = "buscas_config.json"
HISTORICO_FILE = "historico_capturas.json"
RESULTADOS_FILE = "resultados_busca.txt"

# Funções utilitárias mantidas do CLI
def carregar_configuracoes():
    if not os.path.exists(CONFIG_FILE):
        return []
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def carregar_historico():
    if os.path.exists(HISTORICO_FILE):
        try:
            with open(HISTORICO_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except Exception: pass
    return set()

def salvar_historico(historico):
    try:
        with open(HISTORICO_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(historico), f, indent=2, ensure_ascii=False)
    except Exception: pass

def formatar_moeda(valor):
    if valor is None: return "Não informado"
    try: return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception: return str(valor)

def formatar_data(data_str):
    if not data_str: return "Não informada"
    try:
        if "T" in data_str:
            dt = datetime.fromisoformat(data_str.split('.')[0])
            return dt.strftime("%d/%m/%Y às %H:%M")
        return data_str
    except Exception: return data_str

def processar_itens_edital(client, edital_dict):
    control = edital_dict.get('numeroControlePNCP')
    if not control: return [], None
    try:
        parts = control.split('-')
        cnpj, sequencial, ano = parts[0], int(parts[2].split('/')[0]), parts[2].split('/')[1]
        itens = client.buscar_itens_edital(cnpj, ano, sequencial)
        
        itens_formatados = []
        valor_total = 0.0
        if isinstance(itens, list):
            for it in itens:
                desc = it.get('descricao', '').strip()
                qtd = it.get('quantidade', 1)
                valor_unit = it.get('valorUnitarioEstimado') or it.get('valorUnitarioHomologado') or 0.0
                val_total_item = qtd * valor_unit
                valor_total += val_total_item
                itens_formatados.append({
                    "numero": it.get('numeroItem', 1),
                    "descricao": desc,
                    "quantidade": qtd,
                    "unidade": it.get('unidadeMedida', 'UN'),
                    "valor_unitario": valor_unit,
                    "valor_total": val_total_item
                })
            return itens_formatados, valor_total
    except Exception: pass
    return [], None

def salvar_relatorio_txt(editais_descobertos):
    if not editais_descobertos: return
    
    editais_descobertos.sort(key=lambda e: e['score'], reverse=True)
    modo_abertura = 'a' if os.path.exists(RESULTADOS_FILE) else 'w'
    
    try:
        with open(RESULTADOS_FILE, modo_abertura, encoding='utf-8') as f:
            if modo_abertura == 'w':
                f.write("=" * 100 + "\n")
                f.write("PNCP MONITOR - RELATÓRIO DE EDITAIS ENCONTRADOS (BUSCA VETORIAL AI)\n")
                f.write("=" * 100 + "\n\n")

            f.write(f"\n================================================================================\n")
            f.write(f"EXECUÇÃO EM: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}\n")
            f.write(f"Encontrados {len(editais_descobertos)} novos editais relevantes usando IA.\n")
            f.write(f"================================================================================\n\n")
            
            for idx, ed in enumerate(editais_descobertos, 1):
                f.write("-" * 80 + "\n")
                f.write(f"Oportunidade #{idx}: Regra [{ed['busca_nome']}] | Score de Similaridade: {ed['score']*100:.1f}%\n")
                f.write("-" * 80 + "\n")
                f.write(f"Órgão: {ed['orgao']}\n")
                f.write(f"UF: {ed['uf']} | Município: {ed['municipio']}\n")
                f.write(f"Modalidade: {ed['modalidade']}\n")
                f.write(f"Número de Controle PNCP: {ed['control']}\n")
                f.write(f"Valor Estimado Total: {formatar_moeda(ed['valor'])}\n")
                f.write(f"Data de Abertura: {formatar_data(ed['data_abertura'])}\n")
                f.write(f"Link no PNCP: {ed['link_pncp']}\n")
                f.write(f"\nObjeto da Compra:\n{ed['objeto']}\n")
                
                if ed['itens']:
                    f.write(f"\nItens Detalhados do Edital:\n")
                    for it in ed['itens']:
                        f.write(f"#{it['numero']}: {it['descricao'][:120]}... | Qtd: {it['quantidade']} {it['unidade']} | Total: {formatar_moeda(it['valor_total'])}\n")
                f.write("\n\n")
    except Exception as e:
        st.error(f"Erro ao salvar arquivo .txt: {e}")

# Interface Streamlit Principal
def main():
    st.title("🔎 PNCP Monitor")
    st.markdown("Sistema de Busca Semântica em Editais Públicos usando IA (ChromaDB + Sentence Transformers).")

    # --- BARRA LATERAL ---
    with st.sidebar:
        st.header("⚙️ Configurações")
        buscas = carregar_configuracoes()
        buscas_ativas = [b for b in buscas if b.get('ativa', True)]
        
        st.subheader("Regras Ativas")
        
        # Formulário para adicionar nova regra
        with st.expander("➕ Adicionar Nova Regra", expanded=False):
            with st.form("nova_regra_form", clear_on_submit=True):
                novo_nome = st.text_input("Nome da Regra", placeholder="Ex: Teste Varonis")
                novas_palavras = st.text_input("Palavras-chave (separadas por vírgula)", placeholder="varonis, mddr, uba")
                novo_contexto = st.text_area("Contexto esperado para IA avaliar", placeholder="Serviços de segurança cibernética, proteção de dados...")
                
                if st.form_submit_button("Salvar Regra"):
                    if novo_nome and novas_palavras:
                        buscas.append({
                            "nome": novo_nome,
                            "palavras_chave": novas_palavras,
                            "descricao_contexto": novo_contexto,
                            "ativa": True
                        })
                        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                            json.dump(buscas, f, indent=2, ensure_ascii=False)
                        st.success("Regra salva com sucesso!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Nome e Palavras-chave são obrigatórios.")

        st.divider()

        if buscas_ativas:
            for idx, b in enumerate(buscas_ativas):
                with st.container():
                    st.info(f"**{b['nome']}**\n\nGatilhos: {b.get('palavras_chave')}\n\nContexto IA: {b.get('descricao_contexto')[:50]}...")
                    if st.button(f"🗑️ Excluir '{b['nome']}'", key=f"del_{idx}"):
                        buscas.remove(b)
                        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                            json.dump(buscas, f, indent=2, ensure_ascii=False)
                        st.rerun()
        else:
            st.warning("Nenhuma regra de busca ativa.")
            
        st.divider()
        st.markdown(f"**Editais rastreados (Cache):** {len(carregar_historico())}")
        if st.button("Limpar Cache Local"):
            if os.path.exists(HISTORICO_FILE):
                os.remove(HISTORICO_FILE)
            st.success("Histórico apagado. Editais passados serão re-processados na próxima busca.")
            time.sleep(1)
            st.rerun()

    # --- PAINEL PRINCIPAL ---
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("Clique no botão abaixo para varrer os editais publicados mais recentemente no PNCP, baixar os dados, processar os textos e rodar o modelo de inteligência artificial vetorial para avaliar a similaridade contextual.")
    
    with col2:
        btn_buscar = st.button("🚀 EXECUTAR BUSCA")

    if btn_buscar:
        if not buscas_ativas:
            st.error("Configure regras ativas no arquivo buscas_config.json primeiro!")
            return

        # Interface de Progresso
        progresso_container = st.container()
        with progresso_container:
            st.markdown("### Processamento em Andamento")
            status_text = st.empty()
            progress_bar = st.progress(0)
            
            # Inicializa Banco
            status_text.text("1/3 Carregando Modelo de Inteligência Artificial e Banco Vetorial...")
            try:
                vector_db = VectorSearch()
                vector_db.clear_collection()
            except Exception as e:
                st.error(f"Falha ao iniciar ChromaDB/Modelo. Dependências instaladas? Erro: {e}")
                return

            status_text.text("2/3 Baixando e indexando editais do PNCP no banco local...")
            progress_bar.progress(20)
            
            historico = carregar_historico()
            client = PNCPClient(tamanho_pagina=50, delay=1.0)
            editais_coletados = {}
            
            # Callback para log/ui não sobrecarregar
            def callback_pncp(pagina, total):
                if pagina % 5 == 0:
                    status_text.text(f"Baixando PNCP... (Página {pagina}/{total})")
            
            try:
                for lote in client.buscar_todas_propostas_abertas(max_paginas=20, callback=callback_pncp):
                    lote_valido = []
                    for ed in lote:
                        control = ed.get('numeroControlePNCP')
                        if not control or control in historico:
                            continue
                            
                        data_abertura_str = ed.get('dataAberturaProposta') or ed.get('dataHoraAberturaLicitacao')
                        if data_abertura_str:
                            try:
                                iso_str = data_abertura_str[:19]
                                if datetime.fromisoformat(iso_str) < datetime.now():
                                    continue
                            except Exception: pass
                        
                        lote_valido.append(ed)
                        editais_coletados[control] = ed
                        
                    if lote_valido:
                        vector_db.add_editais(lote_valido)
            except Exception as e:
                st.warning(f"Instabilidade no PNCP ({e}). Prosseguindo com o que foi coletado até agora.")

            progress_bar.progress(70)
            status_text.text(f"3/3 Executando Buscas Semânticas sobre {len(editais_coletados)} editais indexados...")
            
            editais_descobertos = []
            
            if len(editais_coletados) > 0:
                from filters import normalizar_texto
                for busca in buscas_ativas:
                    nome_busca = busca['nome']
                    query_text = busca.get('descricao_contexto') or busca.get('palavras_chave')
                    palavras_chave_str = busca.get('palavras_chave', '')
                    
                    # 1. Filtro de Gatilho Lexical (Impede que a IA traga "padarias" se a palavra não existir)
                    gatilhos = [normalizar_texto(k.strip()) for k in palavras_chave_str.split(',') if k.strip()]
                    ids_aprovados_gatilho = []
                    
                    for control, ed in editais_coletados.items():
                        objeto_norm = normalizar_texto(ed.get('objetoCompra', '') or '')
                        # O edital deve conter pelo menos uma das palavras-chave exatas
                        if not gatilhos or any(g in objeto_norm for g in gatilhos):
                            ids_aprovados_gatilho.append(control)
                            
                    # Se nenhum edital baixado tiver a palavra exata, pula para a próxima busca
                    if not ids_aprovados_gatilho:
                        continue
                        
                    # 2. Avaliação de Contexto pela Inteligência Artificial
                    # Limiar super restrito. 0.5 de distância equivale a 75% de Similaridade Mínima
                    max_dist = 0.5 
                    
                    # Filtra apenas os IDs que passaram no gatilho na busca no ChromaDB
                    matches = vector_db.search_editais(
                        query=query_text, 
                        n_results=len(ids_aprovados_gatilho), 
                        max_distance=max_dist,
                        where_filter={"numeroControlePNCP": {"$in": ids_aprovados_gatilho}}
                    )
                    
                    for match in matches:
                        control = match['numeroControlePNCP']
                        dist = match['distancia']
                        score_pct = max(0.0, 1.0 - (dist / 2.0))
                        
                        ed = editais_coletados.get(control)
                        if not ed: continue
                        
                        # Processar valores
                        itens, valor_calculado = processar_itens_edital(client, ed)
                        valor_estimado = ed.get('valorTotalEstimado')
                        if valor_calculado is not None and valor_calculado > 0:
                            valor_estimado = valor_calculado
                            
                        uf_orgao = ed.get('orgaoEntidade', {}).get('ufSigla') or ed.get('ufSigla') or 'DF'
                        cnpj_orgao = ed.get('orgaoEntidade', {}).get('cnpj')
                        
                        link_pncp = f"https://pncp.gov.br/app/editais/visualizar?controle={control}"
                        try:
                            parts = control.split('-')
                            link_pncp = f"https://pncp.gov.br/app/editais/{cnpj_orgao}/{parts[2].split('/')[1]}/{int(parts[2].split('/')[0])}"
                        except Exception: pass

                        editais_descobertos.append({
                            "busca_nome": nome_busca,
                            "score": score_pct,
                            "control": control,
                            "orgao": ed.get('orgaoEntidade', {}).get('razaoSocial', 'Órgão não informado'),
                            "uf": uf_orgao,
                            "municipio": ed.get('municipioNome', 'Não informado'),
                            "objeto": (ed.get('objetoCompra') or '').strip(),
                            "valor": valor_estimado,
                            "data_abertura": ed.get('dataAberturaProposta') or ed.get('dataHoraAberturaLicitacao'),
                            "link_pncp": link_pncp,
                            "modalidade": ed.get('modalidadeNome', 'Não informada'),
                            "itens": itens
                        })
                        historico.add(control)

            progress_bar.progress(100)
            status_text.text("✅ Processamento Concluído!")
            time.sleep(1)
            progresso_container.empty() # Remove a barra da tela após concluído
            
        # -- Renderização dos Resultados --
        st.markdown("---")
        if editais_descobertos:
            editais_descobertos.sort(key=lambda e: e['score'], reverse=True)
            
            st.success(f"🎉 Foram encontrados {len(editais_descobertos)} editais com alta relevância de contexto!")
            
            # Grava no txt em background
            salvar_relatorio_txt(editais_descobertos)
            salvar_historico(historico)
            
            for ed in editais_descobertos:
                score_formated = f"{ed['score']*100:.1f}%"
                
                # Renderiza o Card de Edital
                st.markdown(f"""
                <div class="edital-card">
                    <h3 style="margin-top: 0;">{ed['orgao']} - {ed['uf']}</h3>
                    <div style="margin-bottom: 15px;">
                        <span class="score-badge">Relevância IA: {score_formated}</span>
                        <span style="color: #aaa; margin-left: 10px;">Regra: {ed['busca_nome']}</span>
                    </div>
                    <p style="font-size: 1.1em; color: #ddd;"><b>Objeto:</b> {ed['objeto']}</p>
                    <div style="display: flex; gap: 20px; color: #bbb; margin-bottom: 15px;">
                        <div><b>Valor:</b> <span style="color: #667eea;">{formatar_moeda(ed['valor'])}</span></div>
                        <div><b>Modalidade:</b> {ed['modalidade']}</div>
                        <div><b>Abertura:</b> {formatar_data(ed['data_abertura'])}</div>
                    </div>
                    <a href="{ed['link_pncp']}" target="_blank" style="text-decoration: none;">
                        <button style="background: #2b313e; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer;">
                            🔗 Ver no Portal PNCP
                        </button>
                    </a>
                </div>
                """, unsafe_allow_html=True)
                
                if ed['itens']:
                    with st.expander("📦 Visualizar Itens do Edital"):
                        for it in ed['itens']:
                            st.write(f"- **Item {it['numero']}**: {it['descricao']} | **Qtd:** {it['quantidade']} {it['unidade']} | **Total:** {formatar_moeda(it['valor_total'])}")
        else:
            st.info("Nenhum edital novo com similaridade de contexto encontrada no momento.")

if __name__ == "__main__":
    main()
