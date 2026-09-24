import openpyxl
from datetime import datetime, time
from collections import Counter, defaultdict
import re

wb = openpyxl.load_workbook(r'C:\Users\11429149760\Downloads\chamados glpi consolidados.xlsx', data_only=True)
ws = wb.active
rows = list(ws.iter_rows(values_only=True))
header = rows[0]
data = rows[1:]

total_rows = len(data)

# 1. Spurious vs Event rows
spurious_rows = []
event_rows = []

for r in data:
    cat = str(r[7] or '')
    if 'Banco de Dados' in cat or 'Seguran' in cat:
        spurious_rows.append(r)
    else:
        event_rows.append(r)

print('--- AUDIT COUNTS ---')
print(f'Total rows in spreadsheet: {total_rows}')
print(f'Spurious (Oracle Capacity Planning + InfoSec): {len(spurious_rows)}')
print(f'Net Event tickets: {len(event_rows)}')

# 2. Date ranges
min_date = min(r[2] for r in data if isinstance(r[2], datetime))
max_date = max(r[2] for r in data if isinstance(r[2], datetime))
span_days = (max_date - min_date).days
span_years = span_days / 365.25
months = span_days / 30.4375

print(f"Date range: {min_date.strftime('%d/%m/%Y')} a {max_date.strftime('%d/%m/%Y')}")
print(f"Span: {span_days} dias ({span_years:.2f} anos / {months:.1f} meses)")

# 3. Time window analysis (Alínea A)
open_8_20 = sum(1 for r in event_rows if isinstance(r[2], datetime) and time(8,0) <= r[2].time() < time(20,0))
open_out = len(event_rows) - open_8_20
open_weekend = sum(1 for r in event_rows if isinstance(r[2], datetime) and r[2].weekday() >= 5)

sol_rows = [r for r in event_rows if isinstance(r[12], datetime)]
sol_8_20 = sum(1 for r in sol_rows if time(8,0) <= r[12].time() < time(20,0))
sol_out = len(sol_rows) - sol_8_20
sol_weekend = sum(1 for r in sol_rows if r[12].weekday() >= 5)

print('\n--- ALINEA A (HORARIOS) ---')
print(f'Abertura 08h-20h: {open_8_20} ({open_8_20/len(event_rows)*100:.2f}%)')
print(f'Abertura fora 08h-20h: {open_out} ({open_out/len(event_rows)*100:.2f}%)')
print(f'Abertura final de semana: {open_weekend} ({open_weekend/len(event_rows)*100:.2f}%)')
print(f'Solucao com data/hora registrada: {len(sol_rows)}')
print(f'Solucao 08h-20h: {sol_8_20} ({sol_8_20/len(sol_rows)*100:.2f}%)')
print(f'Solucao fora 08h-20h: {sol_out} ({sol_out/len(sol_rows)*100:.2f}%)')
print(f'Solucao final de semana: {sol_weekend} ({sol_weekend/len(sol_rows)*100:.2f}%)')

# 4. Service Nature (Alínea B)
def classify_detail(r):
    cid, title, d_op, h_op, last_up, req, req_grp, cat, tech, tech_grp, follow, desc, d_sl, h_sl = r
    title_s = str(title or '').lower()
    cat_s = str(cat or '').lower()
    leaf_cat = cat_s.split('>')[-1].strip()
    desc_s = str(desc or '').lower()
    follow_s = str(follow or '').lower()
    all_text = f'{title_s} {desc_s} {follow_s}'
    
    is_online = any(k in all_text for k in ['zoom', 'teams', 'meet', 'youtube', 'streamyard', 'transmiss', 'webinar', 'virtual']) or 'transmiss' in leaf_cat
    is_ji = any(k in all_text for k in ['justia itinerante', 'justica itinerante', 'ao social', 'acao social', 'mutiro', 'mutirao', 'itinerante', 'cogpi']) or 'ao social' in leaf_cat
    is_event = ('evento' in leaf_cat or 'cerimonial' in str(req_grp).lower() or any(k in all_text for k in ['cerimonial', 'posse', 'seminrio', 'seminario', 'conferncia', 'conferencia', 'congresso', 'rock in rio', 'spanta', 'audittio', 'auditorio', 'palestra', 'solenidade', 'forum']))
    is_meeting = 'reuni' in leaf_cat or 'reuni' in title_s
    
    if is_ji:
        return 'Justica Itinerante / Acao Social (Campo/Externo)'
    elif is_event:
        if is_online:
            return 'Transmissao Online / Live / Webinar (Catalogo Ordinario)'
        return 'Suporte a Eventos Presenciais / Institucionais (Excepcional)'
    elif is_meeting:
        if is_online:
            return 'Reuniao Virtual / Hibrida (Catalogo Ordinario)'
        return 'Suporte a Reuniao Presencial (Sede/Salas)'
    else:
        if is_online:
            return 'Transmissao Online / Live / Webinar (Catalogo Ordinario)'
        return 'Suporte a Eventos Presenciais / Institucionais (Excepcional)'

