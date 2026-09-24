"""
Script Otimizado de Renderização do Relatório Técnico-Jurídico em Documento PDF
Converte RELATORIO_COMPARATIVO_ANALISE_SEMANTICA.md em um PDF profissional,
com formatação institucional, paginação dinâmica 'Página X de Y',
cabeçalhos, alertas, cores corporativas e tabelas auto-ajustadas.
"""

import sys
import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = r"C:\Users\11429149760\.gemini\antigravity\scratch\analise_licitacao_telecom"
MD_FILE = os.path.join(BASE_DIR, "RELATORIO_COMPARATIVO_ANALISE_SEMANTICA.md")
PDF_OUT = os.path.join(BASE_DIR, "RELATORIO_COMPARATIVO_ANALISE_SEMANTICA.pdf")

# Paleta Institucional
C_PRIMARY = HexColor("#0F2537")       # Navy Escuro
C_SECONDARY = HexColor("#2B6CB0")     # Azul ardósia
C_TEXT = HexColor("#2D3748")          # Carvão
C_MUTED = HexColor("#718096")         # Cinza suave
C_BORDER = HexColor("#CBD5E0")        # Borda de tabela
C_ALT_ROW = HexColor("#F7FAFC")       # Fundo alternado
C_ALERT_BG = HexColor("#FFF5F5")      # Alerta fundo
C_ALERT_BORDER = HexColor("#C53030")  # Alerta borda
C_INFO_BG = HexColor("#EBF8FF")       # Info fundo
C_INFO_BORDER = HexColor("#2B6CB0")   # Info borda

