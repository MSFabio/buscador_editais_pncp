"""
Script de Análise Semântica e Normalização Econômica com Base na Proposta Oi (2219752)
1. Utiliza a Proposta Oi (Contrato Vigente) como régua comparativa semântica e técnica.
2. Normaliza os valores de pregões/editais com vigência > 12 meses para a base de 12 meses.
3. Compara cada proposta e o TR frente aos parâmetros da Oi.
"""

import sys
import os
import json
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\11429149760\.gemini\antigravity\scratch\analise_licitacao_telecom"
MD_DIR = os.path.join(BASE_DIR, "markdown")
DATA_DIR = os.path.join(BASE_DIR, "data")

DOCUMENTS = [
    {
        "id": "2219752",
        "key": "OI_ATUAL",
        "name": "Proposta Oi - Valor Atual Contratado (2219752)",
        "file": "10_Proposta_Oi_Valor_Atual_2219752.md",
        "role": "Régua Comparativa Central (Baseline)",
        "vigencia_meses": 30,
        "precos_brutos": {"80mbps": 1488.61, "100mbps": 1653.14, "300mbps": 2795.41}
    },
    {
        "id": "2215770",
        "key": "TR_DPRJ",
        "name": "Termo de Referência 2215770 (DPRJ)",
        "file": "01_TR_2215770.md",
        "role": "Novo Termo Emergencial (12 meses)",
        "vigencia_meses": 12,
        "precos_brutos": {"80mbps": None, "100mbps": None, "300mbps": None}
    },
    {
        "id": "2219726",
        "key": "GSNT",
        "name": "Proposta GSNT Telecom (2219726)",
        "file": "02_Proposta_GSNT_2219726.md",
        "role": "Cotação Direta de Mercado",
        "vigencia_meses": 30,
        "precos_brutos": {"80mbps": 5200.00, "100mbps": 5900.00, "300mbps": 6900.00}
    },
    {
        "id": "2219727",
        "key": "PREGAO_GO",
        "name": "Pregão 107458/2025 Sec. Geral GO (2219727)",
        "file": "03_Pregao_GO_107458_2025_2219727.md",
        "role": "Contratação Pública Estadual (GO)",
        "vigencia_meses": 36,
        "precos_brutos": {"80mbps": None, "100mbps": 462.43, "300mbps": None}
    },
    {
        "id": "2219728",
        "key": "PREGAO_MPES",
        "name": "Pregão 90037/2025 MPES (2219728)",
        "file": "04_Pregao_MPES_90037_2025_2219728.md",
        "role": "Contratação Pública Estadual (ES)",
        "vigencia_meses": 30,
        "precos_brutos": {"80mbps": 1243.55, "100mbps": 848.12, "300mbps": None}
    },
    {
        "id": "2219730",
        "key": "PREGAO_DTI_PF",
        "name": "Pregão 90009/2025 DTI / PF (2219730)",
        "file": "05_Pregao_DTI_PF_90009_2025_2219730.md",
        "role": "Pregão SRP Federal Nacional",
        "vigencia_meses": 30,
        "precos_brutos": {"80mbps": None, "100mbps": 323.24, "300mbps": None}
    },
    {
        "id": "2219741",
        "key": "PREGAO_MPRJ",
        "name": "Pregão 90020/2024 MPRJ (2219741)",
        "file": "06_Pregao_MPRJ_90020_2024_2219741.md",
        "role": "Contratação Pública Estadual (RJ)",
        "vigencia_meses": 36,
        "precos_brutos": {"80mbps": 2055.23, "100mbps": 2473.94, "300mbps": 3873.15}
    },
    {
        "id": "2219742",
        "key": "CONTRATO_MTE",
        "name": "Contrato 18/2024 MTE / Telebras (2219742)",
        "file": "07_Contrato_MTE_18_2024_Telebras_2219742.md",
        "role": "Contrato Federal Continuado",
        "vigencia_meses": 60,
        "precos_brutos": {"80mbps": None, "100mbps": 4919.56, "300mbps": 8978.36}
    },
    {
        "id": "2219745",
        "key": "CD_FUPESC",
        "name": "Proposta CD 75/2025 FUPESC (2219745)",
        "file": "08_CD_FUPESC_75_2025_2219745.md",
        "role": "Contratação Direta Estadual (SC)",
        "vigencia_meses": 12,
        "precos_brutos": {"80mbps": None, "100mbps": 1148.00, "300mbps": None}
    },
    {
        "id": "2219747",
        "key": "PREGAO_TJMRS",
        "name": "Pregão 2/2026 TJMRS (2219747)",
        "file": "09_Pregao_TJMRS_2_2026_2219747.md",
        "role": "Contratação Pública Estadual (RS)",
        "vigencia_meses": 48,
        "precos_brutos": {"80mbps": None, "100mbps": 1200.00, "300mbps": None}
    }
]

