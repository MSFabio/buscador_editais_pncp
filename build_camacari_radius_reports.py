import json
import math
import datetime
import os
import subprocess

CAMACARI_COORDS = (-12.6975, -38.3242)

MUNICIPALITY_COORDS = {
    "Camaçari": (-12.6975, -38.3242),
    "Dias d'Ávila": (-12.6181, -38.2961),
    "Lauro de Freitas": (-12.8944, -38.3272),
    "Simões Filho": (-12.7844, -38.4028),
    "Salvador": (-12.9714, -38.5014),
    "Mata de São João": (-12.5303, -38.3039),
    "Pojuca": (-12.4344, -38.3314),
    "Candeias": (-12.6681, -38.5444),
    "São Francisco do Conde": (-12.6264, -38.6806),
    "São Sebastião do Passé": (-12.5117, -38.4958),
    "Madre de Deus": (-12.7411, -38.6214),
    "Santo Amaro": (-12.5469, -38.7111),
    "São Félix": (-12.6058, -38.9722),
    "Cachoeira": (-12.5997, -38.9639),
    "Cabaceiras do Paraguaçu": (-12.6167, -39.1500),
    "Alagoinhas": (-12.1356, -38.4194),
    "Feira de Santana": (-12.2667, -38.9667),
    "Barrocas": (-11.5300, -39.0800),
    "Santa Terezinha": (-12.7722, -39.5242),
    "Santo Antônio de Jesus": (-12.9694, -39.2611),
    "Cruz das Almas": (-12.6731, -39.1022),
    "Jiquiriçá": (-13.2569, -39.5700),
    "Nova Itarana": (-13.1694, -39.9278),
    "Ibirapitanga": (-13.9572, -39.3800),
    "Ubaitaba": (-14.3122, -39.3242),
    "Itagibá": (-14.2831, -39.8458),
    "Ipiaú": (-14.1378, -39.7028),
    "Itajuípe": (-14.6781, -39.3758),
    "Itabuna": (-14.7858, -39.2800),
    "Ilhéus": (-14.7889, -39.0494),
    "Jequié": (-13.8581, -40.0842),
    "Lafaiete Coutinho": (-13.6558, -40.2100),
    "Ruy Barbosa": (-12.2858, -40.4939),
    "Itaberaba": (-12.5278, -40.3069),
    "Capim Grosso": (-11.3808, -40.0128),
    "Campo Formoso": (-10.5108, -40.3217),
    "Iguaí": (-14.7578, -40.0894),
    "Poções": (-14.5300, -40.3667),
    "Brumado": (-14.2039, -41.6653),
    "Rio do Antônio": (-14.4039, -41.7458),
    "Lagoa Real": (-14.1500, -42.2333),
    "Livramento de Nossa Senhora": (-13.6467, -41.8406),
    "Paramirim": (-13.4428, -42.2389),
    "Rio do Pires": (-13.1258, -42.2789),
    "Boquira": (-12.8228, -41.9700),
    "Ibipeba": (-11.6408, -42.0167),
    "Irecê": (-11.3039, -41.8558),
    "Gentio do Ouro": (-11.4339, -42.5039),
    "Xique-Xique": (-10.8231, -42.7311),
    "Juazeiro": (-9.4117, -40.5033),
    "Ibotirama": (-12.1853, -43.2206),
    "Barreiras": (-12.1528, -44.9961),
    "São Desidério": (-12.3639, -44.9733),
    "Luís Eduardo Magalhães": (-12.0967, -45.7967),
    "Riachão das Neves": (-11.7461, -44.9100),
    "Formosa do Rio Preto": (-11.0483, -45.1931),
    "Correntina": (-13.3433, -44.6367),
    "Cocos": (-14.1839, -44.5339),
    "Teixeira de Freitas": (-17.5367, -39.7422),
    "Vitória da Conquista": (-14.8661, -40.8394),
    "Santana": (-13.6067, -44.0500),
    "Curaçá": (-8.9903, -39.9094)
}

def haversine(coord1, coord2):
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return 6371.0 * c

def fmt_date(dt_str):
    if not dt_str:
        return "Não informada"
    try:
        clean = dt_str.split('.')[0]
        if 'T' in clean:
            dt = datetime.datetime.strptime(clean, "%Y-%m-%dT%H:%M:%S")
            return dt.strftime("%d/%m/%Y às %H:%M")
        else:
            dt = datetime.datetime.strptime(clean, "%Y-%m-%d")
            return dt.strftime("%d/%m/%Y")
    except Exception:
        return dt_str

