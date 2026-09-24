# -*- coding: utf-8 -*-
import os
import subprocess
import markdown

comp_md = """# RELATÓRIO COMPARATIVO TÉCNICO-JURÍDICO
## CONFRONTO ANALÍTICO ENTRE O DESPACHO PRELIMINAR DGI E A NOTA TÉCNICA DE AUDITORIA

---

<div class="meta-box">
  <div class="meta-row"><strong>PROCESSO ADMINISTRATIVO:</strong> E-20/001.006873/2022 | <strong>CONTRATO Nº:</strong> 20/2023 (Stefanini)</div>
  <div class="meta-row"><strong>DOCUMENTO A (BASE PRELIMINAR):</strong> <code>SEI_2220201_Despacho.pdf</code> / <code>SEI_2220201_Despacho.md</code> (Minuta de Despacho DGI, 6 páginas, 22/09/2026)</div>
  <div class="meta-row"><strong>DOCUMENTO B (AUDITORIA DEFINITIVA):</strong> <code>RELATORIO_TECNICO_AUDITORIA_CHAMADOS_EVENTOS.md</code> (Nota Técnica Conclusiva STIC/DGI/COATE, 22/09/2026)</div>
  <div class="meta-row"><strong>BASE DE DADOS CONSOLIDADA:</strong> <code>chamados glpi consolidados.xlsx</code> (2.980 registros brutos / 2.951 eventos saneados)</div>
  <div class="meta-row"><strong>OBJETIVO:</strong> Confrontar as premissas fáticas, quantitativas, metodológicas e jurídico-financeiras de ambos os documentos para subsidiar a Assessoria Jurídica (ASSJUR) e a Administração Superior.</div>
</div>

---

### 1. QUADRO COMPARATIVO SINTÉTICO DAS DIMENSÕES ANALÍTICAS

| Dimensão de Análise | Documento A: Despacho DGI (SEI 2220201) | Documento B: Nota Técnica de Auditoria (STIC/DGI/COATE) | Diagnóstico Crítico e Impacto Processual |
| :--- | :--- | :--- | :--- |
| **Autoria e Estágio Processual** | Minuta setorial interna da DGI (`[INSIRA SEU NOME]`), sem consolidação com as demais áreas. | Parecer técnico terminativo conjunto de toda a cadeia de governança (COATE, DGI e STIC). | O Documento B supre a ausência de manifestação fiscalizadora apontada no Item 4 do Parecer 199. |
| **Volume de Dados Analisado** | Cita a base preliminar de 2.043 chamados no texto, mas apresenta tabelas com 2.951 registros. | Audita a base integral de 2.980 registros brutos da planilha consolidada do GLPI. | O Documento B saneia a incoerência numérica do Despacho preliminar, conferindo rastreabilidade perante os órgãos de controle. |
| **Saneamento da Base (Expurgos)** | Não menciona a existência de registros espúrios; assume diretamente 2.951 registros. | Identifica e expurga **29 chamados espúrios** (20 de Banco de Dados Oracle e 9 de Segurança da Informação). | Comprova tecnicamente que a busca inicial no GLPI capturou falsos positivos pela palavra "evento" (Capacity Planning e eventos adversos). |
| **Classificação de Serviços (Alínea B)** | • Justiça Itinerante: 2.384 (80,8%)<br>• Eventos: 386 (13,1%)<br>• Reuniões: 138 (4,7%)<br>• Transmissões: 35 (1,2%)<br>• Empréstimos: 8 (0,3%) | • Justiça Itinerante / Ação Social: 2.207 (74,79%)<br>• Eventos Presenciais: 596 (20,20%)<br>• Transmissões Online: 87 (2,95%)<br>• Reuniões Virtuais: 32 (1,08%)<br>• Reuniões Sede: 29 (0,98%) | O Documento B aplica regras contratuais mais precisas, segregando **148 chamados de catálogo ordinário** (Zoom/Teams/Presencial Sede) da conta do reequilíbrio. |
| **Total de Atuações de Campo** | 2.770 chamados (JI + Eventos). | **2.803 chamados excepcionais de campo** (94,99% da base saneada de eventos). | Ambos convergem em demonstrar que mais de 94% da volumetria decorre de efetiva mobilização de campo. |
| **Deduplicação Física (Alínea C)** | Apurou 2.162 eventos únicos restritos apenas à Justiça Itinerante. | Apurou **2.659 eventos físicos únicos de campo** para todo o conjunto de eventos. | O Documento B estabelece a razão de **1,11 chamado/evento**, provando de forma cabal a inexistência de fracionamento artificial. |
| **Análise Horária de Solução (Alínea A)** | Cita genericamente 118 chamados solucionados fora da janela das 08h às 20h. | Apura detalhadamente: **271 chamados solucionados em finais de semana (12,63%)** e 77 fora da janela diurna (3,59%). | O Documento B comprova a sobrecarga em mutirões de sábado para além da jornada comercial. |
| **Período e Base Temporal** | Considera 812 dias (2,16 anos), de 02/07/2024 a 22/09/2026. | Considera **993 dias corridos (2,72 anos)**, de 02/01/2024 a 21/09/2026. | O Documento B abrange a integralidade cronológica da base consolidada, evitando distorções atuaríais. |
| **Fator de Extrapolação (TR 6.16 - 130/ano)** | • Em tickets: **9,9x** (1.282/ano)<br>• Em eventos únicos JI: **7,7x** (1.001/ano) | • Em chamados de campo: **7,93x (+693,1%)** (1.031/ano)<br>• Em eventos físicos únicos: **7,52x (+652,3%)** (978/ano)<br>• Apenas JI: **6,24x (+524,2%)** (811/ano) | O Documento B oferece matriz tripartite de extrapolação, demonstrando que sob qualquer régua o excesso supera 6 a 8 vezes a estimativa. |
| **Engenharia de Custos e Reajuste Linear** | Sugere apenas genericamente restringir a recomposição ao Suporte ao Usuário. | **Veda formalmente o reajuste linear de 13,1487%** sobre os 9 itens, fundamenta a restrição ao Item 08 e remete haveres passados a TAC. | O Documento B blinda o erário contra apontamentos do TCE-RJ e atende com precisão às exigências da ASSJUR. |
| **Encaminhamentos Processuais** | Não especifica prazos nem providências contratuais concretas. | Fixa 4 encaminhamentos formais: aditivo-ponte (30-60 dias), notificação da Stefanini, TAC e revisão do TR da nova licitação. | O Documento B fornece o roteiro completo de gestão de crise e contratação emergencial. |

---

### 2. ANÁLISE DETALHADA DAS DIVERGÊNCIAS E EVOLUÇÃO METODOLÓGICA

#### 2.1. O "Salto" Numérico da Base de Dados e a Descoberta dos Registros Espúrios
Um dos pontos mais vulneráveis do Despacho DGI preliminar (SEI 2220201) residia na contradição entre o seu *Resumo Executivo* — que afirmava fundamentar-se nos 2.043 registros da planilha `Chamados_Eventos` — e as tabelas subsequentes, que totalizavam 2.951 chamados, sem que o leitor compreendesse como surgiram os cerca de 900 chamados excedentes.

A Nota Técnica de Auditoria (Documento B) resolveu essa fragilidade instrutória por meio de auditoria determinística:
1. Demonstrou que a planilha oficial consolidada do GLPI (`chamados glpi consolidados.xlsx`) continha **2.980 registros operacionais**;
2. Descobriu a razão técnica da distorção: o filtro de extração do GLPI capturou a palavra "evento" em relatórios rotineiros de outras áreas:
   * **20 chamados de Banco de Dados Oracle** (*"Capacity Planning... Principais eventos de espera..."*, como o ID 2024037927);
   * **9 chamados de Segurança da Informação** (*"Análise de percentual de eventos adversos"*).
3. Ao expurgar formalmente esses 29 chamados estranhos ao suporte ($2.980 - 29 = 2.951$), o Documento B validou com exatidão matemática o universo de 2.951 chamados de eventos de suporte, conferindo transparência e integridade perante os órgãos de controle externo.

---

#### 2.2. Rigor na Classificação de Serviços e Segregação do Catálogo Ordinário (Alínea B)
O Despacho 2220201 adotou uma classificação manual simplificada, agrupando 2.384 chamados sob a rubrica genérica de "Justiça Itinerante / Ação Social".

A Nota Técnica de Auditoria (Documento B) refinou essa categorização com base em processamento algorítmico do texto e acompanhamentos das ordens de serviço:
* **Justiça Itinerante e Ações Sociais Comunitárias:** 2.207 chamados (74,79%);
* **Suporte Presencial a Grandes Eventos e Solenidades Externas:** 596 chamados (20,20%) — incluindo operações de grande vulto como Rock in Rio, Spanta, solenidades de posse e audiências públicas;
* **Demandas Ordinárias de Catálogo Isoladas:** 148 chamados (5,01%), subdivididos em transmissões online/lives (87 chamados), reuniões remotas via Zoom/Teams (32 chamados) e reuniões na Sede (29 chamados).

> **Aporte Crítico do Documento B:** Ao expurgar expressamente os 148 chamados de catálogo da contagem do reequilíbrio econômico-financeiro (atribuindo-os à franquia regular do Anexo B de 25 chamados/mês), a área técnica atendeu com precisão cirúrgica à objeção formulada pela Assessoria Jurídica na Alínea "b" do Parecer 199.

---

#### 2.3. A Deduplicação Física e a Refutação do Fracionamento Indevido (Alínea C)
A Assessoria Jurídica havia levantado a hipótese de que a contratada estivesse faturando múltiplos chamados para uma única operação em razão de e-mails da COGPI que desmembrassem cronogramas por bairro ou município.

* **No Despacho 2220201:** A área técnica havia realizado a deduplicação restrita à Justiça Itinerante, encontrando 2.162 eventos físicos únicos.
* **Na Nota Técnica de Auditoria (Documento B):** O algoritmo de deduplicação foi expandido para a totalidade dos eventos de campo, cruzando `(Data de Execução + Localidade Normalizada)`. Foram identificados **2.659 eventos físicos únicos**.

A razão resultante de **1,11 chamado por evento físico** constitui prova pericial irrefutável de que **não houve desmembramento indevido de tickets**. Em mais de 90% das vezes, cada ticket correspondeu a uma localidade geográfica autônoma e um deslocamento independente de equipe. As ocorrências de múltiplos chamados no mesmo dia decorreram de atendimento simultâneo a polos geograficamente distantes (ex.: Belford Roxo e Angra dos Reis na mesma data) ou de etapas prévias indispensáveis de vistoria técnica em D-1 (ex.: comunidade da Rocinha).

---

#### 2.4. Comparativo Temporal e Confrontação com o Subitem 6.16 do TR
Ambos os documentos chegam à mesma conclusão de mérito: a estimativa contratual de **130 atuações excepcionais anuais** prevista no Subitem 6.16 do TR foi amplamente superada.

Contudo, o Documento B aprimora os cálculos atuaríais ao utilizar o intervalo temporal completo e real da base consolidada:
* **Período Auditado no Documento B:** 02/01/2024 a 21/09/2026 = **993 dias corridos (2,72 anos / 32,6 meses)**, em contraposição aos 812 dias (2,16 anos) adotados no Despacho preliminar.
* **Cota Prevista no TR para 2,72 anos:** $130 \times 2,72 = \mathbf{353,6\text{ atuações}}$.
* **Extrapolação em Chamados de Campo:** $2.803\text{ chamados} \rightarrow 1.031,0/\text{ano} \rightarrow \mathbf{7,93\text{ vezes}}\text{ (+693,1%)}$.
* **Extrapolação em Eventos Físicos Únicos:** $2.659\text{ eventos} \rightarrow 978,0/\text{ano} \rightarrow \mathbf{7,52\text{ vezes}}\text{ (+652,3%)}$.
* **Extrapolação Estrita em Ações Sociais:** $2.207\text{ chamados} \rightarrow 811,4/\text{ano} \rightarrow \mathbf{6,24\text{ vezes}}\text{ (+524,2%)}$.

Essa demonstração estratificada impede que a empresa ou os órgãos de controle contestem a métrica utilizada, pois mesmo sob o critério mais rigoroso e conservador possível, o excesso fático é superior a 600%.

---

#### 2.5. Blindagem Jurídico-Financeira e Engenharia de Custos
O Despacho 2220201 continha apenas uma breve menção no sentido de "restringir eventual recomposição financeira à frente de Suporte ao Usuário de TIC".

A Nota Técnica de Auditoria (Documento B) enfrentou de forma exaustiva a engenharia de custos e os ditames da Lei nº 8.666/1993 e do TCU:
1. **Ilegalidade do Reajuste Linear de 13,1487%:** Apontou a nulidade da Proposta SEI nº 2211789, que pretendia onerar linearmente os 9 itens do contrato (incluindo Datacenter, Banco de Dados, Links e Segurança), os quais não sofreram nenhum impacto com o aumento dos eventos de campo;
2. **Adstrição Exclusiva ao Item 08:** Determinou que o reequilíbrio deve recair unicamente sobre o módulo de Suporte ao Usuário de TIC;
3. **Segregação de Efeitos Financeiros Pretéritos:** Consignou que o termo aditivo deve gerar efeitos apenas para o futuro. As parcelas retroativas (janeiro de 2024 a setembro de 2026) deverão ser pleiteadas em processo autônomo de Termo de Ajuste de Contas (TAC), com comprovação de custos reais;
4. **Contrato-Ponte Emergencial:** Recomendou a assinatura imediata de aditivo de curto prazo (30 a 60 dias) com valor mensal vigente mantido em R$ 513.793,12 para evitar o colapso dos sistemas Verde e SEI a dois dias do término do ajuste.

---

### 3. RECOMENDAÇÃO CONCLUSIVA DA ÁREA TÉCNICA

Recomenda-se à Administração Superior da Defensoria Pública:
1. **Adotar a Nota Técnica de Auditoria (`RELATORIO_TECNICO_AUDITORIA_CHAMADOS_EVENTOS.md`) como a manifestação oficial e definitiva da área técnica (STIC/DGI/COATE)**, desconsiderando a minuta preliminar do Despacho 2220201 em razão de suas incoerências de amostragem;
2. **Juntar a Nota Técnica Conclusiva aos autos do Processo Administrativo nº E-20/001.006873/2022**, encaminhando-a à Assessoria Jurídica (ASSJUR) para emissão do parecer conclusivo de mérito;
3. **Formalizar imediatamente o Termo Aditivo emergencial de curto prazo (30 a 60 dias)** em valor mensal inalterado, garantindo a sustentação contínua dos serviços de TIC da DPRJ;
4. **Intimar a empresa Stefanini** para apresentar proposta financeira repactuada, circunscrita exclusivamente aos custos incrementais do Item 08.
"""

