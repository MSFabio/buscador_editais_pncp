"""
Pipeline de Análise Semântica Avançada (IA + scikit-learn + NLTK + Sentence-Transformers)
Processa os 10 documentos (TR 2215770 + 9 propostas/referências de preços),
calcula similaridades globais e por dimensão, extrai vocabulário distintivo e gera
dados estruturados para o relatório comparativo.
"""

import sys
import os
import json
import re
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import nltk
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\11429149760\.gemini\antigravity\scratch\analise_licitacao_telecom"
MD_DIR = os.path.join(BASE_DIR, "markdown")
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# Documentos a analisar
DOCUMENTS = [
    {
        "id": "2215770",
        "key": "TR_DPRJ",
        "name": "Termo de Referência 2215770 (DPRJ)",
        "file": "01_TR_2215770.md",
        "type": "Referência Principal"
    },
    {
        "id": "2219726",
        "key": "GSNT",
        "name": "Proposta GSNT Telecom (2219726)",
        "file": "02_Proposta_GSNT_2219726.md",
        "type": "Cotação de Mercado"
    },
    {
        "id": "2219727",
        "key": "PREGAO_GO",
        "name": "Pregão 107458/2025 Sec. Geral Governadoria - GO (2219727)",
        "file": "03_Pregao_GO_107458_2025_2219727.md",
        "type": "Contratação Pública (GO)"
    },
    {
        "id": "2219728",
        "key": "PREGAO_MPES",
        "name": "Pregão 90037/2025 MPES (2219728)",
        "file": "04_Pregao_MPES_90037_2025_2219728.md",
        "type": "Contratação Pública (ES)"
    },
    {
        "id": "2219730",
        "key": "PREGAO_DTI_PF",
        "name": "Pregão 90009/2025 DTI / Polícia Federal (2219730)",
        "file": "05_Pregao_DTI_PF_90009_2025_2219730.md",
        "type": "Contratação Pública (Federal)"
    },
    {
        "id": "2219741",
        "key": "PREGAO_MPRJ",
        "name": "Pregão 90020/2024 MPRJ (2219741)",
        "file": "06_Pregao_MPRJ_90020_2024_2219741.md",
        "type": "Contratação Pública (RJ)"
    },
    {
        "id": "2219742",
        "key": "CONTRATO_MTE",
        "name": "Contrato 18/2024 MTE / Telebras (2219742)",
        "file": "07_Contrato_MTE_18_2024_Telebras_2219742.md",
        "type": "Contratação Pública (Federal)"
    },
    {
        "id": "2219745",
        "key": "CD_FUPESC",
        "name": "Proposta CD 75/2025 FUPESC (2219745)",
        "file": "08_CD_FUPESC_75_2025_2219745.md",
        "type": "Contratação Pública (SC)"
    },
    {
        "id": "2219747",
        "key": "PREGAO_TJMRS",
        "name": "Pregão 2/2026 Justiça Militar - TJMRS (2219747)",
        "file": "09_Pregao_TJMRS_2_2026_2219747.md",
        "type": "Contratação Pública (RS)"
    },
    {
        "id": "2219752",
        "key": "OI_ATUAL",
        "name": "Proposta Oi - Valor Atual Contratado DPRJ (2219752)",
        "file": "10_Proposta_Oi_Valor_Atual_2219752.md",
        "type": "Contrato Vigente (DPRJ)"
    }
]