# Quantitativos de circuitos da DPRJ (159 unidades)
QUANTIDADES = {
    "80mbps": 102,
    "100mbps": 35,
    "300mbps": 22
}

def load_documents_text():
    docs = []
    for d in DOCUMENTS:
        fp = os.path.join(MD_DIR, d["file"])
        with open(fp, "r", encoding="utf-8") as f:
            txt = f.read()
        d_copy = dict(d)
        d_copy["raw_text"] = txt
        docs.append(d_copy)
    return docs

def extract_dimensions_oi_baseline(doc):
    txt = doc["raw_text"]
    paragraphs = txt.split("\n\n")
    obj_pars, tec_pars, mod_pars, sla_pars = [], [], [], []
    for p in paragraphs:
        p_clean = " ".join(p.split())
        if len(p_clean) < 25:
            continue
        p_lower = p_clean.lower()
        if any(w in p_lower for w in ["objeto", "link", "circuito", "conectividade", "simétrico", "dedicado", "wan", "comunicação de dados"]):
            obj_pars.append(p_clean)
        if any(w in p_lower for w in ["sd-wan", "sdwan", "mpls", "roteador", "cpe", "equipamento", "hardware", "firewall", "ngfw"]):
            tec_pars.append(p_clean)
        if any(w in p_lower for w in ["vigência", "vigencia", "30 meses", "12 meses", "36 meses", "contrato", "pagamento", "reajuste", "icti"]):
            mod_pars.append(p_clean)
        if any(w in p_lower for w in ["sla", "nível", "disponibilidade", "glosa", "penalidade", "suporte"]):
            sla_pars.append(p_clean)
            
    return {
        "objeto": " ".join(obj_pars[:15]) if obj_pars else p_clean[:800],
        "tecnica": " ".join(tec_pars[:15]) if tec_pars else p_clean[:800],
        "contrato": " ".join(mod_pars[:15]) if mod_pars else p_clean[:800],
        "sla": " ".join(sla_pars[:15]) if sla_pars else p_clean[:800]
    }

def run_semantic_recalculation(docs):
    print("Recalculando análise semântica com a Proposta Oi (2219752) como régua...", flush=True)
    model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
    
    # Gerar embeddings por dimensão
    dims = ["objeto", "tecnica", "contrato", "sla"]
    dim_scores = {dim: {} for dim in dims}
    
    for dim in dims:
        texts = [d["dimensions"][dim] for d in docs]
        embs = model.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        # Índice 0 é a Oi Atual
        oi_emb = embs[0:1]
        sims = cosine_similarity(oi_emb, embs)[0]
        for idx, d in enumerate(docs):
            dim_scores[dim][d["key"]] = float(sims[idx])
            
    # TF-IDF contra Oi
    stop_pt = set(stopwords.words('portuguese')).union({
        'fls', 'sei', 'processo', 'art', 'nº', 'dprj', 'dperj', 'sob', 'item', 'contrato', 
        'serviço', 'serviços', 'empresa', 'contratada', 'contratante', 'r', 'reais', 'total', 'unidade'
    })
    corpus = [d["raw_text"] for d in docs]
    vec = TfidfVectorizer(stop_words=list(stop_pt), ngram_range=(1, 2), max_df=0.90, min_df=2, sublinear_tf=True)
    tfidf_mat = vec.fit_transform(corpus)
    tfidf_sims_to_oi = cosine_similarity(tfidf_mat[0:1], tfidf_mat)[0]
    
    return dim_scores, tfidf_sims_to_oi