class NumberedCanvas(canvas.Canvas):
    """Canvas de dois passos para calcular dinamicamente o total de páginas (Página X de Y)."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber > 1:
            self.saveState()
            self.setFont("Helvetica", 8)
            self.setFillColor(C_MUTED)
            # Cabeçalho
            self.drawString(38, 804, "Processo Administrativo SEI nº E-20/001.008552/2026 | DPRJ")
            self.setStrokeColor(C_BORDER)
            self.setLineWidth(0.5)
            self.line(38, 798, 557, 798)
            # Rodapé
            self.line(38, 42, 557, 42)
            self.drawString(38, 30, "Defensoria Pública do Estado do Rio de Janeiro — Relatório Técnico-Jurídico")
            page_text = f"Página {self._pageNumber} de {page_count}"
            self.drawRightString(557, 30, page_text)
            self.restoreState()

def format_inline_markdown(text):
    """Trata negrito, itálico e caracteres especiais escapando XML para o ReportLab."""
    if not text:
        return ""
    # 1. Proteger moeda R$ e R\$
    text = re.sub(r'R\$\s*|R\\\$\s*', '###RS###', text)
    # 2. Escapar & para XML
    text = re.sub(r'&(?!amp;|lt;|gt;|quot;|#\d+;)', '&amp;', text)
    # 3. Símbolos e macros LaTeX
    text = re.sub(r'\\text\{([^}]+)\}', r'\1', text)
    text = re.sub(r'\\mathbf\{([^}]+)\}', r'**\1**', text)
    text = re.sub(r'\\mathrm\{([^}]+)\}', r'\1', text)
    text = text.replace(r'\ge', '≥').replace(r'\le', '≤').replace(r'\times', '×').replace(r'\approx', '≈')
    text = text.replace(r'\ ', ' ')
    text = text.replace(r'\*', '*')
    text = text.replace('\\', '')
    # 4. Remover delimitadores de fórmulas matemáticas restantes
    text = text.replace('$$', '').replace('$', '')
    # 5. Restaurar moeda
    text = text.replace('###RS###', 'R$ ')
    text = re.sub(r'R\$\s+', 'R$ ', text)
    # 6. Preservar tags <br/> e marcar negrito/itálico com placeholders seguros
    text = re.sub(r'<br\s*/?>', '###BR###', text, flags=re.IGNORECASE)
    text = re.sub(r'\*\*(.*?)\*\*', r'###BOLD_START###\1###BOLD_END###', text)
    text = re.sub(r'\*(.*?)\*', r'###ITALIC_START###\1###ITALIC_END###', text)
    # 7. Escapar < e > para XML
    text = text.replace('<', '&lt;').replace('>', '&gt;')
    # 8. Restaurar tags válidas do ReportLab
    text = text.replace('###BR###', '<br/>')
    text = text.replace('###BOLD_START###', '<b>').replace('###BOLD_END###', '</b>')
    text = text.replace('###ITALIC_START###', '<i>').replace('###ITALIC_END###', '</i>')
    return text

def parse_markdown_table(table_text):
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

def build_pdf():
    print("Iniciando geração do documento PDF institucional com ReportLab...", flush=True)
    with open(MD_FILE, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = SimpleDocTemplate(
        PDF_OUT,
        pagesize=A4,
        leftMargin=38,
        rightMargin=38,
        topMargin=46,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=C_PRIMARY,
        alignment=1,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12.5,
        textColor=C_SECONDARY,
        alignment=1,
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14.5,
        textColor=C_PRIMARY,
        spaceBefore=12,
        spaceAfter=4,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=12.5,
        textColor=C_SECONDARY,
        spaceBefore=9,
        spaceAfter=3,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'Heading3_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=C_TEXT,
        spaceBefore=6,
        spaceAfter=2,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=C_TEXT,
        spaceBefore=2,
        spaceAfter=3
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=C_TEXT,
        leftIndent=12,
        firstLineIndent=-8,
        spaceBefore=1,
        spaceAfter=2
    )

    th_style = ParagraphStyle(
        'TH_Style',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=6.8,
        leading=8.5,
        textColor=white,
        alignment=1
    )

    td_style = ParagraphStyle(
        'TD_Style',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.5,
        leading=8.2,
        textColor=C_TEXT
    )

    td_num_style = ParagraphStyle(
        'TD_Num_Style',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=6.5,
        leading=8.2,
        textColor=C_TEXT,
        alignment=2
    )

    story = []

    # Cabeçalho institucional formal
    inst_header = (
        "<b>DEFENSORIA PÚBLICA DO ESTADO DO RIO DE JANEIRO</b><br/>"
        "COORDENAÇÃO DE PLANEJAMENTO E PESQUISA DE MERCADO<br/>"
        "DIRETORIA DE GESTÃO DA INFORMAÇÃO — NÚCLEO DE INFRAESTRUTURA"
    )
    story.append(Paragraph(inst_header, ParagraphStyle('InstHead', alignment=1, fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=C_SECONDARY)))
    story.append(Spacer(1, 8))

    story.append(Paragraph("RELATÓRIO TÉCNICO-JURÍDICO DE ANÁLISE SEMÂNTICA, MODELAGEM ECONÔMICA E ADERÊNCIA DE ESCOPO", title_style))
    story.append(Paragraph("Contratação Direta Emergencial de Conectividade WAN com Gerenciamento SD-WAN e Segurança de Borda (Art. 75, VIII, Lei 14.133/2021)<br/>Processo Administrativo SEI nº E-20/001.008552/2026", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=C_BORDER, spaceBefore=2, spaceAfter=8))

    lines = md_text.split("\n")
    i = 0
    printable_width = 519

    while i < len(lines):
        line = lines[i]
        line_s = line.strip()

        # Ignorar capa inicial do markdown
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
                num_cols = max(len(r) for r in mat)
                if num_cols == 13: # Matriz de escopo técnico
                    col_widths = [44, 68] + [31]*8 + [36, 38, 63]
                elif num_cols == 7: # Tabela de 100 Mbps
                    col_widths = [45, 95, 60, 48, 65, 75, 75]
                elif num_cols == 8: # Tabela de ranking
                    col_widths = [50, 90, 55, 55, 55, 55, 70, 75]
                elif num_cols == 4: # Tabela global de cenários
                    col_widths = [190, 95, 105, 115]
                else:
                    col_w = printable_width / num_cols
                    col_widths = [col_w] * num_cols

                flowable_data = []
                # Cabeçalho
                h_row = []
                for c_idx in range(num_cols):
                    v = mat[0][c_idx] if c_idx < len(mat[0]) else ""
                    v_clean = format_inline_markdown(v)
                    h_row.append(Paragraph(f"<b>{v_clean}</b>", th_style))
                flowable_data.append(h_row)

                # Linhas de dados
                for r_idx in range(1, len(mat)):
                    row_data = []
                    for c_idx in range(num_cols):
                        v = mat[r_idx][c_idx] if c_idx < len(mat[r_idx]) else ""
                        v_clean = format_inline_markdown(v)
                        is_num = any(sym in v for sym in ["R$", "%", "R$ "]) or v.replace(".", "").replace(",", "").isdigit()
                        st = td_num_style if is_num else td_style
                        row_data.append(Paragraph(v_clean, st))
                    flowable_data.append(row_data)

                t = Table(flowable_data, colWidths=col_widths, repeatRows=1)
                t_style = [
                    ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
                    ('TOPPADDING', (0, 0), (-1, -1), 2.5),
                    ('LEFTPADDING', (0, 0), (-1, -1), 2.5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 2.5),
                    ('GRID', (0, 0), (-1, -1), 0.4, C_BORDER),
                ]
                for r_idx in range(1, len(mat)):
                    if r_idx % 2 == 0:
                        t_style.append(('BACKGROUND', (0, r_idx), (-1, r_idx), C_ALT_ROW))
                t.setStyle(TableStyle(t_style))
                story.append(Spacer(1, 3))
                story.append(t)
                story.append(Spacer(1, 5))
            continue

        # Detectar Alert / Callout
        if line_s.startswith("> [!"):
            alert_type = "INFO"
            if "WARNING" in line_s: alert_type = "WARNING"
            elif "CAUTION" in line_s: alert_type = "CAUTION"
            elif "IMPORTANT" in line_s: alert_type = "IMPORTANT"

            callout_paras = []
            i += 1
            while i < len(lines) and lines[i].strip().startswith(">"):
                c_line = lines[i].strip()[1:].strip()
                if c_line:
                    c_clean = format_inline_markdown(c_line)
                    callout_paras.append(Paragraph(c_clean, body_style))
                i += 1

            border_c = C_ALERT_BORDER if alert_type in ["WARNING", "CAUTION", "IMPORTANT"] else C_INFO_BORDER
            bg_c = C_ALERT_BG if alert_type in ["WARNING", "CAUTION", "IMPORTANT"] else C_INFO_BG
            title_text = "<b>AVISO IMPORTANTE</b>" if alert_type in ["WARNING", "CAUTION", "IMPORTANT"] else "<b>NOTA TÉCNICA</b>"

            callout_content = [[Paragraph(f"<font color='{border_c.hexval()}'>{title_text}</font>", h3_style)]]
            for cp in callout_paras:
                callout_content.append([cp])

            callout_table = Table(callout_content, colWidths=[printable_width])
            callout_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), bg_c),
                ('LEFTPADDING', (0, 0), (-1, -1), 7),
                ('RIGHTPADDING', (0, 0), (-1, -1), 7),
                ('TOPPADDING', (0, 0), (-1, -1), 3),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
                ('LINEBEFORE', (0, 0), (0, -1), 3, border_c),
            ]))
            story.append(Spacer(1, 3))
            story.append(callout_table)
            story.append(Spacer(1, 5))
            continue

        # Títulos
        if line_s.startswith("## "):
            story.append(Paragraph(format_inline_markdown(line_s[3:].strip()), h1_style))
            i += 1
            continue
        elif line_s.startswith("### "):
            story.append(Paragraph(format_inline_markdown(line_s[4:].strip()), h2_style))
            i += 1
            continue
        elif line_s.startswith("#### "):
            story.append(Paragraph(format_inline_markdown(line_s[5:].strip()), h3_style))
            i += 1
            continue

        # Listas com marcadores
        if line_s.startswith("* ") or line_s.startswith("- "):
            clean_b = format_inline_markdown(line_s[2:].strip())
            story.append(Paragraph(f"• {clean_b}", bullet_style))
            i += 1
            continue

        # Parágrafos normais
        if line_s:
            p_clean = format_inline_markdown(line_s)
            story.append(Paragraph(p_clean, body_style))

        i += 1

    try:
        print(f"Compilando PDF em: {PDF_OUT}...", flush=True)
        doc.build(story, canvasmaker=NumberedCanvas)
        print(f"Documento PDF gerado com sucesso! ({os.path.getsize(PDF_OUT):,} bytes)", flush=True)
    except PermissionError:
        fallback = os.path.join(BASE_DIR, "RELATORIO_COMPARATIVO_ANALISE_SEMANTICA_ATUALIZADO.pdf")
        print(f"Aviso: PDF aberto em outro visualizador. Gravando em cópia de segurança: {fallback}...", flush=True)
        doc_fallback = SimpleDocTemplate(
            fallback,
            pagesize=A4,
            leftMargin=38,
            rightMargin=38,
            topMargin=46,
            bottomMargin=46
        )
        doc_fallback.build(story, canvasmaker=NumberedCanvas)
        print(f"Documento PDF gerado com sucesso em cópia atualizada! ({os.path.getsize(fallback):,} bytes)", flush=True)

if __name__ == "__main__":
    build_pdf()