# Configurar Stopwords
nltk_stopwords = set(stopwords.words('portuguese'))
custom_stopwords = {
    'fls', 'sei', 'processo', 'art', 'nº', 'no', 'rio', 'janeiro', 'dprj', 'dperj', 
    'sob', 'item', 'termo', 'referência', 'referencia', 'anexo', 'edital', 'contrato', 
    'contratação', 'contratacao', 'prestação', 'prestacao', 'serviço', 'serviços', 
    'servico', 'servicos', 'empresa', 'contratada', 'contratante', 'órgão', 'orgao',
    'página', 'pagina', 'pg', 'data', 'horário', 'horario', 'de', 'a', 'o', 'que', 'e', 
    'do', 'da', 'em', 'um', 'para', 'é', 'com', 'não', 'uma', 'os', 'no', 'se', 'na', 
    'por', 'mais', 'as', 'dos', 'como', 'mas', 'foi', 'ao', 'ele', 'das', 'tem', 'à', 
    'seu', 'sua', 'ou', 'ser', 'quando', 'muito', 'há', 'nos', 'já', 'está', 'eu', 'também',
    'só', 'pelo', 'pela', 'até', 'isso', 'ela', 'entre', 'era', 'depois', 'sem', 'mesmo', 
    'aos', 'ter', 'seus', 'quem', 'nas', 'me', 'esse', 'eles', 'estão', 'você', 'tinha', 
    'foram', 'essa', 'num', 'nem', 'suas', 'meu', 'às', 'minha', 'têm', 'numa', 'pelos', 
    'elas', 'havia', 'seja', 'qual', 'será', 'nós', 'tenho', 'lhe', 'deles', 'essas', 
    'esses', 'pelas', 'este', 'fosse', 'dele', 'tu', 'te', 'vocês', 'vos', 'lhes', 'meus', 
    'minhas', 'teu', 'tua', 'teus', 'tuas', 'nosso', 'nossa', 'nossos', 'nossas', 'dela', 
    'delas', 'esta', 'estes', 'estas', 'aquele', 'aquela', 'aqueles', 'aquelas', 'isto', 
    'aquilo', 'estou', 'está', 'estamos', 'estão', 'estive', 'esteve', 'estivemos', 
    'estiveram', 'estava', 'estávamos', 'estavam', 'estivera', 'estivéramos', 'esteja', 
    'estejamos', 'estejam', 'estivesse', 'estivéssemos', 'estivessem', 'estiver', 
    'estivermos', 'estiverem', 'hei', 'havemos', 'hão', 'houve', 'houvemos', 'houveram', 
    'houvera', 'houvéramos', 'haja', 'hajamos', 'hajam', 'houvesse', 'houvéssemos', 
    'houvessem', 'houver', 'houvermos', 'houverem', 'houverei', 'houverá', 'houveremos', 
    'houverão', 'houveria', 'houveríamos', 'houveriam', 'sou', 'somos', 'são', 'era', 
    'éramos', 'eram', 'fui', 'foi', 'fomos', 'foram', 'fora', 'fôramos', 'seja', 'sejamos', 
    'sejam', 'fosse', 'fôssemos', 'fossem', 'for', 'formos', 'forem', 'serei', 'será', 
    'seremos', 'serão', 'seria', 'seríamos', 'seriam', 'tenho', 'tem', 'temos', 'tém', 
    'tinha', 'tínhamos', 'tinham', 'tive', 'teve', 'tivemos', 'tiveram', 'tivera', 
    'tivéramos', 'tenha', 'tenhamos', 'tenham', 'tivesse', 'tivéssemos', 'tivessem', 
    'tiver', 'tivermos', 'tiverem', 'terei', 'terá', 'teremos', 'terão', 'teria', 
    'teríamos', 'teriam', 'conforme', 'mediante', 'disposto', 'termos', 'seguinte', 
    'presente', 'caso', 'valor', 'reais', 'r', 'unidade', 'unidades', 'total'
}
ALL_STOPWORDS = list(nltk_stopwords.union(custom_stopwords))

def load_documents():
    """Carrega o texto dos 10 documentos analisados."""
    docs = []
    for d in DOCUMENTS:
        filepath = os.path.join(MD_DIR, d["file"])
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        d_copy = dict(d)
        d_copy["raw_text"] = content
        docs.append(d_copy)
    return docs

