"""
Script de Análise Detalhada de Similaridade e Aderência de Escopo Técnico frente ao TR 2215770
Avalia os 9 documentos de referência e a Proposta Oi através de 8 critérios técnicos granulares
definidos no Termo de Referência da DPRJ.
"""

import sys
import os
import json
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\11429149760\.gemini\antigravity\scratch\analise_licitacao_telecom"
DATA_DIR = os.path.join(BASE_DIR, "data")

# Critérios técnicos de escopo do TR 2215770 da DPRJ
CRITERIA = [
    {
        "id": "C1_SDWAN",
        "nome": "Topologia SD-WAN & Orquestração Central",
        "peso": 15,
        "descricao": "Rede WAN gerenciada por software em malha (mesh) segura com console central em nuvem/software para provisionamento e roteamento dinâmico por aplicação."
    },
    {
        "id": "C2_SIMETRIA",
        "nome": "Simetria de Banda (1:1) & CIR 100%",
        "peso": 15,
        "descricao": "Circuitos com garantia integral de banda contratada (CIR=100%), simetria total de download/upload, sem franquia e com IP fixo válido."
    },
    {
        "id": "C3_NGFW_IPS",
        "nome": "Segurança de Borda Integrada (NGFW + IPS)",
        "peso": 15,
        "descricao": "Ativos de borda com firewall de próxima geração (NGFW), inspeção profunda de pacotes, IPS nativo e defesa contra malware/DDoS."
    },
    {
        "id": "C4_3_PERFIS",
        "nome": "Arquitetura de 3 Perfis Físicos Fixos",
        "peso": 15,
        "descricao": "Appliances dimensionados em 3 perfis físicos fixos para permitir upgrade ou downgrade lógico de velocidade sem aditivo contratual de hardware."
    },
    {
        "id": "C5_REDUNDANCIA",
        "nome": "Redundância & Failover Ativo (Link K2)",
        "peso": 10,
        "descricao": "Capacidade de integrar e balancear dinamicamente o tráfego com o segundo link assimétrico existente via Contrato 20/2024 (K2 Telecom)."
    },
    {
        "id": "C6_CAPILARIDADE",
        "nome": "Capilaridade Territorial no Estado do RJ (+DF)",
        "peso": 10,
        "descricao": "Atendimento a 159 unidades operacionais distribuídas pela capital, Baixada, Região dos Lagos, Norte, Noroeste, Serrana e Centro-Sul do RJ + Brasília-DF."
    },
    {
        "id": "C7_GERENCIADO",
        "nome": "Serviço Gerenciado 24x7x365 & Telemetria",
        "peso": 10,
        "descricao": "Fornecimento sob modelo OPEX com manutenção presencial, troca de equipamentos com defeito e console de monitoramento em tempo real."
    },
    {
        "id": "C8_SLA_RIGOR",
        "nome": "SLA Rigoroso (Disp. >= 99,5% & Glosa Direta)",
        "peso": 10,
        "descricao": "Disponibilidade mínima mensal de 99,5%, apuração automática do início da falha por telemetria nos gráficos e glosas diretas em fatura até 30%."
    }
]

