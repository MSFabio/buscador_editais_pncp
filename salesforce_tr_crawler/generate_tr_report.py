import json
import os
from pathlib import Path
import datetime

BASE_DIR = Path(r"C:\Users\11429149760\.gemini\antigravity\scratch\salesforce_tr_crawler")

def generate_html_report(consolidated_data, output_file):
    now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    total_procs = len(consolidated_data)
    
    # Calculate stats
    with_files_count = sum(1 for d in consolidated_data if d['extraction'].get('has_files'))
    categories_cnt = {}
    metrics_cnt = {}
    products_cnt = {}
    
    for d in consolidated_data:
        an = d['analysis']
        for c in an['categories']:
            categories_cnt[c] = categories_cnt.get(c, 0) + 1
        for m in an['metrics']:
            metrics_cnt[m] = metrics_cnt.get(m, 0) + 1
        for p in an['products']:
            products_cnt[p] = products_cnt.get(p, 0) + 1
            
    json_payload = json.dumps(consolidated_data, ensure_ascii=False)
    
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel de Termos de Referência - Salesforce (PNCP & Compras Públicas)</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-main: #0b0f19;
            --bg-card: #141c2e;
            --bg-card-hover: #1b263e;
            --accent-blue: #00a1e0;
            --accent-cyan: #00e5ff;
            --accent-purple: #7952b3;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --border-color: #1e293b;
            --glass-bg: rgba(20, 28, 46, 0.7);
            --glass-border: rgba(255, 255, 255, 0.08);
            --badge-bg: rgba(0, 161, 224, 0.15);
            --badge-text: #38bdf8;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', sans-serif;
            background-color: var(--bg-main);
            color: var(--text-primary);
            line-height: 1.5;
            padding: 20px;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}

        header {{
            background: linear-gradient(135deg, rgba(0,161,224,0.1) 0%, rgba(121,82,179,0.1) 100%);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 25px;
            backdrop-filter: blur(12px);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }}

        .header-title h1 {{
            font-size: 1.8rem;
            font-weight: 800;
            background: linear-gradient(90deg, #00a1e0, #00e5ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 6px;
        }}

        .header-title p {{
            color: var(--text-secondary);
            font-size: 0.95rem;
        }}

        .badge-live {{
            background: rgba(16, 185, 129, 0.15);
            color: #10b981;
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }}

        .badge-live::before {{
            content: '';
            width: 8px;
            height: 8px;
            background-color: #10b981;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 8px #10b981;
        }}

        /* KPI Grid */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 16px;
            margin-bottom: 25px;
        }}

        .kpi-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 20px;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-2px);
            border-color: var(--accent-blue);
        }}

        .kpi-value {{
            font-size: 2.2rem;
            font-weight: 800;
            color: var(--text-primary);
            margin-bottom: 4px;
        }}

        .kpi-label {{
            font-size: 0.85rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 600;
        }}

        /* Controls & Search */
        .controls-bar {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 14px;
            padding: 18px;
            margin-bottom: 25px;
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            align-items: center;
        }}

        .search-box {{
            flex: 1;
            min-width: 280px;
            position: relative;
        }}

        .search-box input {{
            width: 100%;
            background: #0b0f19;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 12px 16px;
            color: var(--text-primary);
            font-size: 0.95rem;
            outline: none;
            transition: border-color 0.2s ease;
        }}

        .search-box input:focus {{
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 3px rgba(0, 161, 224, 0.15);
        }}

        .filter-select {{
            background: #0b0f19;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 12px 16px;
            color: var(--text-primary);
            font-size: 0.9rem;
            outline: none;
            cursor: pointer;
        }}

        .filter-select:focus {{
            border-color: var(--accent-blue);
        }}

        /* Items Grid */
        .items-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
            gap: 20px;
        }}

        .proc-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
        }}

        .proc-card:hover {{
            border-color: rgba(0, 161, 224, 0.5);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
            transform: translateY(-3px);
        }}

        .proc-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
            gap: 12px;
        }}

        .proc-title {{
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--accent-cyan);
            line-height: 1.3;
        }}

        .proc-uf {{
            background: var(--border-color);
            color: var(--text-secondary);
            font-size: 0.75rem;
            font-weight: 700;
            padding: 4px 8px;
            border-radius: 6px;
            white-space: nowrap;
        }}

        .proc-orgao {{
            font-size: 0.88rem;
            font-weight: 600;
            color: var(--text-primary);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .proc-desc {{
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-bottom: 16px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .tag-group {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 16px;
        }}

        .tag {{
            font-size: 0.75rem;
            padding: 4px 10px;
            border-radius: 8px;
            font-weight: 600;
        }}

        .tag-category {{
            background: rgba(0, 161, 224, 0.15);
            color: #38bdf8;
            border: 1px solid rgba(0, 161, 224, 0.3);
        }}

        .tag-metric {{
            background: rgba(121, 82, 179, 0.15);
            color: #c084fc;
            border: 1px solid rgba(121, 82, 179, 0.3);
        }}

        .tag-product {{
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.3);
        }}

        .proc-footer {{
            border-top: 1px solid var(--border-color);
            padding-top: 14px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .proc-value {{
            font-size: 0.9rem;
            font-weight: 700;
            color: #f59e0b;
        }}

        .btn-detail {{
            background: linear-gradient(90deg, #00a1e0, #0081b3);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 8px 14px;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.2s;
        }}

        .btn-detail:hover {{
            opacity: 0.9;
        }}

        /* Modal */
        .modal-overlay {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(8px);
            display: none;
            justify-content: center;
            align-items: center;
            z-index: 1000;
            padding: 20px;
        }}

        .modal-body {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            max-width: 900px;
            width: 100%;
            max-height: 85vh;
            overflow-y: auto;
            padding: 30px;
            position: relative;
            color: var(--text-primary);
        }}

        .modal-close {{
            position: absolute;
            top: 20px;
            right: 20px;
            background: var(--border-color);
            color: var(--text-secondary);
            border: none;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            font-size: 1.2rem;
            cursor: pointer;
        }}

        .modal-title {{
            font-size: 1.4rem;
            font-weight: 800;
            color: var(--accent-cyan);
            margin-bottom: 10px;
        }}

        .modal-section {{
            margin-top: 20px;
            padding-top: 15px;
            border-top: 1px solid var(--border-color);
        }}

        .modal-section h4 {{
            color: var(--accent-blue);
            font-size: 0.95rem;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .text-box {{
            background: #0b0f19;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 16px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.82rem;
            white-space: pre-wrap;
            max-height: 300px;
            overflow-y: auto;
            color: #cbd5e1;
        }}

        .file-link {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(0, 161, 224, 0.1);
            color: var(--accent-cyan);
            border: 1px solid rgba(0, 161, 224, 0.2);
            padding: 8px 12px;
            border-radius: 8px;
            text-decoration: none;
            font-size: 0.85rem;
            margin-right: 10px;
            margin-bottom: 10px;
        }}

        .file-link:hover {{
            background: rgba(0, 161, 224, 0.2);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="header-title">
                <h1>Varredura de Termos de Referência Salesforce</h1>
                <p>Monitoramento e Inteligência de Processos de Contratação e Licitações no Setor Público (PNCP)</p>
            </div>
            <div>
                <span class="badge-live">Varredura Atualizada ({now_str})</span>
            </div>
        </header>

        <!-- KPI Grid -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-value">{total_procs}</div>
                <div class="kpi-label">Processos Encontrados</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{with_files_count}</div>
                <div class="kpi-label">Com Anexos/TRs Baixados</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{len(categories_cnt)}</div>
                <div class="kpi-label">Categorias Identificadas</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{len(products_cnt)}</div>
                <div class="kpi-label">Produtos Salesforce Mencionados</div>
            </div>
        </div>

        <!-- Controls & Search -->
        <div class="controls-bar">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Pesquisar por órgão, objeto, produto, número do edital..." onkeyup="filterCards()">
            </div>
            <select class="filter-select" id="categoryFilter" onchange="filterCards()">
                <option value="">Todas as Categorias</option>
                {"".join([f'<option value="{c}">{c} ({cnt})</option>' for c, cnt in categories_cnt.items()])}
            </select>
            <select class="filter-select" id="metricFilter" onchange="filterCards()">
                <option value="">Todas as Métricas</option>
                {"".join([f'<option value="{m}">{m} ({cnt})</option>' for m, cnt in metrics_cnt.items()])}
            </select>
        </div>

        <!-- Items Grid -->
        <div class="items-grid" id="itemsGrid">
            <!-- Rendered via JS -->
        </div>
    </div>

    <!-- Modal -->
    <div class="modal-overlay" id="detailModal">
        <div class="modal-body">
            <button class="modal-close" onclick="closeModal()">✕</button>
            <div id="modalContent"></div>
        </div>
    </div>

    <script>
        const processesData = {json_payload};

        function renderCards(data) {{
            const container = document.getElementById('itemsGrid');
            container.innerHTML = '';

            if (data.length === 0) {{
                container.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-secondary);">Nenhum processo encontrado com os filtros aplicados.</div>';
                return;
            }}

            data.forEach((item, index) => {{
                const an = item.analysis;
                const extraction = item.extraction;

                const tagsHtml = [
                    ...an.categories.map(c => `<span class="tag tag-category">${{c}}</span>`),
                    ...an.metrics.map(m => `<span class="tag tag-metric">${{m}}</span>`),
                    ...an.products.map(p => `<span class="tag tag-product">${{p}}</span>`)
                ].join('');

                const cardHtml = `
                    <div class="proc-card">
                        <div>
                            <div class="proc-header">
                                <div class="proc-title">${{item.title || 'Edital'}}</div>
                                <div class="proc-uf">${{item.uf || 'BR'}}</div>
                            </div>
                            <div class="proc-orgao">🏢 ${{item.orgao_nome || 'Órgão Desconhecido'}}</div>
                            <div class="proc-desc">${{an.summary_snippet || item.description || ''}}</div>
                            <div class="tag-group">${{tagsHtml}}</div>
                        </div>
                        <div class="proc-footer">
                            <div class="proc-value">💰 ${{an.valor_str}}</div>
                            <button class="btn-detail" onclick="openModal(${{index}})">Ver Detalhes / TR</button>
                        </div>
                    </div>
                `;
                container.innerHTML += cardHtml;
            }});
        }}

        function filterCards() {{
            const search = document.getElementById('searchInput').value.toLowerCase();
            const cat = document.getElementById('categoryFilter').value;
            const met = document.getElementById('metricFilter').value;

            const filtered = processesData.filter(item => {{
                const matchSearch = !search || 
                    (item.title && item.title.toLowerCase().includes(search)) ||
                    (item.orgao_nome && item.orgao_nome.toLowerCase().includes(search)) ||
                    (item.description && item.description.toLowerCase().includes(search)) ||
                    (item.numero_controle_pncp && item.numero_controle_pncp.toLowerCase().includes(search));

                const matchCat = !cat || item.analysis.categories.includes(cat);
                const matchMet = !met || item.analysis.metrics.includes(met);

                return matchSearch && matchCat && matchMet;
            }});

            renderCards(filtered);
        }}

        function openModal(index) {{
            const item = processesData[index];
            const an = item.analysis;
            const ext = item.extraction;

            let filesHtml = '';
            if (ext.downloaded_files && ext.downloaded_files.length > 0) {{
                filesHtml = ext.downloaded_files.map(f => 
                    `<a class="file-link" href="${{f.url}}" target="_blank">📄 ${{f.title}} (${{f.type}})</a>`
                ).join('');
            }} else {{
                filesHtml = '<p style="color: var(--text-secondary); font-size: 0.9rem;">Nenhum anexo PDF/DOCX disponível diretamente para download nesta entrada PNCP.</p>';
            }}

            const certsHtml = an.certifications.length > 0 ? 
                an.certifications.map(c => `<span class="tag tag-metric">${{c}}</span>`).join(' ') : 
                '<span style="color: var(--text-secondary); font-size: 0.9rem;">Nenhuma exigência explícita de certificação mapeada no resumo inicial.</span>';

            const modalHtml = `
                <div class="modal-title">${{item.title}}</div>
                <p style="color: var(--text-secondary); margin-bottom: 15px;"><strong>Órgão:</strong> ${{item.orgao_nome}} | <strong>UF:</strong> ${{item.uf}} - ${{item.municipio_nome}}</p>
                <p style="color: var(--text-secondary); margin-bottom: 15px;"><strong>Número de Controle PNCP:</strong> ${{item.numero_controle_pncp || 'N/A'}}</p>

                <div class="modal-section">
                    <h4>Objeto Completo</h4>
                    <p style="font-size: 0.95rem; line-height: 1.6;">${{item.description || 'Sem descrição.'}}</p>
                </div>

                <div class="modal-section">
                    <h4>Modelos e Métricas</h4>
                    <p style="margin-bottom: 8px;"><strong>Categorias:</strong> ${{an.categories.join(', ')}}</p>
                    <p style="margin-bottom: 8px;"><strong>Unidades de Medida / Métrica:</strong> ${{an.metrics.join(', ')}}</p>
                    <p style="margin-bottom: 8px;"><strong>Produtos Salesforce:</strong> ${{an.products.join(', ')}}</p>
                    <p style="margin-bottom: 8px;"><strong>Valor Estimado:</strong> ${{an.valor_str}}</p>
                </div>

                <div class="modal-section">
                    <h4>Certificações Solicitadas no Escopo</h4>
                    <div>${{certsHtml}}</div>
                </div>

                <div class="modal-section">
                    <h4>Documentos e Anexos (Termos de Referência / Editais)</h4>
                    <div>${{filesHtml}}</div>
                </div>

                <div class="modal-section">
                    <h4>Extrato de Texto Extraído dos Arquivos</h4>
                    <div class="text-box">${{ext.full_extracted_text || 'Sem texto extraído.'}}</div>
                </div>
            `;

            document.getElementById('modalContent').innerHTML = modalHtml;
            document.getElementById('detailModal').style.display = 'flex';
        }}

        function closeModal() {{
            document.getElementById('detailModal').style.display = 'none';
        }}

        // Initial render
        renderCards(processesData);
    </script>
</body>
</html>
"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"[REPORT HTML] Gerado em {output_file}")

def generate_markdown_summary(consolidated_data, output_file):
    now_str = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    total = len(consolidated_data)
    
    md_lines = [
        "# Resumo Executivo - Termos de Referência Salesforce",
        f"**Data da Varredura:** {now_str}  ",
        f"**Total de Processos Identificados:** {total}  ",
        "",
        "---",
        "",
        "## Visão Geral dos Processos Licitatórios Encontrados",
        "",
        "| Órgão / Entidade | Edital / Processo | UF | Categoria | Métrica de Contratação | Valor Estimado | Anexos |",
        "| :--- | :--- | :---: | :--- | :--- | :--- | :---: |"
    ]
    
    for item in consolidated_data:
        orgao = (item.get('orgao_nome') or 'Desconhecido')[:35]
        title = item.get('title') or 'Edital'
        uf = item.get('uf') or 'BR'
        an = item['analysis']
        cat = ", ".join(an['categories'])
        metric = ", ".join(an['metrics'])
        valor = an['valor_str']
        has_files = "✅ Sim" if item['extraction'].get('has_files') else "❌ Não"
        
        md_lines.append(f"| {orgao} | {title} | {uf} | {cat} | {metric} | {valor} | {has_files} |")
        
    md_lines.extend([
        "",
        "---",
        "",
        "## Detalhamento dos Principais Casos Encontrados",
        ""
    ])
    
    for idx, item in enumerate(consolidated_data, 1):
        an = item['analysis']
        ext = item['extraction']
        md_lines.extend([
            f"### {idx}. {item.get('title')} - {item.get('orgao_nome')}",
            f"- **Número de Controle PNCP:** `{item.get('numero_controle_pncp') or 'N/A'}`",
            f"- **Localização:** {item.get('municipio_nome', 'N/A')} - {item.get('uf', 'BR')}",
            f"- **Categorias:** {', '.join(an['categories'])}",
            f"- **Métricas:** {', '.join(an['metrics'])}",
            f"- **Produtos:** {', '.join(an['products'])}",
            f"- **Valor Estimado:** {an['valor_str']}",
            f"- **Objeto:** {item.get('description') or 'Sem descrição'}",
            ""
        ])
        if ext.get('downloaded_files'):
            md_lines.append("**Arquivos Anexos:**")
            for f in ext['downloaded_files']:
                md_lines.append(f"- [{f['title']}]({f['url']}) ({f['type']})")
            md_lines.append("")
            
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_lines))
    print(f"[SUMMARY MD] Gerado em {output_file}")
