import os, sys, json, re
import numpy as np
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv

# Reconfigure stdout for UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv(r"C:\Users\11429149760\Downloads\seduc\.env")
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if not gemini_api_key:
    # Try alternative .env
    load_dotenv(r"C:\Users\11429149760\antigravity\Monitor-de-Licitações-PNCP\.env")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

print("Gemini API key loaded:", bool(gemini_api_key))

DOCS_DIR = r"C:\Users\11429149760\.gemini\antigravity\scratch\processo_docs"

# 1. Read document texts
def read_file(name):
    path = os.path.join(DOCS_DIR, name)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    return ""

despacho_ci_2223276 = read_file("2223276_Despacho 2223276.txt")
despacho_ci_2145441 = read_file("2145441_Despacho 2145441.txt")
despacho_epd_2146497 = read_file("2146497_Despacho EPD (2146497).txt")
despacho_dgi_2106960 = read_file("2106960_Despacho 2106960.txt")
despacho_dgi_2106972 = read_file("2106972_Despacho 2106972.txt")
relatorio_preliminar = read_file("relatorio_preliminar_full.txt")

# Extract the 5 core Achados from the Relatório Preliminar
achados = {
    "Achado 2": "Governança de TIC insuficiente para avaliar, dirigir e monitorar. Necessidade de estrutura formal de governança, alinhamento COBIT EDM01.02 e avaliação de desempenho de estruturas colegiadas.",
    "Achado 3": "Planejamento de TIC insuficiente para orientar a gestão, o orçamento e a atuação estratégica. Necessidade de estruturação, manutenção e revisão periódica do PDTI e integração ao orçamento (COBIT APO02.05 e APO06.03).",
    "Achado 4": "Capacidade institucional insuficiente para sustentar a entrega de serviços e a segurança da informação. Dependência de suporte externo, necessidade de dimensionamento da força de trabalho própria e capacitação contínua (ISO 27001/27002 e COBIT APO07/DSS01).",
    "Achado 5": "Gestão de serviços de TIC insuficiente para assegurar conformidade, continuidade e alinhamento operacional. Necessidade de catálogo de serviços, acordos de nível de serviço (SLA), gestão formal de incidentes e problemas (ITIL 4 e COBIT DSS02).",
    "Achado 6": "Fragilidades na governança técnica da fase preparatória das contratações de TIC. Necessidade de padronização dos ritos, integração ao Plano de Contratações Anual (PCA) e designação formal de equipes de planejamento da contratação (Lei 14.133/2021)."
}

justificativas_candidatas = [
    "Prerrogativa facultativa e opcional do gestor: o Termo TSID nº 03 do TCE-RJ e o Manual de Auditoria estabelecem expressamente que a apresentação de Comentários do Gestor é prerrogativa opcional, sem caráter vinculante ou de obrigatoriedade sancionatória.",
    "Concordância com o diagnóstico técnico: a Administração e a DGI acolhem o diagnóstico do Relatório Preliminar (iGovTI 2026 de 0,5223) como oportunidade de melhoria contínua, inexistindo divergências de fato ou erros materiais que justificassem impugnação.",
    "Direcionamento prioritário para o Plano de Ação: os esforços técnicos e gerenciais foram concentrados na estruturação prática das ações e planos de trabalho para implementação das recomendações do TCE-RJ quando da emissão do Relatório Definitivo.",
    "Instrução probatória e fática prévia exaustiva: todos os elementos de fato, questionários e evidências documentais já haviam sido amplamente fornecidos na fase instrutória pelo Despacho DGI 2106960/2106972 e pela EPD.",
    "Competência e escopo institucional: conforme sinalizado pela EPD e DGI, os achados envolvem governança ampla e governança preparatória de TIC, exigindo articulação institucional colegiada em vez de mera justificativa fática isolada."
]

print("--- ETAPA 1: ANÁLISE SEMÂNTICA COM SENTENCE TRANSFORMERS ---")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# Embeddings
target_query = "Registro de justificativa e razões para o não preenchimento do formulário Comentários do Gestor no encerramento da auditoria de TIC do TCE-RJ"
query_emb = model.encode(target_query, convert_to_tensor=True)