def fmt_currency(val):
    if val is None or val == 0:
        return "Não informado / Sigiloso"
    try:
        val_f = float(val)
        return f"R$ {val_f:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return str(val)

json_file = r'C:\Users\11429149760\.gemini\antigravity\scratch\aug18_bahia_results.json'
md_file = r'C:\Users\11429149760\.gemini\antigravity\brain\001766fb-0fab-4892-bf1e-723cc736a97c\editais_pncp_camacari_raio.md'
html_file = r'C:\Users\11429149760\.gemini\antigravity\scratch\editais_camacari_raio.html'
pdf_file = r'C:\Users\11429149760\.gemini\antigravity\brain\001766fb-0fab-4892-bf1e-723cc736a97c\editais_pncp_camacari_raio.pdf'

with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

ba_items = data.get('bahia', [])

tier1 = [] # <= 100km
tier2 = [] # 101km - 200km
tier3 = [] # 201km - 300km
tier4 = [] # > 300km

for item in ba_items:
    muni = item.get('municipio') or 'Bahia'
    matched_key = "Camaçari"
    for k in MUNICIPALITY_COORDS:
        if k.lower() in muni.lower() or muni.lower() in k.lower():
            matched_key = k
            break
    dist = round(haversine(CAMACARI_COORDS, MUNICIPALITY_COORDS[matched_key]), 1)
    item['distance_km'] = dist
    item['municipio_ref'] = matched_key

    if dist <= 100.0:
        tier1.append(item)
    elif dist <= 200.0:
        tier2.append(item)
    elif dist <= 300.0:
        tier3.append(item)
    else:
        tier4.append(item)

# Sort each tier by distance ascending, then closing date
def tier_sort_key(x):
    return (x.get('distance_km', 0), x.get('data_encerramento_proposta') or '9999')

tier1.sort(key=tier_sort_key)
tier2.sort(key=tier_sort_key)
tier3.sort(key=tier_sort_key)
tier4.sort(key=tier_sort_key)

tiers_data = [
    ("📍 Faixa 1: Municípios em um raio de até 100 km de Camaçari/BA", tier1, "Até 100 km", "#16a34a"),
    ("🚗 Faixa 2: Municípios em um raio de até 200 km de Camaçari/BA (101 a 200 km)", tier2, "101 a 200 km", "#2563eb"),
    ("🚚 Faixa 3: Municípios em um raio de até 300 km de Camaçari/BA (201 a 300 km)", tier3, "201 a 300 km", "#d97706"),
    ("✈️ Faixa 4: Municípios em um raio acima de 300 km de Camaçari/BA (> 300 km)", tier4, "Acima de 300 km", "#dc2626")
]

# 1. BUILD MARKDOWN REPORT
lines_md = []
lines_md.append("# 📍 Editais PNCP na Bahia Organizados por Raio de Distância de Camaçari/BA")
lines_md.append(f"**Ponto de Referência Central:** Camaçari/BA (Região Metropolitana de Salvador)  ")
lines_md.append(f"**Total de Editais Mapeados na Bahia:** `{len(ba_items)}` editais abertos  ")
lines_md.append(f"**Data de Atualização:** 20/08/2026  \n")

lines_md.append("## 📊 Quadro Resumo por Faixa de Distância\n")
lines_md.append("| Faixa de Distância de Camaçari | Qtd Editais | Pregões Eletrônicos | Principais Municípios |")
lines_md.append("| :--- | :---: | :---: | :--- |")

for title, t_list, label, color in tiers_data:
    p_count = sum(1 for i in t_list if 'pregão' in (i.get('modalidade') or '').lower() or 'pregao' in (i.get('modalidade') or '').lower())
    munis_str = ", ".join(sorted(list(set(i.get('municipio_ref') for i in t_list)))[:6])
    lines_md.append(f"| **{label}** | **`{len(t_list)}`** | `{p_count}` | {munis_str} |")

lines_md.append("\n---\n")