def extract_dimensions(doc):
    """
    Segmenta o documento em 4 dimensões temáticas:
    1. Objeto & Topologia
    2. Especificações Técnicas (SD-WAN, CPE, Firewall)
    3. Modelagem Contratual (Vigência, Reajuste, Execução)
    4. Níveis Mínimos de Serviço (SLA, Disponibilidade, Glosas)
    """
    txt = doc["raw_text"]
    key = doc["key"]
    
    # Dicionário de dimensões
    dims = {
        "objeto_topologia": "",
        "especificacoes_tecnicas": "",
        "modelagem_contratual": "",
        "sla_glosas": ""
    }
    
    # Extração inteligente baseada em palavras-chave e cabeçalhos
    paragraphs = txt.split("\n\n")
    
    obj_pars = []
    tec_pars = []
    mod_pars = []
    sla_pars = []
    
    for p in paragraphs:
        p_clean = " ".join(p.split())
        if len(p_clean) < 30:
            continue
        p_lower = p_clean.lower()
        
        # Objeto e Topologia
        if any(w in p_lower for w in ["objeto", "topologia", "links", "circuito", "interconexão", "conectividade", "simétrico", "dedicado", "transporte de dados", "unidades operacionais"]):
            obj_pars.append(p_clean)
            
        # Especificações Técnicas
        if any(w in p_lower for w in ["sd-wan", "sdwan", "cpe", "appliance", "firewall", "ngfw", "ips", "orquestrador", "roteador", "ativos de borda", "hardware", "software", "throughput", "redundância"]):
            tec_pars.append(p_clean)
            
        # Modelagem Contratual
        if any(w in p_lower for w in ["vigência", "vigencia", "prazo", "emergencial", "transição", "reajuste", "icti", "ipca", "subcontratação", "subcontratacao", "faturamento", "pagamento"]):
            mod_pars.append(p_clean)
            
        # SLA e Glosas
        if any(w in p_lower for w in ["sla", "nível mínimo de serviço", "nivel de serviço", "disponibilidade", "99,", "99.", "latência", "latencia", "perda de pacotes", "jitter", "glosa", "glosas", "penalidade", "mttr", "mtbf", "tempo de atendimento"]):
            sla_pars.append(p_clean)
            
    # Garantir que tenhamos texto representativo para cada dimensão
    dims["objeto_topologia"] = " ".join(obj_pars[:15]) if obj_pars else p_clean[:1000]
    dims["especificacoes_tecnicas"] = " ".join(tec_pars[:15]) if tec_pars else p_clean[:1000]
    dims["modelagem_contratual"] = " ".join(mod_pars[:15]) if mod_pars else p_clean[:1000]
    dims["sla_glosas"] = " ".join(sla_pars[:15]) if sla_pars else p_clean[:1000]
    
    return dims

def run_tfidf_analysis(docs):
    """Executa a análise TF-IDF e calcula matriz de similaridade léxico-estatística."""
    print("\nExecutando análise TF-IDF (scikit-learn + NLTK)...", flush=True)
    corpus = [d["raw_text"] for d in docs]
    
    vectorizer = TfidfVectorizer(
        stop_words=ALL_STOPWORDS,
        ngram_range=(1, 2),
        max_df=0.85,
        min_df=2,
        sublinear_tf=True
    )
    
    tfidf_matrix = vectorizer.fit_transform(corpus)
    feature_names = np.array(vectorizer.get_feature_names_out())
    
    # Similaridade de Cosseno global
    sim_matrix = cosine_similarity(tfidf_matrix)
    
    # Extrair termos mais distintivos por documento
    top_terms_per_doc = {}
    for i, d in enumerate(docs):
        row = tfidf_matrix[i].toarray().flatten()
        top_indices = row.argsort()[-12:][::-1]
        top_terms = [feature_names[idx] for idx in top_indices if row[idx] > 0]
        top_terms_per_doc[d["key"]] = top_terms
        
    return sim_matrix, top_terms_per_doc

def run_sentence_transformers_analysis(docs, model_name="paraphrase-multilingual-MiniLM-L12-v2"):
    """Executa embeddings densos com Sentence-Transformers por dimensão."""
    print(f"\nCarregando Sentence-Transformers: {model_name}...", flush=True)
    model = SentenceTransformer(model_name)
    
    dim_keys = ["objeto_topologia", "especificacoes_tecnicas", "modelagem_contratual", "sla_glosas"]
    dim_results = {}
    
    for dim in dim_keys:
        print(f"  Gerando embeddings para dimensão: {dim}...", flush=True)
        texts = [d["dimensions"][dim] for d in docs]
        embeddings = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        
        # Similaridade de cosseno
        sim_mat = cosine_similarity(embeddings)
        dim_results[dim] = {
            "matrix": sim_mat.tolist(),
            "vs_tr": {docs[j]["key"]: float(sim_mat[0][j]) for j in range(len(docs))}
        }
        
    # Calcular similaridade densa global baseada em resumo estruturado
    print("  Gerando embeddings densos globais...", flush=True)
    global_summaries = []
    for d in docs:
        summary = (
            f"Documento: {d['name']}. "
            f"Objeto: {d['dimensions']['objeto_topologia'][:400]}. "
            f"Tecnologia: {d['dimensions']['especificacoes_tecnicas'][:400]}. "
            f"Contrato: {d['dimensions']['modelagem_contratual'][:300]}. "
            f"SLA: {d['dimensions']['sla_glosas'][:300]}."
        )
        global_summaries.append(summary)
        
    global_embs = model.encode(global_summaries, show_progress_bar=False, normalize_embeddings=True)
    global_dense_sim = cosine_similarity(global_embs)
    
    return dim_results, global_dense_sim