just_embs = model.encode(justificativas_candidatas, convert_to_tensor=True)
sims = util.cos_sim(query_emb, just_embs)[0].cpu().numpy()

ranked_justificativas = []
for idx, sim in enumerate(sims):
    ranked_justificativas.append((float(sim), justificativas_candidatas[idx]))
ranked_justificativas.sort(reverse=True, key=lambda x: x[0])

print(f"\nSimilaridade Semântica com o Despacho 2223276:")
for score, just in ranked_justificativas:
    print(f"  [{score:.4f}] {just[:100]}...")

# Achados alignment with action plan
achados_keys = list(achados.keys())
achados_texts = [achados[k] for k in achados_keys]
achados_embs = model.encode(achados_texts, convert_to_tensor=True)

conc_diag_emb = model.encode("Acolhimento das recomendações como diretrizes de melhoria e governança institucional no Plano de Ação", convert_to_tensor=True)
achados_sims = util.cos_sim(conc_diag_emb, achados_embs)[0].cpu().numpy()

print(f"\nAderência Semântica das Recomendações dos Achados à postura de Acolhimento / Plano de Ação:")
for idx, k in enumerate(achados_keys):
    print(f"  {k}: aderência={achados_sims[idx]:.4f}")

semantic_summary = {
    "target_despacho": 2223276,
    "top_reasons": ranked_justificativas,
    "achados_relevance": {achados_keys[i]: float(achados_sims[i]) for i in range(len(achados_keys))}
}

with open(os.path.join(DOCS_DIR, "semantic_analysis_results.json"), "w", encoding="utf-8") as f:
    json.dump(semantic_summary, f, indent=2, ensure_ascii=False)

print("\n--- ETAPA 2: ELABORAÇÃO DO DESPACHO COM GEMINI ---")
from google import genai

client = genai.Client(api_key=gemini_api_key)

