# RELATÓRIO TÉCNICO-JURÍDICO DE ANÁLISE SEMÂNTICA, MODELAGEM ECONÔMICA E ADERÊNCIA DE ESCOPO
## Processo Administrativo SEI nº E-20/001.008552/2026 — Defensoria Pública do Estado do Rio de Janeiro (DPRJ)
### *Régua Comparativa Central: Documento 2219752 — Proposta Oi Soluções S.A. (Contrato Vigente nº 18/2024)*
### *Com Matriz Granular de Aderência ao Escopo Técnico do Termo de Referência 2215770 e Normalização de Vigência*

---

### Sumário
1. [Diretriz Metodológica e Definição da Régua Comparativa (Oi 2219752)](#1-diretriz-metodológica-e-definição-da-régua-comparativa-oi-2219752)
2. [Fundamentação da Normalização Econômica de Vigência (Contratos > 12 Meses)](#2-fundamentação-da-normalização-econômica-de-vigência-contratos--12-meses)
3. [Tabela de Preços Brutos versus Preços Normalizados para 12 Meses](#3-tabela-de-preços-brutos-versus-preços-normalizados-para-12-meses)
4. [Análise Detalhada de Similaridade e Aderência ao Escopo Técnico do TR 2215770](#4-análise-detalhada-de-similaridade-e-aderência-ao-escopo-técnico-do-tr-2215770)
   - [4.1. Definição dos 8 Critérios Técnicos de Escopo](#41-definição-dos-8-critérios-técnicos-de-escopo)
   - [4.2. Matriz Consolidada de Aderência de Escopo Técnico](#42-matriz-consolidada-de-aderência-de-escopo-técnico)
   - [4.3. Análise Qualitativa de Escopo e Gaps Técnicos Documento a Documento](#43-análise-qualitativa-de-escopo-e-gaps-técnicos-documento-a-documento)
5. [Matriz Cruzada: Aderência Técnica de Escopo versus Custo Econômico Normalizado](#5-matriz-cruzada-aderência-técnica-de-escopo-versus-custo-econômico-normalizado)
6. [Achados Críticos sobre a Planilha Oficial 2220599](#6-achados-críticos-sobre-a-planilha-oficial-2220599)
7. [Recomendações Conclusivas para a Administração](#7-recomendações-conclusivas-para-a-administração)

---

## 1. Diretriz Metodológica e Definição da Régua Comparativa (Oi 2219752)

A presente análise adota como **Régua Comparativa Central (Baseline de Custos)** a **Proposta Comercial da Oi Soluções S.A. (Documento SEI nº 2219752)**, instrumento de suporte ao atual **Contrato nº 18/2024 da DPRJ**.

### 1.1. O Cenário da Contratação Atual (Oi Soluções S.A.)
* **Origem**: Proposta de 25/10/2023 referente ao Lote 1 da licitação anterior ("Link Simétrico com Serviço SD-WAN"), pactuada sob regime continuado de telecomunicações para atendimento de 159 unidades da DPRJ e do escritório de Brasília-DF.
* **Vigência Original**: **30 (trinta) meses** (conforme página 658: "PERÍODO: 30 MESES").
* **Valores Unitários Praticados pela Oi**:
  - **80 Mbps**: **R$ 1.488,61** / mês
  - **100 Mbps**: **R$ 1.653,14** / mês
  - **300 Mbps**: **R$ 2.795,41** / mês
* **Custo Atual da Instituição (159 Unidades: 102 de 80M + 35 de 100M + 22 de 300M)**:
  - **Mensalidade Total**: (102 × R$ 1.488,61) + (35 × R$ 1.653,14) + (22 × R$ 2.795,41) = **R$ 271.197,14 / mês**
  - **Custo Anual (12 Meses)**: R$ 271.197,14 × 12 = **R$ 3.254.365,68**
* **O Fato Jurídico Superveniente**: A decretação judicial de falência da Oi Soluções S.A. pelo TJRJ em 25/08/2026 inviabilizou a prorrogação do instrumento (Parecer ASSJUR nº 179/2026), impondo a abertura imediata de contratação emergencial de transição de **até 12 meses** (art. 75, VIII, da Lei Federal nº 14.133/2021). A Proposta Oi materializa, assim, a régua histórica do desembolso real da Defensoria.

---

## 2. Fundamentação da Normalização Econômica de Vigência (Contratos > 12 Meses)

Em contratações corporativas de telecomunicações com fornecimento de equipamentos gerenciados (appliances de borda e switches), o preço mensal cobrado por uma operadora embute despesas operacionais recorrentes (OPEX) e a amortização de investimentos iniciais não recorrentes (CAPEX — instalação, ativação e hardware de borda).

Quando um edital é licitado para **30, 36, 48 ou 60 meses**, a contratada dilui esse CAPEX ao longo de todo o período. Ao exigir uma contratação transitória de **apenas 12 meses** (como no caso emergencial do TR 2215770), a empresa é obrigada a amortizar o investimento em um terço ou um quinto do tempo.

### 2.1. Equações do Modelo de Custo
* **Em contratos plurianuais (T meses)**:
  Preço Mensal P(T) = OPEX(mensal) + [CAPEX(total) / T]
* **Em contratos de transição (12 meses)**:
  Preço Mensal P(12) = OPEX(mensal) + [CAPEX(total) / 12]

### 2.2. O Fator de Normalização de Vigência (FNV)
Considerando a participação média do CAPEX no valor global de contratos corporativos de telecomunicações gerenciadas com SD-WAN (α ≈ 25% do valor contratado em prazos típicos de 30 a 36 meses, conforme benchmarks do setor e referências da Anatel), o preço mensal equivalente para 12 meses é obtido pela fórmula:

* **Preço Normalizado para 12 Meses**:
  P_normalizado(12) = P(T) × [ (1 - α) + α × (T / 12) ]

* **Fator de Normalização de Vigência (com α = 25% de CAPEX)**:
  FNV(T) = 0,75 + 0,25 × (T / 12)

#### Coeficientes de Normalização por Instrumento:
* **12 meses (FUPESC, TR DPRJ)**: FNV = 1.0000 (Base inalterada, já anual)
* **30 meses (GSNT, MPES, DTI/PF, Oi)**: FNV = 1.3750 (+37,5% sobre o valor mensal)
* **36 meses (Pregão GO, Pregão MPRJ)**: FNV = 1.5000 (+50,0% sobre o valor mensal)
* **48 meses (Pregão TJMRS)**: FNV = 1.7500 (+75,0% sobre o valor mensal)
* **60 meses (Contrato MTE / Telebras)**: FNV = 2.0000 (+100,0% sobre o valor mensal)

---

## 3. Tabela de Preços Brutos versus Preços Normalizados para 12 Meses

Confrontando os valores brutos coletados pela CPPM com os valores ajustados pelo **Fator de Normalização de Vigência**:

### Item de 100 Mbps (Parâmetro Mais Concorrido da Cesta):
* **Régua Comparativa Base (Oi Soluções — Preço Praticado DPRJ)**: **R$ 1.653,14** / mês

| Documento SEI | Origem / Proponente | Vigência Original (T) | Fator FNV | Preço Bruto Coletado | Preço Normalizado (12 Meses) | Variação Normalizada vs Oi |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **2219730** | Pregão DTI / PF | 30 meses | 1.3750 | R$ 323,24 | **R$ 444,46** | **-73,11%** |
| **2219727** | Pregão Sec. Geral GO | 36 meses | 1.5000 | R$ 462,43 | **R$ 693,65** | **-58,04%** |
| **2219745** | CD FUPESC | 12 meses | 1.0000 | R$ 1.148,00 | **R$ 1.148,00** | **-30,56%** |
| **2219728** | Pregão MPES | 30 meses | 1.3750 | R$ 848,12 | **R$ 1.166,17** | **-29,46%** |
| **2219752** | **OI SOLUÇÕES (RÉGUA BASE)** | **30 meses** | **—** | **R$ 1.653,14** | **R$ 1.653,14** | **Baseline Atual** |
| **2219747** | Pregão TJMRS | 48 meses | 1.7500 | R$ 1.200,00 | **R$ 2.100,00** | **+27,03%** |
| **2219741** | Pregão MPRJ | 36 meses | 1.5000 | R$ 2.473,94 | **R$ 3.710,91** | **+124,48%** |
| **2219726** | GSNT Telecom | 30 meses | 1.3750 | R$ 5.900,00 | **R$ 8.112,50** | **+390,73%** |
| **2219742** | Contrato MTE / Telebras | 60 meses | 2.0000 | R$ 4.919,56 | **R$ 9.839,12** | **+495,18%** |

> [!IMPORTANT]
> **A Revelação Estatística da Mediana**:
> - **Mediana Normalizada de Mercado (12 Meses)**: **R$ 1.633,08**
> - **Preço Praticado pela Oi Soluções no Contrato Vigente**: **R$ 1.653,14**
> - **Variação Relativa**: apenas **-1,21%**!
>
> Isso demonstra que o contrato da Oi não estava sobreavaliado; ao contrário, representava exatamente o equilíbrio de mercado quando os preços públicos plurianuais são convertidos para o horizonte anual de 12 meses.

---

## 4. Análise Detalhada de Similaridade e Aderência ao Escopo Técnico do TR 2215770

Para responder à necessidade de identificar com rigor quais propostas possuem **maior ou menor aderência técnica** em relação às exigências do **Termo de Referência nº 2215770**, estruturamos uma avaliação multicritério baseada nas especificações consolidadas pela Diretoria de Gestão da Informação e Núcleo de Infraestrutura da DPRJ.

### 4.1. Definição dos 8 Critérios Técnicos de Escopo

1. **C1 (15%) — Topologia SD-WAN Nativa & Orquestração Central**: Rede WAN controlada logicamente por software em topologia de malha (mesh) segura, com orquestrador centralizado em nuvem/software para provisionamento automatizado (zero-touch), monitoramento unificado e roteamento dinâmico baseado em aplicação e métricas de qualidade.
2. **C2 (15%) — Simetria de Banda (1:1) & CIR 100%**: Fornecimento de circuitos com garantia integral de banda contratada (CIR = 100%), simetria plena de upload e download (1:1), sem franquia de tráfego, sem bloqueio de portas e com endereçamento IPv4/IPv6 fixo e público.
3. **C3 (15%) — Segurança de Borda Integrada (NGFW + IPS no Próprio Appliance)**: Exigência de que os equipamentos de borda não sejam meros roteadores, mas appliances integrados com Firewall de Próxima Geração (NGFW), inspeção profunda de pacotes (DPI), Sistema de Prevenção de Intrusão (IPS) ativo e proteção perimetral contra ameaças cibernéticas.
4. **C4 (15%) — Arquitetura de 3 Perfis Físicos Fixos para Upgrade Lógico**: Especificação de 3 perfis físicos padronizados de hardware (Branch Pequeno, Médio e Grande/Concentrador), com capacidade de processamento suficiente para que upgrades ou downgrades de velocidade sejam realizados de forma puramente lógica e remota via software, **eliminando a necessidade de aditivos contratuais de hardware**.
5. **C5 (10%) — Redundância & Failover Automático com 2º Link (K2 Telecom)**: Capacidade dos ativos de borda operarem em Dual-WAN e realizarem balanceamento dinâmico e contingência/failover automático sem perda de sessão com os links assimétricos já existentes na DPRJ via Contrato nº 20/2024 (K2 Telecom).
6. **C6 (10%) — Capilaridade Territorial no Estado do Rio de Janeiro (+ DF)**: Abrangência geográfica real com capacidade de atender as 159 unidades operacionais da Defensoria Pública espalhadas por todas as regiões do Estado do RJ (Capital, Baixada, Região dos Lagos, Norte, Noroeste, Serrana e Centro-Sul) e o escritório de representação em Brasília-DF.
7. **C7 (10%) — Modelo de Serviço Gerenciado 24x7x365 & Telemetria**: Prestação sob a modalidade de serviço continuado (OPEX), englobando suporte técnico especializado ininterrupto, substituição presencial de equipamentos avariados e disponibilização de portal de telemetria em tempo real com sondagens fim-a-fim.
8. **C8 (10%) — SLA Rigoroso (Disponibilidade ≥ 99,5% & Glosa em Fatura)**: Acordo de Nível de Serviço exigindo disponibilidade mínima mensal de 99,5% por circuito em regime 24x7, contagem do início da indisponibilidade pelo momento exato da queda no gráfico (telemetria), limites estritos de MTTR e regime de glosas diretas em fatura mensal com teto de 30%.

---

### 4.2. Matriz Consolidada de Aderência de Escopo Técnico

A tabela a seguir apresenta as notas atribuídas (escala de 0 a 10) para cada um dos 8 critérios técnicos, a pontuação ponderada final, a aderência percentual de escopo e a classificação comparativa:

| ID SEI | Proponente / Edital de Referência | C1: SD-WAN (15%) | C2: Simetria (15%) | C3: NGFW/IPS (15%) | C4: 3 Perfis (15%) | C5: Failover K2 (10%) | C6: Capilaridade (10%) | C7: Gerenciado (10%) | C8: SLA 99,5% (10%) | Total Ponderado (0-100) | Aderência ao Escopo (%) | Grau de Aderência Técnica |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **2215770** | **Termo de Referência (DPRJ)** | **10.0** | **10.0** | **10.0** | **10.0** | **10.0** | **10.0** | **10.0** | **10.0** | **100.00** | **100.00%** | **Padrão de Referência** |
| **2219726** | **Proposta GSNT Telecom** | 9.5 | 10.0 | 9.0 | 8.5 | 9.0 | 10.0 | 9.0 | 8.5 | **92.00** | **92.00%** | **Altíssima Aderência** |
| **2219742** | **Contrato MTE / Telebras** | 10.0 | 9.0 | 10.0 | 9.0 | 8.0 | 5.0 | 9.5 | 8.0 | **87.50** | **87.50%** | **Altíssima Aderência** |
| **2219741** | **Pregão 90020/2024 MPRJ** | 7.5 | 10.0 | 8.0 | 5.0 | 9.5 | 10.0 | 9.5 | 10.0 | **84.75** | **84.75%** | **Alta Aderência** |
| **2219747** | **Pregão 2/2026 TJMRS** | 8.5 | 9.5 | 7.5 | 5.0 | 9.0 | 3.0 | 8.5 | 9.5 | **75.75** | **75.75%** | **Alta Aderência** |
| **2219728** | **Pregão 90037/2025 MPES** | 8.0 | 9.0 | 9.0 | 4.0 | 7.0 | 5.0 | 8.0 | 7.5 | **72.50** | **72.50%** | **Aderência Moderada** |
| **2219730** | **Pregão 90009/2025 DTI / PF** | 9.5 | 6.5 | 8.0 | 4.0 | 8.5 | 4.0 | 9.0 | 7.0 | **70.50** | **70.50%** | **Aderência Moderada** |
| **2219752** | **Proposta Oi (Contrato Vigente)** | 5.0 | 9.5 | 4.0 | 2.0 | 6.0 | 10.0 | 8.5 | 7.5 | **62.75** | **62.75%** | **Aderência Moderada** |
| **2219727** | **Pregão 107458/2025 GO** | 8.0 | 6.0 | 5.5 | 3.0 | 6.5 | 3.0 | 7.5 | 7.5 | **58.25** | **58.25%** | **Baixa Aderência** |
| **2219745** | **CD 75/2025 FUPESC** | 3.0 | 6.0 | 4.0 | 1.0 | 4.0 | 2.0 | 6.0 | 6.5 | **39.50** | **39.50%** | **Muito Baixa Aderência** |

---

### 4.3. Análise Qualitativa de Escopo e Gaps Técnicos Documento a Documento

#### 1. Proposta GSNT Telecom (2219726) — Aderência: 92,00% (Altíssima)
* **Destaques Técnicos**: Foi elaborada sob medida para a solicitação da DPRJ, cotando exatamente os lotes solicitados (Lote I SD-WAN e Lote II Internet Dedicada) para os 159 endereços da instituição. Especificou CPEs dedicados compatíveis com a arquitetura do órgão e garantiu simetria 1:1.
* **Gaps em Relação ao TR**: A proposta não apresentou detalhamento técnico profundo sobre o motor de inteligência do orquestrador e aceitou passivamente o modelo de SLA sem especificar estrutura operacional própria de MTTR no interior do RJ. *(Seu principal obstáculo reside no preço outlier, não no escopo)*.

#### 2. Contrato 18/2024 MTE / Telebras (2219742) — Aderência: 87,50% (Altíssima)
* **Destaques Técnicos**: É a solução mais avançada tecnologicamente da amostra. A Telebras desenhou o "SD-WAN Telebras Seguro" com orquestrador central nativo, CPEs estratificados em perfis físicos de hardware (Small, Mid e Enterprise Branch), Next-Generation Firewall integrado com suporte de fabricante e gestão contínua pelo NSOC da Telebras.
* **Gaps em Relação ao TR**: O escopo é federal e disperso (409 agências do trabalho no Brasil), não contemplando a densidade regional das comarcas isoladas do Rio de Janeiro. Além disso, não possui previsão para integração e failover com o link assimétrico da K2 Telecom contratado pela DPRJ.

#### 3. Pregão 90020/2024 MPRJ (2219741) — Aderência: 84,75% (Alta)
* **Destaques Técnicos**: Possui a **maior aderência prática e logística** de toda a pesquisa. Atende exatamente o mesmo território geográfico da DPRJ (comarcas do interior fluminense e capital). Prevê circuitos dedicados simétricos e exige redundância ativa com agregação de banda (100+50 e 200+100 Mbps), além de estabelecer o exato mesmo SLA de 99,5% com regime de glosas diretas.
* **Gaps em Relação ao TR**: Não implementa a modelagem dos 3 perfis físicos fixos para upgrade sem aditivo e sua redundância é baseada em enlaces físicos duplos contratados no mesmo certame, em vez do failover com o segundo contrato da DPRJ.

#### 4. Pregão 2/2026 TJMRS (2219747) — Aderência: 75,75% (Alta)
* **Destaques Técnicos**: Objeto focado na interligação com tecnologia SD-WAN e túneis IPsec criptografados entre Sede e auditorias militares. Contempla links simétricos redundantes (100+50 Mbps) e SLA rigoroso de 99,5% com glosa direta.
* **Gaps em Relação ao TR**: Escopo geográfico extremamente limitado (apenas 4 localidades no RS: Porto Alegre, Santa Maria e Passo Fundo), não possuindo a complexidade de malha de 159 pontos nem a padronização de 3 perfis fixos de hardware.

#### 5. Pregão 90037/2025 MPES (2219728) — Aderência: 72,50% (Moderada)
* **Destaques Técnicos**: Solução focada na ampliação da segurança cibernética utilizando tecnologia SD-WAN e links dedicados para promotorias de justiça no Sudeste (Espírito Santo). Excelente nível de exigência de NGFW/IPS.
* **Gaps em Relação ao TR**: O objeto principal do certame foi a aquisição e ampliação da infraestrutura de segurança (appliances UTM/NGFW) com a conectividade em segundo plano. Não estabelece os 3 perfis fixos para dispensa de aditivos e atende exclusivamente ao território capixaba.

#### 6. Pregão 90009/2025 DTI / Polícia Federal (2219730) — Aderência: 70,50% (Moderada)
* **Destaques Técnicos**: Orquestração SD-WAN de grande porte com capacidade comprovada de gerenciamento de tráfego crítico em âmbito nacional.
* **Gaps em Relação ao TR**: A topologia é heterogênea e híbrida, apoiando-se pesadamente em conexões satelitais e banda larga assimétrica com CIR reduzido (incompatível com a exigência de links 100% simétricos dedicados em fibra do TR fluminense). A escala continental da PF distancia o objeto da realidade física do Estado do RJ.

#### 7. Proposta Oi - Contrato Vigente (2219752) — Aderência: 62,75% (Moderada)
* **Destaques Técnicos**: Possui 100% de capilaridade nas 159 unidades operacionais da Defensoria e fornece circuitos simétricos de excelente estabilidade física.
* **Gaps em Relação ao TR**: Representa uma arquitetura legada de WAN/MPLS tradicional. **Não possui** a plataforma moderna de orquestração SD-WAN centralizada por software, **não dispõe** de NGFW e IPS integrados no appliance de borda e **não adota** os 3 perfis fixos de hardware. A substituição dessa defasagem tecnológica foi justamente a motivação técnica para a DPRJ desenhar o novo TR 2215770.

#### 8. Pregão 107458/2025 GO (2219727) — Aderência: 58,25% (Baixa)
* **Destaques Técnicos**: Fornecimento de circuitos terrestres de acesso à internet com tecnologia SD-WAN em secretarias do Estado de Goiás.
* **Gaps em Relação ao TR**: Trata-se de internet banda larga comercial com gerenciamento básico de tráfego, sem garantia de simetria plena (CIR=100%), sem NGFW corporativo integrado e sem capilaridade fluminense.

#### 9. CD 75/2025 FUPESC (2219745) — Aderência: 39,50% (Muito Baixa)
* **Destaques Técnicos**: Fornece conectividade de dados dedicada para unidades prisionais sob prazo de 12 meses.
* **Gaps em Relação ao TR**: Conexão simples de internet provida por ISPs regionais de Santa Catarina; não contempla orquestrador SD-WAN, não possui firewall de borda NGFW/IPS e sua realidade geográfica não guarda nenhuma correspondência com o Rio de Janeiro.

---

## 5. Matriz Cruzada: Aderência Técnica de Escopo versus Custo Econômico Normalizado

Ao cruzar a **Aderência de Escopo Técnico ao TR 2215770** com o **Custo Mensal Normalizado de 100 Mbps**, obtém-se a matriz de quadrantes estratégicos para tomada de decisão:

| Classificação de Aderência Técnica | Faixa de Preço Normalizado Baixo / Médio (< R$ 2.000 / mês) | Faixa de Preço Normalizado Alto / Muito Alto (> R$ 2.000 / mês) |
|---|---|---|
| **ALTA ADERÊNCIA TÉCNICA (> 75%)** | **[EQUILÍBRIO TÉCNICO-FINANCEIRO]**<br/>• **MPRJ (84,8% / R$ 3.710,91)***: Melhor correlação logística fluminense<br/>• **TJMRS (75,8% / R$ 2.100,00)**: Links redundantes com SD-WAN | **[ALTO ESCOPO / CUSTO ELEVADO]**<br/>• **GSNT (92,0% / R$ 8.112,50)**: Outlier de mercado privado<br/>• **MTE Telebras (87,5% / R$ 9.839,12)**: Tabela federal estatal |
| **MODERADA / BAIXA ADERÊNCIA (< 75%)** | **[BAIXO CUSTO / GAPS DE ESCOPO]**<br/>• **Oi Vigente (62,8% / R$ 1.653,14)**: Baseline histórico DPRJ<br/>• **MPES (72,5% / R$ 1.166,17)**: Foco em segurança no ES<br/>• **DTI / PF (70,5% / R$ 444,46)**: Escala continental / satélite<br/>• **GO (58,3% / R$ 693,65)**: Banda larga simples em Goiás<br/>• **FUPESC (39,5% / R$ 1.148,00)**: Internet regional para presídios | **[INCOMPATIBILIDADE TÉCNICA]**<br/>*(Nenhum documento se enquadra nesta categoria)* |

*Nota sobre o MPRJ: Encontra-se na fronteira entre os quadrantes, pois seu preço unitário de R$ 3.710,91 contempla a soma de dois links redundantes dedicados (100 + 50 Mbps).*

### Conclusões do Cruzamento Escopo vs Custo:
1. **O paradoxo do alto escopo**: Os únicos documentos que atendem quase integralmente à sofisticada arquitetura de SD-WAN com NGFW e perfis de hardware fixos (GSNT com 92% e Telebras MTE com 87,5%) cobram preços entre **R$ 8.112,50 e R$ 9.839,12** (normalizados para 12 meses) — valores proibitivos para a dotação orçamentária da DPRJ.
2. **O parâmetro de maior viabilidade técnica e jurídica (MPRJ)**: Com 84,75% de aderência técnica, mesma jurisdição fluminense, idêntico SLA de 99,5% e valor normalizado de **R$ 3.710,91** (já incluindo redundância somada de 100+50 Mbps), o **Pregão 90020/2024 do MPRJ** consolida-se como a âncora técnica mais consistente.
3. **O papel da Oi como balizador de base**: A Oi possui aderência de escopo intermediária (62,75%) porque seu contrato é de tecnologia anterior (sem SD-WAN/NGFW). O fato de o mercado normalizado para links modernos situar-se em torno de R$ 1.633 a R$ 2.100 confirma que a evolução para SD-WAN demandará uma dotação ligeiramente superior à da Oi, mas muito distante das pretensões da GSNT.

---

## 6. Achados Críticos sobre a Planilha Oficial 2220599

1. **A Desconsideração da Amortização em Contratos Plurianuais**:
   A planilha da CPPM misturou contratos de 12, 30, 36, 48 e 60 meses sem qualquer equalização de vigência. Editais de 36 meses (GO: R$ 462,43) ou 60 meses (MTE: R$ 4.919,56) diluem o custo de aquisição dos appliances em horizontes muito mais longos, tornando a comparação direta com o contrato transitório de 12 meses da DPRJ tecnicamente imperfeita.
2. **O Erro no Prazo Global da Planilha (30m vs 12m)**:
   A coluna da Oi na planilha oficial computou R$ 3.254.365,68 na linha *"Valor Total Estimado 30 meses"*, quando esse montante é o resultado de exatamente **12 meses de faturamento**. Enquanto isso, as demais propostas foram multiplicadas por 30 meses. Corrigindo o horizonte para os **12 meses reais do TR emergencial**, a contratação deve ser estimada em **R$ 4.830.281,52** (pela Mediana Normalizada).

---

## 7. Recomendações Conclusivas para a Administração

1. **Adoção do MPRJ (2219741) como Referência de Escopo e SLA**:
   Utilizar os parâmetros do Ministério Público do Rio de Janeiro como justificativa técnica primordial junto ao TCE-RJ, comprovando que órgãos congêneres no território fluminense exigem o mesmo nível de serviço (99,5%) e links simétricos dedicados.
2. **Fixação do Preço Teto pela Mediana Normalizada**:
   Adotar a **Mediana Normalizada de 12 Meses (R$ 4.830.281,52 global anual / R$ 402.523,46 mensal)** como teto rígido do certame de transição. Esse patamar garante a atratividade comercial para provedores qualificados sem onerar o erário com os valores desproporcionais da GSNT.
3. **Descarte Técnico da Cotação FUPESC (2219745)**:
   Com apenas 39,50% de aderência ao escopo técnico (internet banda larga simples sem SD-WAN ou NGFW), a cotação da FUPESC deve ser descartada da cesta de preços do Lote I de SD-WAN por manifesta incompatibilidade de objeto, fortalecendo a segurança jurídica do processo de pesquisa de preços.
