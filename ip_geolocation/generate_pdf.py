import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

def create_pdf(file_path, output_pdf):
    print("Lendo os dados da planilha...")
    df = pd.read_excel(file_path)
    
    total_consultas = len(df)
    ips_unicos = df['IP'].nunique() if 'IP' in df.columns else 0
    cidades_unicas = df['Cidade'].nunique() if 'Cidade' in df.columns else 0
    estados_unicos = df['Estado/Região'].nunique() if 'Estado/Região' in df.columns else 0
    
    print("Gerando gráficos...")
    # Configuração visual do matplotlib
    plt.style.use('ggplot')
    
    # Grafico 1: Cidades
    plt.figure(figsize=(10, 5))
    if 'Cidade' in df.columns:
        ax1 = df['Cidade'].value_counts().head(10).plot(kind='bar', color='#FF4B4B')
        for container in ax1.containers:
            ax1.bar_label(container, padding=3)
    plt.title('Cidades com mais acessos', fontsize=14)
    plt.ylabel('Número de Consultas')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('grafico_cidades.png')
    plt.close()
    
    # Grafico 2: Provedores
    plt.figure(figsize=(10, 5))
    if 'Provedor (ISP)' in df.columns:
        ax2 = df['Provedor (ISP)'].value_counts().head(10).plot(kind='bar', color='#0068C9')
        for container in ax2.containers:
            ax2.bar_label(container, padding=3)
    plt.title('ISP (provedores) com mais acessos', fontsize=14)
    plt.ylabel('Número de Consultas')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('grafico_isps.png')
    plt.close()

    print("Montando o documento PDF...")
    # Criando o PDF com FPDF
    class PDF(FPDF):
        def header(self):
            self.set_font('helvetica', 'B', 16)
            # Título principal
            self.cell(0, 10, 'Relatório Analítico de Geolocalização de Acessos', align='C', new_x="LMARGIN", new_y="NEXT")
            self.set_draw_color(0, 0, 0)
            self.line(10, 22, 200, 22)
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font('helvetica', 'I', 8)
            self.cell(0, 10, f'Página {self.page_no()}', align='C')

    pdf = PDF()
    pdf.add_page()
    
    # Seção 1: Métricas
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, '1. Visão Geral', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('helvetica', '', 12)
    pdf.cell(0, 8, f'Total de Consultas: {total_consultas:,}'.replace(',', '.'), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f'Endereços IP Únicos: {ips_unicos:,}'.replace(',', '.'), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f'Cidades Atingidas: {cidades_unicas:,}'.replace(',', '.'), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f'Estados Atingidos: {estados_unicos:,}'.replace(',', '.'), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    # Seção 2: Gráfico de Cidades
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, '2. Cidades com mais acessos', new_x="LMARGIN", new_y="NEXT")
    pdf.image('grafico_cidades.png', x=10, w=190)
    pdf.ln(5)
    
    # Nova página para o segundo gráfico
    pdf.add_page()
    pdf.set_font('helvetica', 'B', 14)
    pdf.cell(0, 10, '3. ISP (provedores) com mais acessos', new_x="LMARGIN", new_y="NEXT")
    pdf.image('grafico_isps.png', x=10, w=190)
    pdf.ln(10)
    
    # Seção 3: Top Motivos
    if 'MOTIVO_CONSULTA' in df.columns:
        pdf.set_font('helvetica', 'B', 14)
        pdf.cell(0, 10, '4. Top 10 Motivos de Consulta', new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('helvetica', '', 11)
        
        motivos = df['MOTIVO_CONSULTA'].value_counts().head(10)
        for motivo, count in motivos.items():
            # encode ascii to avoid character issues or clean up text
            motivo_text = str(motivo).encode('latin-1', 'replace').decode('latin-1')
            pdf.cell(0, 8, f'- {count:,} acessos : {motivo_text}'.replace(',', '.'), new_x="LMARGIN", new_y="NEXT")

    pdf.output(output_pdf)
    print(f"Relatório PDF gerado com sucesso em: {output_pdf}")
    
    # Limpeza de imagens temporárias
    if os.path.exists('grafico_cidades.png'): os.remove('grafico_cidades.png')
    if os.path.exists('grafico_isps.png'): os.remove('grafico_isps.png')

if __name__ == '__main__':
    file_path = r"C:\Users\11429149760\Downloads\Relatório_IPs_Localizados.xlsx"
    output_pdf = r"C:\Users\11429149760\Downloads\Relatorio_Geolocalizacao_Acessos.pdf"
    create_pdf(file_path, output_pdf)
