import csv
from pathlib import Path

folder = Path(r'C:\Users\11429149760\Desktop\pregões - pesquisa de preços - renovação K2')
md_file = folder / 'PLANILHA_DE_ORCAMENTO_LINK_LOTE_III_PDF.md'
csv_file = folder / 'PLANILHA_DE_ORCAMENTO_LINK_LOTE_III.csv'

itens = [
    {
        'velocidade': '80 MBPS',
        'qtd': 154,
        'k2': 'R$ 568,0000',
        'gstn': 'R$ 99,9000',
        'codevasf': '-',
        'mpes': 'R$ 1.208,0300',
        'mjsp': '-',
        'mte': '-',
        'spa': '-',
        'ifma': '-',
        'fupesc': '-',
        'jmrs': '-',
        'anac': '-',
        'casa_civil': '-',
        'pmdf': '-',
        'canapolis': '-',
        'media_unit': 'R$ 653,9650',
        'media_mensal': 'R$ 100.710,6100',
        'mediana_unit': 'R$ 653,9650',
        'mediana_mensal': 'R$ 100.710,6100'
    },
    {
        'velocidade': '100 MBPS',
        'qtd': 7,
        'k2': 'R$ 637,4900',
        'gstn': 'R$ 129,9000',
        'codevasf': '-',
        'mpes': 'R$ 823,9000',
        'mjsp': 'R$ 314,0100',
        'mte': 'R$ 7.007,1800',
        'spa': 'R$ 180,0000',
        'ifma': 'R$ 600,0000',
        'fupesc': 'R$ 1.148,0000',
        'jmrs': 'R$ 1.200,0000',
        'anac': '-',
        'casa_civil': '-',
        'pmdf': '-',
        'canapolis': '-',
        'media_unit': 'R$ 1.425,3738',
        'media_mensal': 'R$ 9.977,6163',
        'mediana_unit': 'R$ 711,9500',
        'mediana_mensal': 'R$ 4.983,6500'
    },
    {
        'velocidade': '150 MBPS',
        'qtd': 115,
        'k2': 'R$ 756,0000',
        'gstn': 'R$ 139,9000',
        'codevasf': '-',
        'mpes': 'R$ 1.703,7700',
        'mjsp': '-',
        'mte': '-',
        'spa': '-',
        'ifma': '-',
        'fupesc': '-',
        'jmrs': 'R$ 2.400,0000',
        'anac': '-',
        'casa_civil': '-',
        'pmdf': '-',
        'canapolis': '-',
        'media_unit': 'R$ 1.414,5567',
        'media_mensal': 'R$ 162.674,0167',
        'mediana_unit': 'R$ 1.703,7700',
        'mediana_mensal': 'R$ 195.933,5500'
    },
    {
        'velocidade': '200 MBPS',
        'qtd': 41,
        'k2': 'R$ 860,1000',
        'gstn': 'R$ 159,9000',
        'codevasf': 'R$ 770,1300',
        'mpes': 'R$ 800,0000',
        'mjsp': 'R$ 471,0000',
        'mte': '-',
        'spa': '-',
        'ifma': '-',
        'fupesc': '-',
        'jmrs': '-',
        'anac': 'R$ 3.962,2500',
        'casa_civil': '-',
        'pmdf': 'R$ 520,0000',
        'canapolis': 'R$ 1.000,0000',
        'media_unit': 'R$ 1.097,6114',
        'media_mensal': 'R$ 45.002,0686',
        'mediana_unit': 'R$ 770,1300',
        'mediana_mensal': 'R$ 31.575,3300'
    },
    {
        'velocidade': '300 MBPS',
        'qtd': 9,
        'k2': 'R$ 980,9000',
        'gstn': 'R$ 199,9000',
        'codevasf': '-',
        'mpes': '-',
        'mjsp': '-',
        'mte': 'R$ 8.250,5100',
        'spa': '-',
        'ifma': '-',
        'fupesc': '-',
        'jmrs': '-',
        'anac': '-',
        'casa_civil': 'R$ 5.671,8400',
        'pmdf': '-',
        'canapolis': 'R$ 1.024,3700',
        'media_unit': 'R$ 3.786,6550',
        'media_mensal': 'R$ 34.079,8950',
        'mediana_unit': 'R$ 3.348,1050',
        'mediana_mensal': 'R$ 30.132,9450'
    }
]

totais_30_meses = {
    'k2': 'R$ 6.688.998,9000',
    'gstn': 'R$ 1.222.122,0000',
    'codevasf': 'R$ 947.259,9000',
    'mpes': 'R$ 12.616.124,1000',
    'mjsp': 'R$ 645.272,1000',
    'mte': 'R$ 3.699.145,5000',
    'spa': 'R$ 37.800,0000',
    'ifma': 'R$ 126.000,0000',
    'fupesc': 'R$ 241.080,0000',
    'jmrs': 'R$ 8.532.000,0000',
    'anac': 'R$ 4.873.567,5000',
    'casa_civil': 'R$ 1.531.396,8000',
    'pmdf': 'R$ 639.600,0000',
    'canapolis': 'R$ 1.506.579,9000',
    'media_total': 'R$ 10.573.326,1900',
    'mediana_total': 'R$ 10.900.082,5500'
}

