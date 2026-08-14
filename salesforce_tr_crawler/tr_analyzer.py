import re
import json

def is_valid_salesforce_process(item, full_text):
    text_lower = (str(item.get('title', '')) + " " + str(item.get('description', '')) + " " + str(full_text)).lower()
    
    # Core Salesforce Ecosystem Keywords
    sf_core_keywords = [
        'salesforce', 'government cloud', 'service cloud', 'sales cloud', 'marketing cloud', 
        'experience cloud', 'agentforce', 'mulesoft', 'slack', 'tableau', 'tableu',
        'customer 360', 'data 360', 'headless 360'
    ]
    
    has_sf_core = any(k in text_lower for k in sf_core_keywords)
    
    if not has_sf_core:
        return False
        
    # Exclusion rule for false positives (generic Adobe Creative Cloud or generic office supplies without Salesforce)
    if any(ak in text_lower for ak in ['adobe', 'creative cloud', 'photoshop', 'indesign', 'coreldraw']) and not any(k in text_lower for k in ['salesforce', 'mulesoft', 'slack', 'tableau', 'agentforce', 'customer 360', 'data 360']):
        return False
        
    return True

def analyze_salesforce_tr(item, extraction_result):
    desc = item.get('description') or ""
    full_text = extraction_result.get('full_extracted_text') or desc
    text_lower = full_text.lower()
    
    # Check strict validity
    valid = is_valid_salesforce_process(item, full_text)
    if not valid:
        return None # Rejected false positive
        
    # 1. Categorization
    categories = []
    if any(k in text_lower for k in ['subscrição', 'subscricao', 'licença', 'licenca', 'saas', 'subscrições', 'software como serviço']):
        categories.append("Licenciamento / SaaS")
    if any(k in text_lower for k in ['sustentação', 'sustentacao', 'suporte técnico', 'suporte tecnico', 'manutenção', 'manutencao', 'operação assistida', 'operacao assistida', 'ams']):
        categories.append("Sustentação & Suporte (AMS)")
    if any(k in text_lower for k in ['desenvolvimento', 'customização', 'customizacao', 'parametrização', 'parametrizacao', 'integração', 'integracao', 'postos de trabalho', 'apex', 'lwc']):
        categories.append("Desenvolvimento & Customização")
    if any(k in text_lower for k in ['treinamento', 'capacitação', 'capacitacao', 'consultoria', 'transferência de conhecimento']):
        categories.append("Treinamento & Consultoria")
        
    if not categories:
        categories.append("Outros / Serviços Correlatos")
        
    # 2. Metric / Unit of Measurement
    metrics = []
    if any(k in text_lower for k in ['licença', 'licenca', 'subscrição', 'subscricao', 'usuário', 'usuario']):
        metrics.append("Licença / Subscrição")
    if any(k in text_lower for k in ['posto de trabalho', 'postes de trabalho', 'alocação', 'alocacao']):
        metrics.append("Postos de Trabalho / Alocação")
    if any(k in text_lower for k in ['hora', 'horas', 'homem-hora']):
        metrics.append("Horas / HH")
    if any(k in text_lower for k in ['pontos de função', 'pontos de funcao', 'pf']):
        metrics.append("Pontos de Função (PF)")
    if any(k in text_lower for k in ['ust', 'unidade de serviço técnico', 'unidades de serviço']):
        metrics.append("UST (Unidade de Serviço Técnico)")
    if any(k in text_lower for k in ['preço global', 'preco global', 'valor global', 'empreitada integral']):
        metrics.append("Preço Global")
        
    if not metrics:
        metrics.append("Não Especificado / Ver Edital")
        
    # 3. Certifications Search
    certifications_found = []
    cert_keywords = [
        ("Salesforce Certified Administrator", ["certified administrator", "administrador certificado", "administrador salesforce"]),
        ("Salesforce Certified Platform Developer", ["platform developer", "desenvolvedor certificado", "desenvolvedor apex", "developer i", "developer ii"]),
        ("Salesforce Certified App Builder", ["app builder", "platform app builder"]),
        ("Salesforce Certified Technical / Integration Architect", ["architect", "arquiteto salesforce", "integration architect", "system architect"]),
        ("Salesforce Certified Consultant", ["sales cloud consultant", "service cloud consultant", "consultor certificado"]),
        ("Salesforce Certified Marketing Cloud", ["marketing cloud", "marketing cloud email", "marketing cloud developer"])
    ]
    
    for cert_name, keywords in cert_keywords:
        if any(kw in text_lower for kw in keywords):
            certifications_found.append(cert_name)
            
    # 4. Values / Budget
    val_global = item.get('valor_global')
    valor_str = "Não informado"
    
    if val_global is not None and val_global > 0:
        valor_str = f"R$ {val_global:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    else:
        matches = re.findall(r'R\$\s*[\d\.]+(?:,\d{2})?', full_text)
        if matches:
            valor_str = f"Estimado no texto: {matches[0]}"
            
    # 5. Extract Salesforce Specific Ecosystem Products & Terms
    products_found = []
    sf_products = [
        "Salesforce", "Government Cloud", "Sales Cloud", "Service Cloud", "Marketing Cloud", 
        "Experience Cloud", "Commerce Cloud", "MuleSoft", "Tableau", 
        "Slack", "Agentforce", "Customer 360", "Data 360", "Headless 360",
        "CRM Analytics", "Financial Services Cloud", "Health Cloud"
    ]
    for prod in sf_products:
        if prod.lower() in text_lower:
            products_found.append(prod)
            
    if not products_found:
        products_found.append("Salesforce CRM")
        
    # 6. Highlights / Executive Summary
    summary_snippet = desc
    if len(summary_snippet) > 300:
        summary_snippet = summary_snippet[:300] + "..."
        
    return {
        'is_valid': True,
        'categories': categories,
        'metrics': metrics,
        'certifications': certifications_found,
        'products': products_found,
        'valor_str': valor_str,
        'summary_snippet': summary_snippet,
        'text_length': len(full_text)
    }