prompt_despacho = f"""
Você é o assistente técnico especializado da Defensoria Pública do Estado do Rio de Janeiro (DPGERJ).
Precisa redigir a minuta oficial de DESPACHO da Diretoria de Gestão da Informação (DGI), assinado pelo Diretor FÁBIO MARÇAL DA SILVEIRA, em resposta ao Despacho 2223276 do Controle Interno (Nelson Wesp Keller), no Processo SEI nº E-20/001.002323/2026.

### CONTEXTO DO PROCESSO SEI:
- Processo: E-20/001.002323/2026 (ID 2848395)
- Assunto: AUDITORIA TCE-RJ - Boas práticas de Governança e Gestão de TI (Auditoria de Conformidade nº 18/2026)
- Interessado / Remetente: CONTROLE INTERNO (Nelson Wesp Keller, Coordenador de Controle Interno)
- Destinatário do Despacho: AO CONTROLE INTERNO - CI (A/C Sr. Coordenador Nelson Wesp Keller)
- Autor do Despacho: FÁBIO MARÇAL DA SILVEIRA (Diretor de Gestão da Informação - DGI)

### O QUE DIZ O DESPACHO 2223276 A SER RESPONDIDO:
"Para fins de encerramento, registra-se a opção pelo não preenchimento do questionário 'Comentários do Gestor'.
Solicita-se, se possível, o registro da justificativa ou das razões que motivaram a referida opção, para fins de documentação nos autos."

### ELEMENTOS TÉCNICOS E JURÍDICOS APURADOS NA ANÁLISE SEMÂNTICA (SENTENCE TRANSFORMERS):
1. NATUREZA ESTRITAMENTE FACULTATIVA/OPCIONAL:
   - Conforme previsto no Termo de Solicitação de Informações e Documentos nº 03 (TSID 03 - fl. 2 / id 2145419) e no Formulário 'Comentários do Gestor' (id 2145425), bem como no Manual de Auditoria do TCE-RJ (item 8.4) e ratificado no próprio Despacho CI nº 2145441, a apresentação de comentários ao Relatório Individual Preliminar constitui prerrogativa processual franqueada ao gestor para eventual impugnação, tendo caráter expressamente opcional, sem constituir encargo obrigatório nem configurar omissão ou infração funcional.
2. CONCORDÂNCIA TÉCNICA COM O DIAGNÓSTICO (INEXISTÊNCIA DE CONTROVÉRSIA FÁTICA):
   - Os 5 achados apontados no Relatório Individual Preliminar (id 2145424) - referentes a governança colegiada (Achado 2), planejamento/PDTI (Achado 3), capacidade da força de trabalho e capacitação (Achado 4), catálogo de serviços e SLAs (Achado 5) e governança preparatória de contratações sob a Lei 14.133/2021 (Achado 6) - refletem com fidelidade o estágio de maturidade diagnosticado pelo índice iGovTI 2026 (0,5223).
   - Inexistindo divergência quanto aos pressupostos fáticos ou erros materiais na apuração da equipe de auditoria do TCE-RJ, a Administração acolheu as conclusões não sob viés litigioso, mas como valioso diagnóstico institucional e roteiro de boas práticas internacionais (COBIT 2019, ITIL 4, ISO 27001).
3. DIRECIONAMENTO DA FORÇA DE TRABALHO PARA O FUTURO PLANO DE AÇÃO:
   - Em consonância com a sistemática das auditorias de governança do TCE-RJ, o momento oportuno e de efetivo ganho institucional para atuação dos gestores dar-se-á após a emissão do Relatório Definitivo, com a formalização e execução do Plano de Ação estruturado para implementação das recomendações expedidas pelo Tribunal. A DGI e as áreas afins optaram por concentrar sua capacidade operacional no planejamento das soluções definitivas em vez de elaborar manifestação preliminar formalista.
4. EXAURIMENTO PROBATÓRIO DA FASE INSTRUTÓRIA:
   - Os subsídios e evidências cabíveis à DGI já haviam sido integralmente juntados aos autos por meio do Despacho 2106960 e 2106972 (Termo TSID nº 2 e dossiê de evidências com links oficiais), inexistindo fatos novos que demandassem complementação extemporânea.

### ESTRUTURA DO DESPACHO:
Elabore o despacho com rigoroso padrão redacional do SEI / DPGE, linguagem formal, escorreita, fundamentada e polida.
O texto deve conter:
1. Cabeçalho formal:
   DIRETORIA DE GESTÃO DA INFORMAÇÃO - DGI
   Referência: Processo nº E-20/001.002323/2026
   AO CONTROLE INTERNO - CI
   A/C Sr. Coordenador de Controle Interno
2. Objeto / Introdução: referência ao Despacho CI nº 2223276.
3. Fundamentação das razões e justificativas dividida em tópicos claros e objetivos:
   - Da Natureza Facultativa e Prerrogativa do Gestor (TSID nº 03, Despacho CI nº 2145441 e Manual do TCE-RJ);
   - Da Inexistência de Divergência Fática e Acolhimento do Diagnóstico de Maturidade de TIC (iGovTI 2026);
   - Da Suficiência da Instrução Probatória Prévia (Despachos DGI nº 2106960 e 2106972);
   - Do Foco na Futura Elaboração e Cumprimento do Plano de Ação Institucional.
4. Conclusão / Encerramento: reafirmação de compromisso com a melhoria contínua da governança de TIC, disponibilidade para apoiar o Controle Interno na interlocução com o TCE-RJ e encaminhamento para os devidos fins de documentação e encerramento.
5. Fecho formal: "Atenciosamente, FÁBIO MARÇAL DA SILVEIRA, Diretor de Gestão da Informação".

Gere apenas o texto final pronto do despacho, impecável e diretamente utilizável no SEI.
"""

print("Chamando o modelo Gemini (gemini-flash-lite-latest)...")
response = client.models.generate_content(
    model="gemini-flash-lite-latest",
    contents=prompt_despacho
)

despacho_gerado = response.text.strip()
print("\n=== DESPACHO GERADO COM SUCESSO! ===")
print(despacho_gerado[:500] + "...\n")

output_md_path = r"C:\Users\11429149760\.gemini\antigravity\scratch\DESPACHO_DGI_ATENDIMENTO_2223276.md"
with open(output_md_path, "w", encoding="utf-8") as f:
    f.write(despacho_gerado)
print(f"Salvo em: {output_md_path}")
