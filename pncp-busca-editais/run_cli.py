import os
import json
import time
import logging
from datetime import datetime
import requests

# Configura o logger do python
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("pncp_cli")

from pncp_client import PNCPClient
from vector_search import VectorSearch
import config

CONFIG_FILE = "buscas_config.json"
HISTORICO_FILE = "historico_capturas.json"
RESULTADOS_FILE = "resultados_busca.txt"

def carregar_configuracoes():
    if not os.path.exists(CONFIG_FILE):
        logger.error(f"Arquivo de configuracao '{CONFIG_FILE}' nao encontrado!")
        return []
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erro ao ler arquivo de configuracao: {e}")
        return []

def carregar_historico():
    if os.path.exists(HISTORICO_FILE):
        try:
            with open(HISTORICO_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except Exception as e:
            logger.error(f"Erro ao ler historico local: {e}")
    return set()

def salvar_historico(historico):
    try:
        with open(HISTORICO_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(historico), f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erro ao salvar historico local: {e}")

def formatar_moeda(valor):
    if valor is None: return "Nao informado"
    try: return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception: return str(valor)

def formatar_data(data_str):
    if not data_str: return "Nao informada"
    try:
        if "T" in data_str:
            dt = datetime.fromisoformat(data_str.split('.')[0])
            return dt.strftime("%d/%m/%Y as %H:%M")
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
    except Exception as e:
        pass
    return [], None

def rodar_busca():
    print("=" * 80)
    print(" [BUSCA] PNCP MONITOR - BUSCA VETORIAL COM CHROMADB (CLI/BAT)")
    print("=" * 80)
    
    buscas = carregar_configuracoes()
    buscas_ativas = [b for b in buscas if b.get('ativa', True)]
    
    if not buscas_ativas:
        logger.warning("Nenhuma regra de busca ativa configurada!")
        return

    historico = carregar_historico()
    client = PNCPClient(tamanho_pagina=50, delay=2.0)
    
    print("\nInicializando banco vetorial ChromaDB...")
    vector_db = VectorSearch()
    
    # Limpa a coleção para garantir que a busca atual pegue apenas do que coletarmos agora
    vector_db.clear_collection()
    
    def print_progresso(pagina, total):
        print(f"    Progresso PNCP: Pagina {pagina}/{total}...", end="\r", flush=True)

    print("\n[Fase 1] Baixando editais do PNCP e indexando no banco vetorial...")
    editais_coletados = {}
    
    try:
        for lote in client.buscar_todas_propostas_abertas(max_paginas=30, callback=print_progresso):
            lote_valido = []
            for ed in lote:
                control = ed.get('numeroControlePNCP')
                if not control or control in historico:
                    continue
                    
                # Regra de Data Futura
                data_abertura_str = ed.get('dataAberturaProposta') or ed.get('dataHoraAberturaLicitacao')
                if data_abertura_str:
                    try:
                        iso_str = data_abertura_str[:19]
                        if datetime.fromisoformat(iso_str) < datetime.now():
                            continue
                    except Exception: pass
                
                lote_valido.append(ed)
                editais_coletados[control] = ed
                
            # Adiciona lote ao ChromaDB
            if lote_valido:
                vector_db.add_editais(lote_valido)
    except Exception as e:
        logger.error(f"Erro ao buscar no PNCP: {e}")

    print(f"\nTotal de {len(editais_coletados)} novos editais indexados no vetor.")
    
    if not editais_coletados:
        print("\nNenhum edital novo no momento. Busca finalizada.")
        return

    print("\n[Fase 2] Realizando Buscas Semânticas (Filtro Híbrido)...")
    editais_descobertos = []
    
    from filters import normalizar_texto

    for idx, busca in enumerate(buscas_ativas, 1):
        nome_busca = busca['nome']
        
        query_text = busca.get('descricao_contexto') or busca.get('palavras_chave')
        palavras_chave_str = busca.get('palavras_chave', '')
        
        # 1. Filtro Lexical
        gatilhos = [normalizar_texto(k.strip()) for k in palavras_chave_str.split(',') if k.strip()]
        ids_aprovados_gatilho = []
        
        for control, ed in editais_coletados.items():
            objeto_norm = normalizar_texto(ed.get('objetoCompra', '') or '')
            if not gatilhos or any(g in objeto_norm for g in gatilhos):
                ids_aprovados_gatilho.append(control)
                
        if not ids_aprovados_gatilho:
            print(f" -> Executando regra: '{nome_busca}' - Ignorada (nenhuma palavra-chave encontrada)")
            continue
            
        max_dist = 0.5 # Limiar restrito (~75%)
        
        print(f" -> Executando regra: '{nome_busca}' ({len(ids_aprovados_gatilho)} candidatos)")
        matches = vector_db.search_editais(
            query=query_text, 
            n_results=len(ids_aprovados_gatilho), 
            max_distance=max_dist,
            where_filter={"numeroControlePNCP": {"$in": ids_aprovados_gatilho}}
        )
        
        for match in matches:
            control = match['numeroControlePNCP']
            distancia = match['distancia']
            score_similaridade = max(0.0, 1.0 - (distancia / 2.0)) # Aproximacao de score %
            
            ed = editais_coletados.get(control)
            if not ed: continue
            
            objeto = ed.get('objetoCompra', '') or ''
            
            print(f"    [*] Match! Score: {score_similaridade*100:.1f}% | Control: {control}")
            
            itens, valor_calculado = processar_itens_edital(client, ed)
            valor_estimado = ed.get('valorTotalEstimado')
            if valor_calculado is not None and valor_calculado > 0:
                valor_estimado = valor_calculado
                
            uf_orgao = ed.get('orgaoEntidade', {}).get('ufSigla') or ed.get('ufSigla') or 'DF'
            cnpj_orgao = ed.get('orgaoEntidade', {}).get('cnpj')
            
            link_pncp = f"https://pncp.gov.br/app/editais/visualizar?controle={control}"
            try:
                parts = control.split('-')
                seq_pncp = int(parts[2].split('/')[0])
                ano_pncp = parts[2].split('/')[1]
                link_pncp = f"https://pncp.gov.br/app/editais/{cnpj_orgao}/{ano_pncp}/{seq_pncp}"
            except Exception: pass

            edital_relevante = {
                "busca_nome": nome_busca,
                "score": score_similaridade,
                "distancia_chroma": distancia,
                "control": control,
                "orgao": ed.get('orgaoEntidade', {}).get('razaoSocial', 'Orgao nao informado'),
                "uf": uf_orgao,
                "municipio": ed.get('municipioNome', 'Nao informado'),
                "objeto": objeto.strip(),
                "valor": valor_estimado,
                "data_abertura": ed.get('dataAberturaProposta') or ed.get('dataHoraAberturaLicitacao'),
                "link_pncp": link_pncp,
                "link_origem": ed.get('linkSistemaOrigem', ''),
                "modalidade": ed.get('modalidadeNome', 'Nao informada'),
                "itens": itens
            }
            
            editais_descobertos.append(edital_relevante)
            historico.add(control)

    # 4. Grava relatorio
    if editais_descobertos:
        editais_descobertos.sort(key=lambda e: e['score'], reverse=True)
        modo_abertura = 'a' if os.path.exists(RESULTADOS_FILE) else 'w'
        
        with open(RESULTADOS_FILE, modo_abertura, encoding='utf-8') as f:
            if modo_abertura == 'w':
                f.write("=" * 100 + "\n")
                f.write("PNCP MONITOR - RELATORIO DE EDITAIS ENCONTRADOS (BUSCA VETORIAL AI)\n")
                f.write("=" * 100 + "\n\n")

            f.write(f"\n================================================================================\n")
            f.write(f"EXECUCAO EM: {datetime.now().strftime('%d/%m/%Y as %H:%M:%S')}\n")
            f.write(f"Encontrados {len(editais_descobertos)} novos editais relevantes usando Inteligencia Artificial.\n")
            f.write(f"================================================================================\n\n")
            
            for idx, ed in enumerate(editais_descobertos, 1):
                f.write("-" * 80 + "\n")
                f.write(f"Oportunidade #{idx}: Regra [{ed['busca_nome']}] | Score de Similaridade: {ed['score']*100:.1f}% (Dist: {ed['distancia_chroma']:.2f})\n")
                f.write("-" * 80 + "\n")
                f.write(f"Orgao: {ed['orgao']}\n")
                f.write(f"UF: {ed['uf']} | Municipio: {ed['municipio']}\n")
                f.write(f"Modalidade: {ed['modalidade']}\n")
                f.write(f"Numero de Controle PNCP: {ed['control']}\n")
                f.write(f"Valor Estimado Total: {formatar_moeda(ed['valor'])}\n")
                f.write(f"Data de Abertura: {formatar_data(ed['data_abertura'])}\n")
                f.write(f"Link no PNCP: {ed['link_pncp']}\n")
                f.write(f"\nObjeto da Compra:\n{ed['objeto']}\n")
                
                if ed['itens']:
                    f.write(f"\nItens Detalhados do Edital:\n")
                    for it in ed['itens']:
                        f.write(f"#{it['numero']}: {it['descricao'][:120]}... | Qtd: {it['quantidade']} {it['unidade']} | Total: {formatar_moeda(it['valor_total'])}\n")
                f.write("\n\n")
                
        salvar_historico(historico)
        
        print("\n" + "=" * 80)
        print(f" SUCCESS: {len(editais_descobertos)} novos editais gravados com sucesso em '{RESULTADOS_FILE}'!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print(" Nao foram localizados novos editais com similaridade suficiente nesta varredura.")
        print("=" * 80)

if __name__ == "__main__":
    rodar_busca()
