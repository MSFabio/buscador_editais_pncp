"""
Script de Renderização do Relatório Técnico-Jurídico em Documento Word (.docx)
Converte RELATORIO_COMPARATIVO_ANALISE_SEMANTICA.md em um documento DOCX profissional,
com identidade visual institucional, capa, sumário, tabelas formatadas, alertas e paginação.
"""

import sys
import os
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\11429149760\.gemini\antigravity\scratch\analise_licitacao_telecom"
MD_FILE = os.path.join(BASE_DIR, "RELATORIO_COMPARATIVO_ANALISE_SEMANTICA.md")
DOCX_OUT = os.path.join(BASE_DIR, "RELATORIO_COMPARATIVO_ANALISE_SEMANTICA.docx")

# Cores da Paleta Institucional
COLOR_PRIMARY = RGBColor(15, 37, 55)       # Deep Navy #0F2537
COLOR_SECONDARY = RGBColor(43, 108, 176)   # Slate Blue #2B6CB0
COLOR_TEXT = RGBColor(45, 55, 72)          # Charcoal #2D3748
COLOR_MUTED = RGBColor(113, 128, 150)      # Muted Gray #718096
HEX_PRIMARY = "0F2537"
HEX_LIGHT_BG = "F7FAFC"
HEX_ALT_ROW = "EDF2F7"
HEX_ALERT_BORDER = "C53030"
HEX_ALERT_BG = "FFF5F5"
HEX_INFO_BORDER = "2B6CB0"
HEX_INFO_BG = "EBF8FF"