def main():
    print("=== INICIANDO PIPELINE DE ANÁLISE SEMÂNTICA ===", flush=True)
    docs = load_documents()
    print(f"Carregados {len(docs)} documentos com sucesso.", flush=True)
    
    # 1. Segmentação dimensional
    print("Segmentando documentos em dimensões conceituais...", flush=True)
    for d in docs:
        d["dimensions"] = extract_dimensions(d)
        
    # 2. Scikit-learn TF-IDF
    tfidf_sim, top_terms = run_tfidf_analysis(docs)
    
    # 3. Sentence-Transformers
    dim_results, global_dense_sim = run_sentence_transformers_analysis(docs)
    
    # 4. Consolidar scores comparativos contra o TR (Documento 0)
    print("\nConsolidando Scores de Similaridade frente ao TR 2215770...", flush=True)
    comparison_table = []
    
    for i, d in enumerate(docs):
        if i == 0:
            continue
        key = d["key"]
        name = d["name"]
        t_sim = float(tfidf_sim[0][i])
        d_sim = float(global_dense_sim[0][i])
        
        sim_obj = dim_results["objeto_topologia"]["vs_tr"][key]
        sim_tec = dim_results["especificacoes_tecnicas"]["vs_tr"][key]
        sim_mod = dim_results["modelagem_contratual"]["vs_tr"][key]
        sim_sla = dim_results["sla_glosas"]["vs_tr"][key]
        
        # Score ponderado global (Radar de Aderência)
        # Pesos: Objeto (30%), Especificações Técnicas (30%), Modelagem Contratual (20%), SLA/Glosas (20%)
        weighted_score = (sim_obj * 0.30) + (sim_tec * 0.30) + (sim_mod * 0.20) + (sim_sla * 0.20)
        
        row = {
            "ID_SEI": d["id"],
            "Chave": key,
            "Documento": name,
            "Tipo": d["type"],
            "Similaridade_TFIDF": round(t_sim, 4),
            "Similaridade_Densa_Global": round(d_sim, 4),
            "Sim_Objeto": round(sim_obj, 4),
            "Sim_Tecnica_SDWAN": round(sim_tec, 4),
            "Sim_Contratual": round(sim_mod, 4),
            "Sim_SLA_Glosas": round(sim_sla, 4),
            "Score_Aderencia_Ponderado": round(weighted_score, 4),
            "Top_Termos": top_terms[key][:6]
        }
        comparison_table.append(row)
        
    df_comparison = pd.DataFrame(comparison_table)
    df_sorted = df_comparison.sort_values(by="Score_Aderencia_Ponderado", ascending=False)
    
    print("\n=== RANKING DE ADERÊNCIA AO TR 2215770 (SENTENCE-TRANSFORMERS + TF-IDF) ===")
    print(df_sorted[["ID_SEI", "Chave", "Score_Aderencia_Ponderado", "Sim_Objeto", "Sim_Tecnica_SDWAN", "Sim_Contratual", "Sim_SLA_Glosas"]].to_string(index=False))
    
    # 5. Salvar resultados em JSON e CSV
    results_json = {
        "metadata": {
            "total_documents": len(docs),
            "reference_document": docs[0]["name"],
            "transformer_model": "paraphrase-multilingual-MiniLM-L12-v2",
            "tfidf_features": len(ALL_STOPWORDS)
        },
        "ranking": df_sorted.to_dict(orient="records"),
        "top_terms": top_terms,
        "dimensional_matrices": {dim: dim_results[dim]["matrix"] for dim in dim_results},
        "tfidf_matrix": tfidf_sim.tolist(),
        "global_dense_matrix": global_dense_sim.tolist()
    }
    
    out_json_path = os.path.join(DATA_DIR, "semantic_analysis_results.json")
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(results_json, f, ensure_ascii=False, indent=2)
        
    out_csv_path = os.path.join(DATA_DIR, "comparative_ranking.csv")
    df_sorted.to_csv(out_csv_path, index=False, encoding="utf-8-sig")
    
    print(f"\nResultados salvos com sucesso em:\n  - {out_json_path}\n  - {out_csv_path}")

if __name__ == "__main__":
    main()