# Gerar Markdown
md = []
md.append('# PLANILHA DE ORÇAMENTOS - PESQUISA DE PREÇOS')
md.append('**Processo:** E-20/001.001992/2024  ')
md.append('**Objeto:** Contratação de Links com Serviço SD-WAN - Link Assimétrico de Acesso à Internet - **LOTE III**  ')
md.append('**Lote:** 3 | **Item:** 1 | **Unidade de Medida (U.M):** UNID.  \n')

md.append('## 1. Resumo Executivo: Médias e Medianas por Velocidade\n')
md.append('| Item | Velocidade | Qtd (Links) | Média Unitária | Média Mensal (Total) | Mediana Unitária | Mediana Mensal (Total) |')
md.append('| :---: | :---: | :---: | :---: | :---: | :---: | :---: |')
for idx, it in enumerate(itens, 1):
    md.append(f"| {idx} | {it['velocidade']} | {it['qtd']} | {it['media_unit']} | {it['media_mensal']} | {it['mediana_unit']} | {it['mediana_mensal']} |")
md.append('| **TOTAL** | **326 Links** | **326** | -- | **R$ 352.444,21** | -- | **R$ 363.336,09** |\n')

md.append('## 2. Tabela Completa de Preços Unitários por Fornecedor / Órgão Público\n')
cols = ['Velocidade', 'Qtd', 'K2 Telecom (Atual)', 'GSTN Telecom', 'CODEVASF', 'MPES', 'MJSP', 'MTE', 'Pref. S. P. Aldeia', 'IFMA', 'FUPESC', 'JMRS', 'ANAC', 'Presidência Casa Civil', 'PMDF', 'Pref. Canápolis']
md.append('| ' + ' | '.join(cols) + ' |')
md.append('| ' + ' | '.join([':---:'] * len(cols)) + ' |')

keys = ['k2', 'gstn', 'codevasf', 'mpes', 'mjsp', 'mte', 'spa', 'ifma', 'fupesc', 'jmrs', 'anac', 'casa_civil', 'pmdf', 'canapolis']
for it in itens:
    vals = [it['velocidade'], str(it['qtd'])] + [it[k] for k in keys]
    md.append('| ' + ' | '.join(vals) + ' |')

tot_vals = ['**Total 30 meses**', '--'] + [totais_30_meses[k] for k in keys]
md.append('| ' + ' | '.join(tot_vals) + ' |\n')

md.append('## 3. Estimativa Global para Contrato de 30 Meses\n')
md.append('- **Valor Total Estimado pela Média (30 meses):** R$ 10.573.326,19')
md.append('- **Valor Total Estimado pela Mediana (30 meses):** R$ 10.900.082,55')
md.append('- **Valor Total K2 Telecom (Atual Contratada - 30 meses):** R$ 6.688.998,90\n')

md.append('## 4. Observações\n')
md.append('> **Nota:** O PREGÃO 02/2026 (JUSTIÇA MILITAR DO ESTADO DO RIO GRANDE DO SUL - RS) está com a soma da velocidade de 100 MBPS + 50 MBPS conforme anexo do pregão.\n')

content_md = '\n'.join(md)
md_file.write_text(content_md, encoding='utf-8')
print('Markdown salvo com sucesso:', md_file.name)

# Gerar CSV
with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(['Lote', 'Item', 'Velocidade', 'Quantidade', 'K2 Telecom', 'GSTN', 'CODEVASF', 'MPES', 'MJSP', 'MTE', 'Pref São Pedro Aldeia', 'IFMA', 'FUPESC', 'JMRS', 'ANAC', 'Casa Civil', 'PMDF', 'Pref Canápolis', 'Média Unitária', 'Média Mensal', 'Mediana Unitária', 'Mediana Mensal'])
    for it in itens:
        writer.writerow(['3', '1', it['velocidade'], it['qtd'], it['k2'], it['gstn'], it['codevasf'], it['mpes'], it['mjsp'], it['mte'], it['spa'], it['ifma'], it['fupesc'], it['jmrs'], it['anac'], it['casa_civil'], it['pmdf'], it['canapolis'], it['media_unit'], it['media_mensal'], it['mediana_unit'], it['mediana_mensal']])
    writer.writerow(['Total 30 meses', '', '', '326', totais_30_meses['k2'], totais_30_meses['gstn'], totais_30_meses['codevasf'], totais_30_meses['mpes'], totais_30_meses['mjsp'], totais_30_meses['mte'], totais_30_meses['spa'], totais_30_meses['ifma'], totais_30_meses['fupesc'], totais_30_meses['jmrs'], totais_30_meses['anac'], totais_30_meses['casa_civil'], totais_30_meses['pmdf'], totais_30_meses['canapolis'], '', totais_30_meses['media_total'], '', totais_30_meses['mediana_total']])

print('CSV salvo com sucesso:', csv_file.name)