for title, t_list, label, color in tiers_data:
    p_count = sum(1 for i in t_list if 'pregão' in (i.get('modalidade') or '').lower() or 'pregao' in (i.get('modalidade') or '').lower())
    lines_md.append(f"## {title} ({len(t_list)} editais | {p_count} Pregões)\n")
    
    if not t_list:
        lines_md.append("_Nenhum edital localizado nesta faixa._\n\n")
        continue

    for idx, item in enumerate(t_list, 1):
        orgao = item.get('orgao') or 'Não informado'
        muni = item.get('municipio') or 'Bahia'
        dist = item.get('distance_km', 0)
        title_ed = item.get('title') or f"Edital {item.get('control_num')}"
        modalidade = item.get('modalidade') or 'Credenciamento'
        objeto = (item.get('objeto') or 'Sem descrição.').strip()
        val = fmt_currency(item.get('valor_estimado'))
        dt_pub = fmt_date(item.get('data_publicacao'))
        dt_enc = fmt_date(item.get('data_encerramento_proposta'))
        terms_str = ", ".join([f"`{t}`" for t in item.get('matched_terms', [])])
        link_pncp = item.get('link_pncp')
        link_origem = item.get('link_origem')

        is_pregao = 'pregão' in modalidade.lower() or 'pregao' in modalidade.lower()
        badge_mod = f"🔥 **{modalidade}**" if is_pregao else f"`{modalidade}`"

        lines_md.append(f"### {idx}. {title_ed} — {orgao}")
        lines_md.append(f"- **Município / Distância:** **{muni} - BA (~{dist} km de Camaçari)**")
        lines_md.append(f"- **Modalidade:** {badge_mod}")
        lines_md.append(f"- **Termos Relacionados:** {terms_str}")
        lines_md.append(f"- **Valor Estimado:** `{val}`")
        lines_md.append(f"- **Data de Publicação:** {dt_pub}")
        lines_md.append(f"- **Encerramento / Sessão Pública:** **{dt_enc}**")
        lines_md.append(f"- **Objeto:** {objeto}")
        links_arr = []
        if link_pncp:
            links_arr.append(f"[🔗 Ver no PNCP]({link_pncp})")
        if link_origem:
            links_arr.append(f"[🌐 Sistema de Origem]({link_origem})")
        lines_md.append(f"- **Links:** {' | '.join(links_arr)}")
        lines_md.append("\n---\n")

with open(md_file, 'w', encoding='utf-8') as f:
    f.write("\n".join(lines_md))

print(f"Markdown written to {md_file}")