# Write markdown report
comp_md_path = r'C:\Users\11429149760\Downloads\RELATORIO_COMPARATIVO_DESPACHO_VS_AUDITORIA.md'
with open(comp_md_path, 'w', encoding='utf-8') as f:
    f.write(comp_md)
print('Salvo Markdown comparativo em:', comp_md_path)

# Convert to HTML with institutional styling
html_body = markdown.markdown(comp_md, extensions=['tables', 'fenced_code'])

full_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Relatório Comparativo Técnico-Jurídico - Despacho DGI vs Auditoria STIC</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 20mm 15mm 20mm 15mm;
    @bottom-right {{
      content: counter(page);
    }}
  }}

  body {{
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
    font-size: 9.5pt;
    line-height: 1.5;
    color: #1a202c;
    margin: 0;
    padding: 0;
  }}

  .inst-header {{
    border-bottom: 3px solid #00563B;
    padding-bottom: 8px;
    margin-bottom: 16px;
  }}
  .inst-header .inst-title {{
    font-size: 13pt;
    font-weight: 800;
    color: #00563B;
    margin: 0 0 3px 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  .inst-header .inst-sub {{
    font-size: 10.5pt;
    font-weight: 600;
    color: #2d3748;
    margin: 0 0 2px 0;
  }}
  .inst-header .inst-dept {{
    font-size: 9pt;
    font-weight: 500;
    color: #4a5568;
    margin: 0;
  }}

  h1 {{
    font-size: 12.5pt;
    font-weight: 800;
    color: #1A365D;
    text-align: center;
    margin: 10px 0 14px 0;
  }}
  h2 {{
    font-size: 11pt;
    font-weight: 700;
    color: #00563B;
    border-bottom: 1.5px solid #CBD5E0;
    padding-bottom: 3px;
    margin-top: 18px;
    margin-bottom: 8px;
    page-break-after: avoid;
  }}
  h3 {{
    font-size: 10.2pt;
    font-weight: 700;
    color: #1A365D;
    margin-top: 14px;
    margin-bottom: 6px;
    page-break-after: avoid;
  }}
  h4 {{
    font-size: 9.6pt;
    font-weight: 600;
    color: #2D3748;
    margin-top: 10px;
    margin-bottom: 4px;
    page-break-after: avoid;
  }}

  p {{
    margin: 0 0 7px 0;
    text-align: justify;
  }}

  hr {{
    border: none;
    border-top: 1px solid #E2E8F0;
    margin: 12px 0;
  }}

  .meta-box {{
    background-color: #F8FAFC;
    border: 1px solid #CBD5E0;
    border-left: 4px solid #00563B;
    padding: 10px 14px;
    margin: 10px 0 16px 0;
    font-size: 8.6pt;
  }}
  .meta-row {{
    margin-bottom: 4px;
    line-height: 1.4;
  }}
  .meta-row:last-child {{
    margin-bottom: 0;
  }}

  blockquote {{
    background-color: #F0FDF4;
    border-left: 4px solid #16A34A;
    margin: 8px 0;
    padding: 8px 12px;
    font-style: italic;
    color: #1F2937;
    font-size: 9pt;
  }}

  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0 14px 0;
    font-size: 8.2pt;
    page-break-inside: auto;
  }}
  tr {{ page-break-inside: avoid; }}
  th, td {{
    border: 1px solid #CBD5E0;
    padding: 5px 7px;
    vertical-align: middle;
  }}
  th {{
    background-color: #00563B;
    color: #FFFFFF;
    font-weight: 600;
    text-align: center;
  }}
  tbody tr:nth-child(even) {{
    background-color: #F8FAFC;
  }}

  ul, ol {{
    margin: 4px 0 10px 18px;
    padding: 0;
  }}
  li {{
    margin-bottom: 4px;
    text-align: justify;
  }}