def calculate_duration_normalization():
    """
    Calcula o Fator de Normalização de Vigência (FNV) para converter preços de T meses para 12 meses:
    FNV(T, alpha) = (1 - alpha) + alpha * (T / 12)
    Onde alpha é a taxa de amortização de CAPEX / instalação inicial (benchmark de mercado = 25%).
    """
    alpha = 0.25 # 25% CAPEX / 75% OPEX
    norm_results = []
    
    oi_prices = DOCUMENTS[0]["precos_brutos"]
    oi_monthly_total_159 = (
        oi_prices["80mbps"] * QUANTIDADES["80mbps"] +
        oi_prices["100mbps"] * QUANTIDADES["100mbps"] +
        oi_prices["300mbps"] * QUANTIDADES["300mbps"]
    )
    oi_annual_total = oi_monthly_total_159 * 12
    
    print(f"\n--- BASELINE OI SOLUÇÕES (2219752) ---")
    print(f"Mensalidade 159 Unidades: R$ {oi_monthly_total_159:,.2f}")
    print(f"Anualidade (12 meses): R$ {oi_annual_total:,.2f}")
    
    for d in DOCUMENTS:
        key = d["key"]
        T = d["vigencia_meses"]
        fnv = (1.0 - alpha) + alpha * (T / 12.0)
        
        raw_p = d["precos_brutos"]
        # Preços normalizados para 12 meses
        norm_p = {}
        for speed, p in raw_p.items():
            if p is not None:
                # Se T > 12, para cumprir em apenas 12 meses o fornecedor precisa de uma taxa mensal maior para recuperar o CAPEX
                # P_12 = P_T * FNV
                norm_p[speed] = round(p * fnv, 2)
            else:
                norm_p[speed] = None
                
        # Total mensal normalizado para os 159 circuitos da DPRJ (onde disponível)
        mensal_159 = 0.0
        itens_disponiveis = 0
        if norm_p["80mbps"] is not None:
            mensal_159 += norm_p["80mbps"] * QUANTIDADES["80mbps"]
            itens_disponiveis += 1
        if norm_p["100mbps"] is not None:
            mensal_159 += norm_p["100mbps"] * QUANTIDADES["100mbps"]
            itens_disponiveis += 1
        if norm_p["300mbps"] is not None:
            mensal_159 += norm_p["300mbps"] * QUANTIDADES["300mbps"]
            itens_disponiveis += 1
            
        anual_159 = mensal_159 * 12.0 if itens_disponiveis == 3 else None
        
        # Comparativo percentual frente à Oi (100 Mbps)
        diff_oi_100_raw = round(((raw_p["100mbps"] - oi_prices["100mbps"]) / oi_prices["100mbps"]) * 100, 2) if raw_p["100mbps"] else None
        diff_oi_100_norm = round(((norm_p["100mbps"] - oi_prices["100mbps"]) / oi_prices["100mbps"]) * 100, 2) if norm_p["100mbps"] else None
        
        norm_results.append({
            "id": d["id"],
            "key": key,
            "documento": d["name"],
            "papel": d["role"],
            "vigencia_original_meses": T,
            "fator_normalizacao_fnv": round(fnv, 4),
            "preco_bruto_80mbps": raw_p["80mbps"],
            "preco_norm_80mbps": norm_p["80mbps"],
            "preco_bruto_100mbps": raw_p["100mbps"],
            "preco_norm_100mbps": norm_p["100mbps"],
            "preco_bruto_300mbps": raw_p["300mbps"],
            "preco_norm_300mbps": norm_p["300mbps"],
            "diff_oi_100mbps_bruto_pct": diff_oi_100_raw,
            "diff_oi_100mbps_norm_pct": diff_oi_100_norm,
            "total_mensal_159_norm": round(mensal_159, 2) if itens_disponiveis == 3 else None,
            "total_anual_12m_norm": round(anual_159, 2) if itens_disponiveis == 3 else None
        })
        
    return norm_results