b_counts = Counter()
for r in event_rows:
    b_counts[classify_detail(r)] += 1

print('\n--- ALINEA B (NATUREZA DOS SERVICOS) ---')
for k, v in b_counts.most_common():
    print(f'{k}: {v} ({v/len(event_rows)*100:.2f}%)')

# 5. Deduplication (Alínea C)
date_pat = re.compile(r'(\b\d{1,2}[\/\.-]\d{1,2}(?:[\/\.-]\d{2,4})?\b)')
events_map = defaultdict(list)

for r in event_rows:
    cid, title, d_op, h_op, last_up, req, req_grp, cat, tech, tech_grp, follow, desc, d_sl, h_sl = r
    t_clean = str(title or '').strip()
    m_d = date_pat.search(t_clean)
    if m_d:
        ev_d = m_d.group(1)
    elif isinstance(d_sl, datetime):
        ev_d = d_sl.strftime('%d/%m/%Y')
    elif isinstance(d_op, datetime):
        ev_d = d_op.strftime('%d/%m/%Y')
    else:
        ev_d = 'DATA_INDET'
        
    parts = re.split(r'[-–—|]', t_clean)
    loc = parts[-1].strip() if len(parts) >= 2 else t_clean
    loc_norm = re.sub(r'[^a-zA-Z0-9]', '', loc).upper()[:25]
    
    events_map[(ev_d, loc_norm)].append(cid)

unique_phys_events = len(events_map)
print('\n--- ALINEA C (DEDUPLICACAO FISICA) ---')
print(f'Eventos fisicos unicos identificados: {unique_phys_events}')
print(f'Media de chamados por evento fisico unico: {len(event_rows) / unique_phys_events:.2f}')

# 6. TR 6.16 Comparison
ji_social_count = b_counts['Justica Itinerante / Acao Social (Campo/Externo)']
event_pres_count = b_counts['Suporte a Eventos Presenciais / Institucionais (Excepcional)']
total_exceptional_tickets = ji_social_count + event_pres_count
annual_exceptional_tickets = total_exceptional_tickets / span_years

print('\n--- COMPARATIVO COM SUBITEM 6.16 DO TR ---')
print(f'Chamados Excepcionais de Campo (JI + Eventos Presenciais): {total_exceptional_tickets}')
print(f'Anualizado (chamados): {annual_exceptional_tickets:.1f} chamados/ano')
print(f'Estimativa contratual no TR 6.16: 130/ano')
print(f'Fator de Excesso sobre a estimativa: {annual_exceptional_tickets / 130:.2f}x ({((annual_exceptional_tickets / 130) - 1)*100:.1f}% de acrescimo)')

annual_unique_events = unique_phys_events / span_years
print(f'Eventos fisicos unicos anualizados: {annual_unique_events:.1f} eventos/ano')
print(f'Fator de Excesso em eventos unicos: {annual_unique_events / 130:.2f}x ({((annual_unique_events / 130) - 1)*100:.1f}% de acrescimo)')