</style>
</head>
<body>

<div class="inst-header">
  <div class="inst-title">Defensoria Pública do Estado do Rio de Janeiro</div>
  <div class="inst-sub">Subdefensoria Pública-Geral de Gestão</div>
  <div class="inst-dept">Secretaria de Tecnologia da Informação e Comunicação (STIC) | Assessoria Especial de Governança de TIC</div>
</div>

{html_body}

</body>
</html>
"""

comp_html_path = r'C:\Users\11429149760\Downloads\RELATORIO_COMPARATIVO_DESPACHO_VS_AUDITORIA.html'
with open(comp_html_path, 'w', encoding='utf-8') as f:
    f.write(full_html)

# Render PDF using Chrome headless
comp_pdf_path = r'C:\Users\11429149760\Downloads\RELATORIO_COMPARATIVO_DESPACHO_VS_AUDITORIA.pdf'
chrome_exe = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

cmd = [
    chrome_exe,
    '--headless=new',
    '--disable-gpu',
    '--no-pdf-header-footer',
    f'--print-to-pdf={comp_pdf_path}',
    comp_html_path
]

res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode == 0 and os.path.exists(comp_pdf_path):
    size_kb = os.path.getsize(comp_pdf_path) / 1024
    print(f"Sucesso! PDF comparativo gerado em: {comp_pdf_path} ({size_kb:.1f} KB)")
else:
    print("Erro ao gerar PDF comparativo:", res.stderr)