# 2. BUILD HTML FOR PDF
html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>PNCP - Editais da Bahia por Raio de Distância de Camaçari</title>
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    @page {{ size: A4; margin: 10mm; }}
    body {{
        font-family: 'Inter', -apple-system, sans-serif;
        color: #0f172a; background: #ffffff; font-size: 11px; line-height: 1.4; margin: 0; padding: 0;
    }}
    header {{ border-bottom: 2px solid #1e40af; padding-bottom: 8px; margin-bottom: 12px; }}
    h1 {{ color: #1e40af; font-size: 18px; margin: 0 0 4px 0; font-weight: 700; }}
    .meta-bar {{ font-size: 10.5px; color: #475569; margin-bottom: 8px; }}
    .summary-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        margin-bottom: 14px;
    }}
    .stat-card {{
        background: #f8fafc;
        border: 1px solid #cbd5e1;
        border-radius: 6px;
        padding: 8px;
        text-align: center;
    }}
    .stat-val {{ font-size: 18px; font-weight: 700; }}
    .stat-lbl {{ font-size: 10px; font-weight: 600; color: #475569; }}
    .tier-header {{
        font-size: 13px; font-weight: 700; color: #ffffff;
        padding: 6px 10px; border-radius: 4px; margin: 16px 0 10px 0;
    }}
    .card {{
        background: #ffffff; border: 1px solid #cbd5e1; border-radius: 5px;
        padding: 8px 10px; margin-bottom: 8px; page-break-inside: avoid;
    }}
    .card.pregao {{ background: #fef2f2; border-color: #fca5a5; }}
    .card-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px; }}
    .card-title {{ font-weight: 700; font-size: 11.5px; color: #1e3a8a; margin: 0; }}
    .badge {{ display: inline-block; padding: 2px 6px; border-radius: 3px; font-size: 9.5px; font-weight: 600; text-transform: uppercase; }}
    .badge-pregao {{ background: #ef4444; color: #ffffff; }}
    .badge-outros {{ background: #e2e8f0; color: #334155; }}
    .badge-dist {{ background: #0284c7; color: #ffffff; font-size: 9.5px; padding: 2px 6px; border-radius: 3px; font-weight: 600; }}
    .grid-info {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2px 10px; font-size: 10.5px; margin-bottom: 4px; }}
    .info-label {{ font-weight: 600; color: #475569; }}
    .enc-date {{ color: #dc2626; font-weight: 700; }}
    .objeto-text {{ font-size: 10.5px; color: #334155; background: rgba(255, 255, 255, 0.7); border: 1px solid #e2e8f0; padding: 4px 6px; border-radius: 3px; margin-top: 3px; }}
    .links-bar {{ margin-top: 4px; font-size: 10.5px; }}
    .links-bar a {{ color: #2563eb; text-decoration: none; font-weight: 500; margin-right: 10px; }}
</style>
</head>
<body>

<header>
    <h1>📍 PNCP - Editais da Bahia por Raio de Distância de Camaçari/BA</h1>
    <div class="meta-bar">
        <b>Ponto Central:</b> Camaçari - BA &nbsp;|&nbsp;
        <b>Total Editais Mapeados:</b> {len(ba_items)} &nbsp;|&nbsp;
        <b>Fonte:</b> Portal Nacional de Contratações Públicas
    </div>
    <div class="summary-grid">
        <div class="stat-card" style="border-left: 4px solid #16a34a;">
            <div class="stat-val" style="color: #16a34a;">{len(tier1)}</div>
            <div class="stat-lbl">Até 100 km</div>
        </div>
        <div class="stat-card" style="border-left: 4px solid #2563eb;">
            <div class="stat-val" style="color: #2563eb;">{len(tier2)}</div>
            <div class="stat-lbl">101 a 200 km</div>
        </div>
        <div class="stat-card" style="border-left: 4px solid #d97706;">
            <div class="stat-val" style="color: #d97706;">{len(tier3)}</div>
            <div class="stat-lbl">201 a 300 km</div>
        </div>
        <div class="stat-card" style="border-left: 4px solid #dc2626;">
            <div class="stat-val" style="color: #dc2626;">{len(tier4)}</div>
            <div class="stat-lbl">Acima de 300 km</div>
        </div>
    </div>
</header>
"""

for title, t_list, label, color in tiers_data:
    p_count = sum(1 for i in t_list if 'pregão' in (i.get('modalidade') or '').lower() or 'pregao' in (i.get('modalidade') or '').lower())
    html_content += f"""
    <div class="tier-header" style="background-color: {color};">
        {title} ({len(t_list)} editais | {p_count} Pregões)
    </div>
    """
    for idx, item in enumerate(t_list, 1):
        orgao = item.get('orgao') or 'Não informado'
        muni = item.get('municipio') or 'Bahia'
        dist = item.get('distance_km', 0)
        title_ed = item.get('title') or f"Edital {item.get('control_num')}"
        modalidade = item.get('modalidade') or 'Credenciamento'
        objeto = (item.get('objeto') or 'Sem descrição.').strip()
        val = fmt_currency(item.get('valor_estimado'))
        dt_pub = fmt_date(item.get('data_publicacao'))
        dt_enc = fmt_date(item.get('data_encerramento_proposta'))
        terms = ", ".join(item.get('matched_terms', []))
        link_pncp = item.get('link_pncp')
        link_origem = item.get('link_origem')

        is_pregao = 'pregão' in modalidade.lower() or 'pregao' in modalidade.lower()
        badge_class = "badge-pregao" if is_pregao else "badge-outros"
        card_class = "card pregao" if is_pregao else "card"

        html_content += f"""
        <div class="{card_class}">
            <div class="card-header">
                <div class="card-title">{idx}. {title_ed} — {orgao}</div>
                <div>
                    <span class="badge-dist">📍 ~{dist} km</span>
                    <span class="badge {badge_class}">{modalidade}</span>
                </div>
            </div>
            <div class="grid-info">
                <div><span class="info-label">Município:</span> <b>{muni} - BA</b></div>
                <div><span class="info-label">Sessão Pública:</span> <span class="enc-date">{dt_enc}</span></div>
                <div><span class="info-label">Valor Estimado:</span> {val}</div>
                <div><span class="info-label">Publicação:</span> {dt_pub}</div>
            </div>
            <div><span class="info-label">Termos:</span> {terms}</div>
            <div class="objeto-text"><b>Objeto:</b> {objeto}</div>
            <div class="links-bar">
                {"<a href='" + link_pncp + "' target='_blank'>🔗 Abrir no PNCP</a>" if link_pncp else ""}
                {"<a href='" + link_origem + "' target='_blank'>🌐 Portal de Origem</a>" if link_origem else ""}
            </div>
        </div>
        """

html_content += """</body></html>"""

with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"HTML generated at {html_file}")

edge_bin = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if not os.path.exists(edge_bin):
    edge_bin = r'C:\Program Files\Microsoft\Edge\Application\msedge.exe'

cmd = [
    edge_bin,
    '--headless',
    '--disable-gpu',
    '--no-pdf-header-footer',
    f'--print-to-pdf={pdf_file}',
    f'file:///{html_file.replace("\\", "/")}'
]

subprocess.run(cmd, capture_output=True, text=True)
if os.path.exists(pdf_file):
    print(f"SUCCESS: PDF generated at {pdf_file}, Size: {os.path.getsize(pdf_file)/1024:.2f} KB")
