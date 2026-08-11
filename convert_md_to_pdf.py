import os
import json
import re
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

# Files
md_file = r'C:\Users\11429149760\.gemini\antigravity\brain\001766fb-0fab-4892-bf1e-723cc736a97c\editais_pncp_25paginas_bahia.md'
pdf_file = r'C:\Users\11429149760\.gemini\antigravity\brain\001766fb-0fab-4892-bf1e-723cc736a97c\editais_pncp_25paginas_bahia.pdf'
json_file = r'C:\Users\11429149760\.gemini\antigravity\scratch\expanded_25pages_results.json'

with open(json_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

ba_items = data.get('bahia', [])

# Separate Pregão vs Others
ba_pregao = [i for i in ba_items if 'pregão' in (i.get('modalidade') or '').lower() or 'pregao' in (i.get('modalidade') or '').lower()]
ba_outros = [i for i in ba_items if i not in ba_pregao]

class NumberedCanvas(canvas.Canvas):
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
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header (pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 810, "PNCP - Editais Abertos na Bahia (BA)")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(36, 802, 559, 802)
        
        # Footer
        footer_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(559, 20, footer_text)
        self.drawString(36, 20, "Relatório Gerado em 06/08/2026 — Portal Nacional de Contratações Públicas (PNCP)")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(36, 30, 559, 30)
        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        pdf_file,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#0f172a") # dark slate
    brand_blue = colors.HexColor("#1e40af") # royal blue
    accent_green = colors.HexColor("#166534") # forest green
    bg_card = colors.HexColor("#f8fafc")
    border_card = colors.HexColor("#e2e8f0")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=brand_blue,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=15
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'Heading3_Custom',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=brand_blue,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#1e293b")
    )

    badge_pregao_style = ParagraphStyle(
        'BadgePregao',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#b91c1c") # red bold for Pregão
    )

    label_style = ParagraphStyle(
        'Label_Custom',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=primary_color
    )

    story = []

    # Title Banner
    story.append(Paragraph("📋 Editais Abertos PNCP — Estado da Bahia (BA)", title_style))
    meta_text = (
        "<b>Data da Busca:</b> 06/08/2026 &nbsp;|&nbsp; "
        "<b>Profundidade:</b> 25 páginas por termo de busca &nbsp;|&nbsp; "
        "<b>Filtro:</b> Sessão Pública Futura<br/>"
        "<b>Termos Pesquisados (8):</b> Buffet, Buffet para eventos, Buffet para cerimônias, Catering, Alimentação, Alimentação para eventos, Coffee Break, Lanches"
    )
    story.append(Paragraph(meta_text, subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=brand_blue, spaceAfter=12))

    # Executive Summary Card
    summary_html = f"""
    <b>Total de Editais Únicos na Bahia:</b> {len(ba_items)} editais<br/>
    <b>• Modalidade Pregão (Eletrônico/Presencial):</b> {len(ba_pregao)} editais<br/>
    <b>• Demais Modalidades (Credenciamento / Dispensa):</b> {len(ba_outros)} editais
    """
    summary_p = Paragraph(summary_html, body_style)
    summary_table = Table([[summary_p]], colWidths=[523])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#eff6ff")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#bfdbfe")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 14))

    # Section 1: Pregões na Bahia
    story.append(Paragraph("⚡ 1. Editais na Modalidade Pregão na Bahia (BA)", h2_style))
    story.append(Paragraph("Oportunidades em Pregão Eletrônico/Presencial com sessão pública agendada:", subtitle_style))

    def make_item_card(item, idx, is_pregao=False):
        orgao = item.get('orgao') or 'Não informado'
        unidade = item.get('unidade') or ''
        muni = item.get('municipio') or 'Bahia'
        title = item.get('title') or f"Edital {item.get('control_num')}"
        modalidade = item.get('modalidade') or 'Pregão Eletrônico'
        objeto = (item.get('objeto') or 'Sem descrição.').strip()
        
        val = item.get('valor_estimado')
        val_str = f"R$ {float(val):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if (val and val > 0) else "Não informado / Sigiloso"
        
        dt_pub = item.get('data_publicacao', '')[:10] if item.get('data_publicacao') else 'N/A'
        dt_enc = item.get('data_encerramento_proposta', '')[:16].replace('T', ' às ') if item.get('data_encerramento_proposta') else 'N/A'
        
        terms_str = ", ".join(item.get('matched_terms', []))
        link_pncp = item.get('link_pncp')
        link_origem = item.get('link_origem')

        header_title = f"{idx}. {title} — {orgao}"
        
        link_html = ""
        if link_pncp:
            link_html += f'<a href="{link_pncp}"><font color="#1d4ed8"><u>Ver Edital no Portal PNCP</u></font></a>'
        if link_origem:
            if link_html:
                link_html += " &nbsp;|&nbsp; "
            link_html += f'<a href="{link_origem}"><font color="#0f766e"><u>Sistema de Origem</u></font></a>'

        mod_color = "#b91c1c" if is_pregao else "#1e3a8a"

        card_html = f"""
        <font size="10" color="{brand_blue}"><b>{header_title}</b></font><br/>
        <b>Município / UF:</b> {muni} - BA &nbsp;|&nbsp; <b>Modalidade:</b> <font color="{mod_color}"><b>{modalidade}</b></font><br/>
        <b>Termos Relacionados:</b> <font color="#475569">{terms_str}</font><br/>
        <b>Valor Estimado:</b> {val_str} &nbsp;|&nbsp; <b>Sessão Pública / Encerramento:</b> <font color="#b91c1c"><b>{dt_enc}</b></font><br/>
        <b>Objeto:</b> {objeto}<br/>
        <b>Links Úteis:</b> {link_html}
        """
        p_card = Paragraph(card_html, body_style)
        
        bg_c = colors.HexColor("#fef2f2") if is_pregao else bg_card
        border_c = colors.HexColor("#fca5a5") if is_pregao else border_card

        t = Table([[p_card]], colWidths=[523])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), bg_c),
            ('BOX', (0,0), (-1,-1), 0.8, border_c),
            ('PADDING', (0,0), (-1,-1), 7),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        return t

    for idx, item in enumerate(ba_pregao, 1):
        story.append(make_item_card(item, idx, is_pregao=True))
        story.append(Spacer(1, 8))

    story.append(Spacer(1, 10))

    # Section 2: Credenciamentos e Outras Modalidades
    story.append(Paragraph("📜 2. Demais Editais Abertos na Bahia (Credenciamento, Dispensa, etc.)", h2_style))
    story.append(Paragraph(f"Total de {len(ba_outros)} oportunidades em Credenciamento e Dispensa de Licitação:", subtitle_style))

    for idx, item in enumerate(ba_outros, 1):
        story.append(make_item_card(item, idx, is_pregao=False))
        story.append(Spacer(1, 8))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF successfully created: {pdf_file}")

if __name__ == '__main__':
    build_pdf()