def main():
    print("=== PIPELINE: RÉGUA COMPARATIVA OI (2219752) & NORMALIZAÇÃO DE VIGÊNCIA ===")
    docs = load_documents_text()
    for d in docs:
        d["dimensions"] = extract_dimensions_oi_baseline(d)
        
    dim_scores, tfidf_sims = run_semantic_recalculation(docs)
    norm_econ = calculate_duration_normalization()
    
    # Combinar resultados semânticos e econômicos
    consolidated_table = []
    for idx, d in enumerate(docs):
        key = d["key"]
        econ = norm_econ[idx]
        
        sim_obj = dim_scores["objeto"][key]
        sim_tec = dim_scores["tecnica"][key]
        sim_mod = dim_scores["contrato"][key]
        sim_sla = dim_scores["sla"][key]
        sim_tfidf = float(tfidf_sims[idx])
        
        # Score ponderado frente à Oi
        weighted_sim = (sim_obj * 0.30) + (sim_tec * 0.30) + (sim_mod * 0.20) + (sim_sla * 0.20)
        
        row = {
            "ID_SEI": d["id"],
            "Chave": key,
            "Documento": d["name"],
            "Vigencia_Original": d["vigencia_meses"],
            "FNV_Fator": econ["fator_normalizacao_fnv"],
            "Sim_Global_Oi": round(weighted_sim, 4),
            "Sim_Objeto_Oi": round(sim_obj, 4),
            "Sim_Tecnica_Oi": round(sim_tec, 4),
            "Sim_Contratual_Oi": round(sim_mod, 4),
            "Sim_SLA_Oi": round(sim_sla, 4),
            "Preco_Bruto_100M": econ["preco_bruto_100mbps"],
            "Preco_Norm_100M_12m": econ["preco_norm_100mbps"],
            "Variacao_vs_Oi_Bruta_Pct": econ["diff_oi_100mbps_bruto_pct"],
            "Variacao_vs_Oi_Norm_Pct": econ["diff_oi_100mbps_norm_pct"],
            "Preco_Norm_80M_12m": econ["preco_norm_80mbps"],
            "Preco_Norm_300M_12m": econ["preco_norm_300mbps"],
            "Total_Anual_12m_Norm": econ["total_anual_12m_norm"]
        }
        consolidated_table.append(row)
        
    df = pd.DataFrame(consolidated_table)
    df_sorted = df.sort_values(by="Sim_Global_Oi", ascending=False)
    
    print("\n=== RANKING DE SIMILARIDADE FRENTE À PROPOSTA OI (RÉGUA BASE) ===")
    print(df_sorted[["ID_SEI", "Chave", "Vigencia_Original", "Sim_Global_Oi", "Sim_Objeto_Oi", "Sim_Tecnica_Oi", "Preco_Norm_100M_12m", "Variacao_vs_Oi_Norm_Pct"]].to_string(index=False))
    
    out_json = os.path.join(DATA_DIR, "oi_reference_recalculated_analysis.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(consolidated_table, f, ensure_ascii=False, indent=2)
        
    out_csv = os.path.join(DATA_DIR, "oi_reference_recalculated_analysis.csv")
    df.to_csv(out_csv, index=False, encoding="utf-8-sig")
    
    print(f"\nResultados gravados com sucesso em:\n  - {out_json}\n  - {out_csv}")

if __name__ == "__main__":
    main()