# Avaliação granular de cada documento (Notas de 0 a 10 em cada critério)
DOC_EVALUATION = [
    {
        "id": "2215770",
        "key": "TR_DPRJ",
        "nome": "Termo de Referência 2215770 (DPRJ)",
        "papel": "Padrão de Referência Absoluto (100%)",
        "notas": {
            "C1_SDWAN": 10,
            "C2_SIMETRIA": 10,
            "C3_NGFW_IPS": 10,
            "C4_3_PERFIS": 10,
            "C5_REDUNDANCIA": 10,
            "C6_CAPILARIDADE": 10,
            "C7_GERENCIADO": 10,
            "C8_SLA_RIGOR": 10
        },
        "destaques": "Documento base de referência técnica e jurídica elaborado pela DPRJ.",
        "gaps_vs_tr": "Nenhum (Matriz padrão)."
    },
    {
        "id": "2219726",
        "key": "GSNT",
        "nome": "Proposta GSNT Telecom",
        "papel": "Cotação Direta de Mercado",
        "notas": {
            "C1_SDWAN": 9.5,
            "C2_SIMETRIA": 10.0,
            "C3_NGFW_IPS": 9.0,
            "C4_3_PERFIS": 8.5,
            "C5_REDUNDANCIA": 9.0,
            "C6_CAPILARIDADE": 10.0,
            "C7_GERENCIADO": 9.0,
            "C8_SLA_RIGOR": 8.5
        },
        "destaques": "Cotou especificamente para as 159 unidades da DPRJ nos lotes solicitados, contemplando link simétrico com SD-WAN e segurança integrada.",
        "gaps_vs_tr": "Detalhamento genérico sobre a telemetria do orquestrador; submissão passiva ao modelo do TR sem detalhar matriz própria de MTTR."
    },
    {
        "id": "2219741",
        "key": "PREGAO_MPRJ",
        "nome": "Pregão 90020/2024 MPRJ",
        "papel": "Contratação Pública Estadual (RJ)",
        "notas": {
            "C1_SDWAN": 7.5,
            "C2_SIMETRIA": 10.0,
            "C3_NGFW_IPS": 8.0,
            "C4_3_PERFIS": 5.0,
            "C5_REDUNDANCIA": 9.5,
            "C6_CAPILARIDADE": 10.0,
            "C7_GERENCIADO": 9.5,
            "C8_SLA_RIGOR": 10.0
        },
        "destaques": "Mesma malha territorial fluminense (comarcas do interior e capital); links dedicados com redundância ativa obrigatória (100+50 e 200+100 Mbps); SLA idêntico de 99,5% com regime de glosas mensais rigoroso.",
        "gaps_vs_tr": "Não adota a cláusula de 3 perfis físicos fixos para upgrade sem aditivo; redundância provida por dois enlaces contratados no mesmo edital em vez de failover com 2º contrato (K2)."
    },
    {
        "id": "2219742",
        "key": "CONTRATO_MTE",
        "nome": "Contrato 18/2024 MTE / Telebras",
        "papel": "Contrato Federal (Telebras SD-WAN)",
        "notas": {
            "C1_SDWAN": 10.0,
            "C2_SIMETRIA": 9.0,
            "C3_NGFW_IPS": 10.0,
            "C4_3_PERFIS": 9.0,
            "C5_REDUNDANCIA": 8.0,
            "C6_CAPILARIDADE": 5.0,
            "C7_GERENCIADO": 9.5,
            "C8_SLA_RIGOR": 8.0
        },
        "destaques": "Arquitetura técnica mais próxima do ideal em SD-WAN e segurança: CPEs inteligentes estratificados em perfis (Small, Mid, Enterprise), NGFW Premium com suporte de fabricante e gestão centralizada pelo NSOC da Telebras.",
        "gaps_vs_tr": "Escopo geográfico nacional (agências do trabalho em todo o Brasil) sem correlação direta com a capilaridade das comarcas isoladas do Estado do RJ; não prevê integração com o link K2 Telecom."
    },
    {
        "id": "2219747",
        "key": "PREGAO_TJMRS",
        "nome": "Pregão 2/2026 TJMRS",
        "papel": "Contratação Pública Estadual (RS)",
        "notas": {
            "C1_SDWAN": 8.5,
            "C2_SIMETRIA": 9.5,
            "C3_NGFW_IPS": 7.5,
            "C4_3_PERFIS": 5.0,
            "C5_REDUNDANCIA": 9.0,
            "C6_CAPILARIDADE": 3.0,
            "C7_GERENCIADO": 8.5,
            "C8_SLA_RIGOR": 9.5
        },
        "destaques": "Interligação com tecnologia SD-WAN e túneis IPsec criptografados; links simétricos com contingência e agregação de banda (100+50 Mbps); SLA rigoroso de 99,5% com sanções por glosa direta.",
        "gaps_vs_tr": "Escopo territorial diminuto (apenas 4 localidades militares no Rio Grande do Sul: Porto Alegre, Santa Maria e Passo Fundo); não possui a lógica de 3 perfis fixos de hardware."
    },
    {
        "id": "2219728",
        "key": "PREGAO_MPES",
        "nome": "Pregão 90037/2025 MPES",
        "papel": "Contratação Pública Estadual (ES)",
        "notas": {
            "C1_SDWAN": 8.0,
            "C2_SIMETRIA": 9.0,
            "C3_NGFW_IPS": 9.0,
            "C4_3_PERFIS": 4.0,
            "C5_REDUNDANCIA": 7.0,
            "C6_CAPILARIDADE": 5.0,
            "C7_GERENCIADO": 8.0,
            "C8_SLA_RIGOR": 7.5
        },
        "destaques": "Foco prioritário em ampliação de segurança cibernética com tecnologia SD-WAN e links dedicados para promotorias de justiça no Sudeste (ES).",
        "gaps_vs_tr": "Edital focado em expansão de segurança perimetral (UTM/NGFW) com conectividade secundária; não possui modelagem de 3 perfis físicos fixos nem abrangência no Rio de Janeiro."
    },
    {
        "id": "2219730",
        "key": "PREGAO_DTI_PF",
        "nome": "Pregão 90009/2025 DTI / PF",
        "papel": "Pregão SRP Federal Nacional",
        "notas": {
            "C1_SDWAN": 9.5,
            "C2_SIMETRIA": 6.5,
            "C3_NGFW_IPS": 8.0,
            "C4_3_PERFIS": 4.0,
            "C5_REDUNDANCIA": 8.5,
            "C6_CAPILARIDADE": 4.0,
            "C7_GERENCIADO": 9.0,
            "C8_SLA_RIGOR": 7.0
        },
        "destaques": "Orquestração SD-WAN de grande porte interligando centenas de pontos em território nacional; alta maturidade na gerência de tráfego por aplicação.",
        "gaps_vs_tr": "Transporte híbrido com forte dependência de conexões satelitais e banda larga assimétrica com CIR reduzido (incompatível com os links simétricos dedicados 1:1 exigidos pela DPRJ); não atende à malha das comarcas fluminenses."
    },
    {
        "id": "2219727",
        "key": "PREGAO_GO",
        "nome": "Pregão 107458/2025 Sec. Geral GO",
        "papel": "Contratação Pública Estadual (GO)",
        "notas": {
            "C1_SDWAN": 8.0,
            "C2_SIMETRIA": 6.0,
            "C3_NGFW_IPS": 5.5,
            "C4_3_PERFIS": 3.0,
            "C5_REDUNDANCIA": 6.5,
            "C6_CAPILARIDADE": 3.0,
            "C7_GERENCIADO": 7.5,
            "C8_SLA_RIGOR": 7.5
        },
        "destaques": "Contratação de circuitos terrestres de acesso à internet corporativa com tecnologia SD-WAN em Goiás.",
        "gaps_vs_tr": "Internet banda larga terrestre simples, sem garantia de simetria plena 1:1, sem camada robusta de NGFW/IPS integrado nos CPEs e sem os 3 perfis físicos fixos; abrangência exclusiva em Goiás."
    },
    {
        "id": "2219752",
        "key": "OI_ATUAL",
        "nome": "Proposta Oi (Contrato Vigente DPRJ)",
        "papel": "Contrato Vigente em Extinção (DPRJ)",
        "notas": {
            "C1_SDWAN": 5.0,
            "C2_SIMETRIA": 9.5,
            "C3_NGFW_IPS": 4.0,
            "C4_3_PERFIS": 2.0,
            "C5_REDUNDANCIA": 6.0,
            "C6_CAPILARIDADE": 10.0,
            "C7_GERENCIADO": 8.5,
            "C8_SLA_RIGOR": 7.5
        },
        "destaques": "Atendimento pleno a 100% da malha geográfica da instituição (as 159 unidades da DPRJ no RJ e Brasília-DF); links simétricos de alta qualidade operacional.",
        "gaps_vs_tr": "Arquitetura legada de conectividade WAN tradicional, sem o orquestrador SD-WAN moderno, sem ativos de borda com NGFW/IPS integrado e sem a inovação de 3 perfis físicos para alteração de banda sem aditivo."
    },
    {
        "id": "2219745",
        "key": "CD_FUPESC",
        "nome": "Proposta CD 75/2025 FUPESC",
        "papel": "Contratação Direta Estadual (SC)",
        "notas": {
            "C1_SDWAN": 3.0,
            "C2_SIMETRIA": 6.0,
            "C3_NGFW_IPS": 4.0,
            "C4_3_PERFIS": 1.0,
            "C5_REDUNDANCIA": 4.0,
            "C6_CAPILARIDADE": 2.0,
            "C7_GERENCIADO": 6.0,
            "C8_SLA_RIGOR": 6.5
        },
        "destaques": "Fornecimento de links dedicados e internet para presídios em Santa Catarina sob prazo anual de 12 meses.",
        "gaps_vs_tr": "Trata-se de link de internet/conectividade pura via provedores regionais de SC; ausência de arquitetura SD-WAN gerenciada, sem NGFW e sem nenhuma aderência geográfica com o Estado do Rio de Janeiro."
    }
]