def set_cell_background(cell, hex_color):
    """Define a cor de fundo de uma célula via XML."""
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=120, bottom=120, left=150, right=150):
    """Define margens internas da célula em twips (1/20 pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def set_table_borders(table, color="CBD5E0", sz="4"):
    """Aplica bordas suaves cinzas em toda a tabela."""
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'<w:insideH w:val="single" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def clean_latex_and_symbols(text):
    """Sanitiza quaisquer tags LaTeX ou símbolos residuais para tipografia limpa, preservando moedas."""
    if not text:
        return ""
    # 1. Proteger moeda R$ e R\$
    text = re.sub(r'R\$\s*|R\\\$\s*', '###RS###', text)
    # 2. Desempacotar comandos e símbolos LaTeX
    text = re.sub(r'\\text\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\mathbf\{([^}]+)\}', r'**\1**', text)
    text = re.sub(r'\\mathrm\{([^}]+)\}', r'\1', text)
    text = text.replace(r'\times', '×')
    text = text.replace(r'\approx', '≈')
    text = text.replace(r'\ge', '≥')
    text = text.replace(r'\le', '≤')
    text = text.replace(r'\ ', ' ')
    text = text.replace(r'\*', '*')
    text = text.replace('\\', '')
    # 3. Remover delimitadores de fórmulas matemáticas restantes
    text = text.replace('$$', '').replace('$', '')
    # 4. Restaurar moeda
    text = text.replace('###RS###', 'R$ ')
    text = re.sub(r'R\$\s+', 'R$ ', text)
    return text

def add_callout(doc, text_lines, alert_type="INFO"):
    """Adiciona caixa de destaque (Callout box) com borda lateral colorida."""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    cell = tbl.cell(0, 0)
    cell.width = Inches(6.5)
    
    border_hex = HEX_ALERT_BORDER if alert_type in ["WARNING", "CAUTION", "IMPORTANT"] else HEX_INFO_BORDER
    bg_hex = HEX_ALERT_BG if alert_type in ["WARNING", "CAUTION", "IMPORTANT"] else HEX_INFO_BG
    
    set_cell_background(cell, bg_hex)
    set_cell_margins(cell, top=160, bottom=160, left=200, right=200)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:left w:val="single" w:sz="36" w:space="0" w:color="{border_hex}"/>'
        f'<w:top w:val="none"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.line_spacing = 1.15
    
    prefix = "AVISO IMPORTANTE: " if alert_type in ["WARNING", "CAUTION", "IMPORTANT"] else "NOTA TÉCNICA: "
    run_title = p.add_run(prefix)
    run_title.bold = True
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(10.5)
    run_title.font.color.rgb = RGBColor(197, 48, 48) if alert_type in ["WARNING", "CAUTION", "IMPORTANT"] else COLOR_SECONDARY
    
    for i, line in enumerate(text_lines):
        if i > 0:
            p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
        clean_line = clean_latex_and_symbols(re.sub(r'^\s*[\*\-]\s*', '', line).strip())
        run = p.add_run(clean_line)
        run.font.name = "Calibri"
        run.font.size = Pt(10)
        run.font.color.rgb = COLOR_TEXT
        if clean_line.startswith("**"):
            run.bold = True
            
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def parse_markdown_table(table_text):
    """Converte linhas de tabela markdown em matriz de strings limpas."""
    lines = [l.strip() for l in table_text.strip().split("\n") if l.strip()]
    if len(lines) < 2:
        return None
    matrix = []
    for l in lines:
        if re.match(r"^\|?[\s\-:|]+\|?$", l):
            continue
        cells = [c.strip() for c in l.split("|")]
        if cells and cells[0] == "":
            cells.pop(0)
        if cells and cells[-1] == "":
            cells.pop(-1)
        if cells:
            matrix.append(cells)
    return matrix if len(matrix) >= 2 else None

def render_table_in_docx(doc, matrix):
    """Cria tabela DOCX com formatação refinada, cabeçalho e zebrado."""
    num_rows = len(matrix)
    num_cols = max(len(row) for row in matrix)
    
    tbl = doc.add_table(rows=num_rows, cols=num_cols)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl)
    
    # Processar cabeçalho
    header_row = matrix[0]
    for c_idx in range(num_cols):
        cell = tbl.cell(0, c_idx)
        val = header_row[c_idx] if c_idx < len(header_row) else ""
        set_cell_background(cell, HEX_PRIMARY)
        set_cell_margins(cell, top=140, bottom=140, left=120, right=120)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(val)
        run.bold = True
        run.font.name = "Calibri"
        run.font.size = Pt(9.5)
        run.font.color.rgb = RGBColor(255, 255, 255)
        
    # Processar linhas de dados
    for r_idx in range(1, num_rows):
        row_data = matrix[r_idx]
        bg_color = HEX_ALT_ROW if (r_idx % 2 == 0) else "FFFFFF"
        for c_idx in range(num_cols):
            cell = tbl.cell(r_idx, c_idx)
            val = row_data[c_idx] if c_idx < len(row_data) else ""
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
            sublines = re.split(r'<br\s*/?>', val, flags=re.IGNORECASE)
            for s_idx, subline in enumerate(sublines):
                if s_idx == 0:
                    p = cell.paragraphs[0]
                else:
                    p = cell.add_paragraph()
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(1)
                p.paragraph_format.line_spacing = 1.1
                
                sub_clean = clean_latex_and_symbols(subline.strip())
                # Alinhamento
                is_num = any(sym in sub_clean for sym in ["R$", "%"]) or (sub_clean.replace(".", "").replace(",", "").isdigit())
                if is_num and len(sublines) == 1:
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                elif c_idx == 0 and len(sub_clean) < 15 and len(sublines) == 1:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
                # Renderizar spans em negrito
                parts = re.split(r'(\*\*[^\*]+\*\*)', sub_clean)
                for part in parts:
                    if part.startswith("**") and part.endswith("**"):
                        r = p.add_run(part[2:-2])
                        r.bold = True
                    else:
                        r = p.add_run(part)
                    r.font.name = "Calibri"
                    r.font.size = Pt(8.5)
                    r.font.color.rgb = COLOR_TEXT
                    if "Altíssima" in part or "Ideal" in part:
                        r.font.color.rgb = RGBColor(39, 103, 73)
                        r.bold = True
                    elif "Muito Baixa" in part or "Outlier" in part:
                        r.font.color.rgb = RGBColor(197, 48, 48)
                
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

def build_docx():
    print("Iniciando geração do documento Word (.docx)...", flush=True)
    with open(MD_FILE, "r", encoding="utf-8") as f:
        md_text = f.read()
        
    doc = Document()
    
    # Configurar margens
    sections = doc.sections
    for sec in sections:
        sec.top_margin = Inches(0.8)
        sec.bottom_margin = Inches(0.8)
        sec.left_margin = Inches(0.8)
        sec.right_margin = Inches(0.8)
        
        # Cabeçalho
        header = sec.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("Processo Administrativo SEI nº E-20/001.008552/2026 | DPRJ")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = COLOR_MUTED
        
        # Rodapé
        footer = sec.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("Defensoria Pública do Estado do Rio de Janeiro — Relatório Técnico-Jurídico de Análise de Preços e Escopo")
        frun.font.name = "Calibri"
        frun.font.size = Pt(8)
        frun.font.color.rgb = COLOR_MUTED
        
    # --- CAPA / CABEÇALHO FORMAL ---
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("DEFENSORIA PÚBLICA DO ESTADO DO RIO DE JANEIRO\nCOORDENAÇÃO DE PLANEJAMENTO E PESQUISA DE MERCADO\nDIRETORIA DE GESTÃO DA INFORMAÇÃO — NÚCLEO DE INFRAESTRUTURA\n")
    r_inst.bold = True
    r_inst.font.name = "Calibri"
    r_inst.font.size = Pt(11)
    r_inst.font.color.rgb = COLOR_SECONDARY
    p_inst.paragraph_format.space_after = Pt(20)
    
    # Título Principal
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("RELATÓRIO TÉCNICO-JURÍDICO DE ANÁLISE SEMÂNTICA, MODELAGEM ECONÔMICA E ADERÊNCIA DE ESCOPO")
    r_title.bold = True
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(18)
    r_title.font.color.rgb = COLOR_PRIMARY
    p_title.paragraph_format.space_after = Pt(8)
    
    # Subtítulo
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("Contratação Direta Emergencial de Conectividade WAN com Gerenciamento SD-WAN e Segurança de Borda (Art. 75, VIII, Lei 14.133/2021)\nProcesso SEI nº E-20/001.008552/2026")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = COLOR_SECONDARY
    p_sub.paragraph_format.space_after = Pt(24)
    
    # Linha divisória
    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_div = p_div.add_run("—" * 45)
    r_div.font.color.rgb = COLOR_MUTED
    p_div.paragraph_format.space_after = Pt(24)
    
    # Processar conteúdo Markdown
    blocks = re.split(r'\n(?=#{1,4}\s+|>[^>\n]+|\|)', md_text)
    
    in_table_block = False
    current_table_lines = []
    
    lines = md_text.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        line_s = line.strip()
        
        # Ignorar capa inicial do markdown pois já criamos estilizada
        if line_s.startswith("# RELATÓRIO TÉCNICO-JURÍDICO") or line_s.startswith("## Processo Administrativo") or line_s.startswith("### *Régua") or line_s.startswith("### *Com Matriz"):
            i += 1
            continue
            
        # Detectar tabela markdown
        if line_s.startswith("|") and line_s.endswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                table_lines.append(lines[i])
                i += 1
            mat = parse_markdown_table("\n".join(table_lines))
            if mat:
                render_table_in_docx(doc, mat)
            continue
            
        # Detectar Alert / Callout
        if line_s.startswith("> [!"):
            alert_type = "INFO"
            if "WARNING" in line_s: alert_type = "WARNING"
            elif "CAUTION" in line_s: alert_type = "CAUTION"
            elif "IMPORTANT" in line_s: alert_type = "IMPORTANT"
            
            callout_lines = []
            i += 1
            while i < len(lines) and lines[i].strip().startswith(">"):
                c_line = lines[i].strip()[1:].strip()
                callout_lines.append(c_line)
                i += 1
            add_callout(doc, callout_lines, alert_type)
            continue
            
        # Títulos
        if line_s.startswith("## "):
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(16)
            h.paragraph_format.space_after = Pt(6)
            h.paragraph_format.keep_with_next = True
            run = h.add_run(clean_latex_and_symbols(line_s[3:].strip()))
            run.bold = True
            run.font.name = "Calibri"
            run.font.size = Pt(14)
            run.font.color.rgb = COLOR_PRIMARY
            i += 1
            continue
        elif line_s.startswith("### "):
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(12)
            h.paragraph_format.space_after = Pt(4)
            h.paragraph_format.keep_with_next = True
            run = h.add_run(clean_latex_and_symbols(line_s[4:].strip()))
            run.bold = True
            run.font.name = "Calibri"
            run.font.size = Pt(12)
            run.font.color.rgb = COLOR_SECONDARY
            i += 1
            continue
        elif line_s.startswith("#### "):
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(10)
            h.paragraph_format.space_after = Pt(3)
            h.paragraph_format.keep_with_next = True
            run = h.add_run(clean_latex_and_symbols(line_s[5:].strip()))
            run.bold = True
            run.font.name = "Calibri"
            run.font.size = Pt(11)
            run.font.color.rgb = COLOR_TEXT
            i += 1
            continue
            
        # Listas com marcadores (* ou -)
        if line_s.startswith("* ") or line_s.startswith("- "):
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            content = clean_latex_and_symbols(line_s[2:].strip())
            parts = re.split(r'(\*\*[^\*]+\*\*)', content)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    r = p.add_run(part[2:-2])
                    r.bold = True
                else:
                    r = p.add_run(part)
                r.font.name = "Calibri"
                r.font.size = Pt(10)
                r.font.color.rgb = COLOR_TEXT
            i += 1
            continue
            
        # Parágrafos normais
        if line_s:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(3)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            line_cleaned = clean_latex_and_symbols(line_s)
            parts = re.split(r'(\*\*[^\*]+\*\*)', line_cleaned)
            for part in parts:
                if part.startswith("**") and part.endswith("**"):
                    r = p.add_run(part[2:-2])
                    r.bold = True
                else:
                    r = p.add_run(part)
                r.font.name = "Calibri"
                r.font.size = Pt(10)
                r.font.color.rgb = COLOR_TEXT
                
        i += 1
        
    try:
        print(f"Salvando documento Word em: {DOCX_OUT}...", flush=True)
        doc.save(DOCX_OUT)
        print(f"Documento Word salvo com sucesso! ({os.path.getsize(DOCX_OUT):,} bytes)", flush=True)
    except PermissionError:
        fallback = os.path.join(BASE_DIR, "RELATORIO_COMPARATIVO_ANALISE_SEMANTICA_ATUALIZADO.docx")
        print(f"Aviso: Arquivo aberto em outro aplicativo. Gravando cópia em: {fallback}...", flush=True)
        doc.save(fallback)
        print(f"Documento Word salvo com sucesso em cópia atualizada! ({os.path.getsize(fallback):,} bytes)", flush=True)

if __name__ == "__main__":
    build_docx()
