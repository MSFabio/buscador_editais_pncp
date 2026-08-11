import json
import datetime

json_file = r'C:\Users\11429149760\.gemini\antigravity\scratch\pncp_results.json'
artifact_file = r'C:\Users\11429149760\.gemini\antigravity\brain\001766fb-0fab-4892-bf1e-723cc736a97c\editais_pncp_bahia.md'

with open(json_file, 'r', encoding='utf-8') as f:
    items = json.load(f)

ba_items = [item for item in items if item.get('uf') == 'BA']

def fmt_date(dt_str):
    if not dt_str:
        return "Não informada"
    try:
        clean = dt_str.split('.')[0]
        if 'T' in clean:
            dt = datetime.datetime.strptime(clean, "%Y-%m-%dT%H:%M:%S")
            return dt.strftime("%d/%m/%Y às %H:%H")
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

lines = []
lines.append("# 📍 Editais Abertos PNCP - Estado da Bahia (BA)")
lines.append(f"**Data do Filtro:** 06/08/2026  ")
lines.append(f"**Filtro:** UF = BA | Editais Abertos / Recebendo Proposta com Sessão Pública em Datas Futuras  ")
lines.append(f"**Total Encontrado na Bahia:** `{len(ba_items)}` editais únicos\n")

lines.append("> [!NOTE]")
lines.append("> Todos os editais listados abaixo são de órgãos localizados na **Bahia** com prazos abertos para datas futuras a partir de 06/08/2026.\n")

lines.append("## 📜 Lista de Editais na Bahia\n")

for idx, item in enumerate(ba_items, 1):
    orgao = item.get('orgao') or 'Não informado'
    unidade = item.get('unidade') or ''
    muni = item.get('municipio') or 'Bahia'
    loc = f"{muni} - BA"
    
    title = item.get('title') or f"Edital {item.get('control_num')}"
    modalidade = item.get('modalidade') or 'Pregão / Concorrência / Dispensa'
    objeto = (item.get('objeto') or 'Sem descrição do objeto.').strip()
    
    val = fmt_currency(item.get('valor_estimado'))
    dt_pub = fmt_date(item.get('data_publicacao'))
    dt_abert = fmt_date(item.get('data_abertura_proposta'))
    dt_enc = fmt_date(item.get('data_encerramento_proposta'))
    
    terms_str = ", ".join([f"`{t}`" for t in item.get('matched_terms', [])])
    
    link_pncp = item.get('link_pncp')
    link_origem = item.get('link_origem')
    
    lines.append(f"### {idx}. {title} — {orgao}")
    lines.append(f"- **Órgão / Entidade:** {orgao}")
    if unidade and unidade != orgao:
        lines.append(f"- **Unidade:** {unidade}")
    lines.append(f"- **Município / UF:** {loc}")
    lines.append(f"- **Modalidade:** {modalidade}")
    lines.append(f"- **Termos Relacionados:** {terms_str}")
    lines.append(f"- **Valor Estimado:** `{val}`")
    lines.append(f"- **Data de Publicação:** {dt_pub}")
    lines.append(f"- **Abertura das Propostas:** {dt_abert}")
    lines.append(f"- **Encerramento / Sessão Pública:** **{dt_enc}**")
    lines.append(f"- **Objeto:** {objeto}")
    
    links_md = []
    if link_pncp:
        links_md.append(f"[🔗 Ver no PNCP]({link_pncp})")
    if link_origem:
        links_md.append(f"[🌐 Acessar Sistema de Origem]({link_origem})")
    
    lines.append(f"- **Links:** {' | '.join(links_md)}")
    lines.append("\n---\n")

report_content = "\n".join(lines)

with open(artifact_file, 'w', encoding='utf-8') as f:
    f.write(report_content)

print(f"Bahia report generated: {len(ba_items)} items.")