def calculate_adherence():
    results = []
    
    for doc in DOC_EVALUATION:
        total_score_weighted = 0.0
        max_score_weighted = 0.0
        
        row = {
            "ID_SEI": doc["id"],
            "Chave": doc["key"],
            "Documento": doc["nome"],
            "Papel": doc["papel"],
        }
        
        for c in CRITERIA:
            c_id = c["id"]
            peso = c["peso"]
            nota = doc["notas"][c_id]
            
            # Adicionar nota por critério
            row[c_id] = nota
            total_score_weighted += nota * (peso / 10.0)
            max_score_weighted += 10.0 * (peso / 10.0)
            
        aderencia_pct = round((total_score_weighted / max_score_weighted) * 100, 2)
        row["Pontos_Ponderados"] = round(total_score_weighted, 2)
        row["Aderencia_Escopo_Pct"] = aderencia_pct
        
        # Classificação de aderência
        if aderencia_pct >= 95.0:
            grau = "Padrão de Referência (100%)"
        elif aderencia_pct >= 85.0:
            grau = "Altíssima Aderência"
        elif aderencia_pct >= 75.0:
            grau = "Alta Aderência"
        elif aderencia_pct >= 60.0:
            grau = "Aderência Moderada"
        elif aderencia_pct >= 45.0:
            grau = "Baixa Aderência"
        else:
            grau = "Muito Baixa Aderência"
            
        row["Grau_Aderencia"] = grau
        row["Destaques"] = doc["destaques"]
        row["Gaps_vs_TR"] = doc["gaps_vs_tr"]
        
        results.append(row)
        
    df = pd.DataFrame(results)
    df_sorted = df.sort_values(by="Aderencia_Escopo_Pct", ascending=False)
    
    print("\n=== RANKING DE ADERÊNCIA DE ESCOPO TÉCNICO AO TR 2215770 ===")
    print(df_sorted[["ID_SEI", "Chave", "Aderencia_Escopo_Pct", "Grau_Aderencia", "C1_SDWAN", "C3_NGFW_IPS", "C4_3_PERFIS", "C6_CAPILARIDADE"]].to_string(index=False))
    
    # Salvar em CSV e JSON
    out_csv = os.path.join(DATA_DIR, "aderencia_escopo_tecnico_tr2215770.csv")
    df_sorted.to_csv(out_csv, index=False, encoding="utf-8-sig")
    
    out_json = os.path.join(DATA_DIR, "aderencia_escopo_tecnico_tr2215770.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(df_sorted.to_dict(orient="records"), f, ensure_ascii=False, indent=2)
        
    print(f"\nResultados gravados em:\n  - {out_csv}\n  - {out_json}")

if __name__ == "__main__":
    calculate_adherence()
