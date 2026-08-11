"""
Módulo de filtros e cálculo de relevância para editais do PNCP.
Implementa normalização de texto, scoring por palavras-chave e filtragem.
"""

import re
import unicodedata
from typing import Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Lista de stop words e termos burocráticos de licitação para focar no contexto real
STOP_WORDS_PT = [
    # Stop words comuns em português
    "de", "a", "o", "que", "e", "do", "da", "em", "um", "para", "com", "na", "no", "uma", "os", "as", "dos", "das",
    "se", "por", "mais", "ao", "aos", "como", "mas", "ele", "ela", "nos", "sua", "seu", "seus", "suas", "pelo", "pela",
    # Termos burocráticos de editais (ruído contextual)
    "contratacao", "aquisicao", "prestacao", "servico", "servicos", "empresa", "especializada", "fornecimento", 
    "objeto", "licitacao", "edital", "registro", "precos", "orgao", "secretaria", "municipal", "estadual", 
    "atendimento", "destinados", "destinadas", "visando", "futura", "eventual", "solucao", "solucoes"
]


def calcular_similaridade_contexto(objeto: str, info_complementar: str, contexto_negocio: str) -> float:
    """
    Calcula a similaridade de cosseno entre o edital e o contexto do negócio
    utilizando representação vetorial TF-IDF com bigramas e remoção de stop words.
    
    Args:
        objeto: Descrição do objeto do edital.
        info_complementar: Informações complementares do edital.
        contexto_negocio: Descrição textual do negócio cadastrado na busca.
        
    Returns:
        Similaridade de cosseno como float entre 0.0 e 1.0.
    """
    if not contexto_negocio or not (objeto or info_complementar):
        return 0.0

    # Normaliza e limpa os textos
    contexto_norm = normalizar_texto(contexto_negocio)
    
    # Combina as informações do edital dando mais ênfase ao objeto
    edital_texto = f"{objeto or ''} {objeto or ''} {info_complementar or ''}"
    edital_norm = normalizar_texto(edital_texto)

    if not edital_norm or not contexto_norm:
        return 0.0

    try:
        # TF-IDF com bigramas e remoção de ruídos de edital
        vectorizer = TfidfVectorizer(
            stop_words=STOP_WORDS_PT,
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        
        tfidf = vectorizer.fit_transform([contexto_norm, edital_norm])
        similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]
        return float(similarity)
    except Exception:
        # Em caso de falha de vocabulário ou vetores vazios
        return 0.0


def normalizar_texto(texto: str) -> str:
    """
    Normaliza texto para comparação: remove acentos, converte para minúsculas
    e normaliza espaços em branco.
    
    Args:
        texto: Texto original a ser normalizado.
        
    Returns:
        Texto normalizado sem acentos, em minúsculas e com espaços simples.
    """
    if not texto:
        return ''

    # Remove acentos usando decomposição Unicode (NFD) e filtrando marcas diacríticas
    texto_nfkd = unicodedata.normalize('NFKD', texto)
    texto_sem_acentos = ''.join(
        char for char in texto_nfkd
        if not unicodedata.combining(char)
    )

    # Converte para minúsculas
    texto_lower = texto_sem_acentos.lower()

    # Normaliza espaços: substitui múltiplos espaços/tabs/newlines por espaço único
    texto_normalizado = re.sub(r'\s+', ' ', texto_lower).strip()

    return texto_normalizado


def calcular_relevancia(edital: dict, palavras_chave: list[str]) -> float:
    """
    Calcula o score de relevância de um edital com base nas palavras-chave.
    
    O score é calculado considerando:
    - Campo 'objetoCompra': peso 2x (mais relevante)
    - Campo 'informacaoComplementar': peso 1x
    
    Args:
        edital: Dicionário com os dados do edital da API do PNCP.
        palavras_chave: Lista de palavras-chave para buscar.
        
    Returns:
        Score de relevância entre 0.0 e 1.0.
    """
    if not palavras_chave:
        return 0.0

    # Normaliza os textos do edital para comparação
    objeto_compra = normalizar_texto(edital.get('objetoCompra', '') or '')
    info_complementar = normalizar_texto(edital.get('informacaoComplementar', '') or '')

    # Pesos dos campos
    peso_objeto = 2.0
    peso_info = 1.0

    # Score total possível: cada palavra-chave pode pontuar nos dois campos
    total_possivel = len(palavras_chave) * (peso_objeto + peso_info)

    if total_possivel == 0:
        return 0.0

    score_obtido = 0.0

    for palavra in palavras_chave:
        palavra_normalizada = normalizar_texto(palavra)
        if not palavra_normalizada:
            continue

        # Verifica presença no objeto da compra (peso 2x)
        if palavra_normalizada in objeto_compra:
            score_obtido += peso_objeto

        # Verifica presença na informação complementar (peso 1x)
        if palavra_normalizada in info_complementar:
            score_obtido += peso_info

    return round(score_obtido / total_possivel, 4)


def filtrar_editais(
    editais: list[dict],
    palavras_chave: list[str],
    score_minimo: float = 0.1,
) -> list[dict]:
    """
    Filtra editais por palavras-chave, retornando apenas aqueles acima do score mínimo.
    
    Cada edital retornado recebe uma chave '_score' com o valor de relevância calculado.
    A lista é ordenada por score decrescente (mais relevante primeiro).
    
    Args:
        editais: Lista de dicionários com dados dos editais da API.
        palavras_chave: Lista de palavras-chave para filtrar.
        score_minimo: Score mínimo de relevância (0.0 a 1.0). Padrão: 0.1.
        
    Returns:
        Lista de editais filtrados e ordenados por relevância, com chave '_score' adicionada.
    """
    if not editais or not palavras_chave:
        return []

    # Limpa palavras-chave vazias
    palavras_limpas = [p.strip() for p in palavras_chave if p.strip()]
    if not palavras_limpas:
        return []

    editais_relevantes = []

    for edital in editais:
        score = calcular_relevancia(edital, palavras_limpas)

        if score >= score_minimo:
            edital_com_score = dict(edital)  # Cria cópia para não modificar o original
            edital_com_score['_score'] = score
            editais_relevantes.append(edital_com_score)

    # Ordena por score decrescente (mais relevante primeiro)
    editais_relevantes.sort(key=lambda e: e['_score'], reverse=True)

    return editais_relevantes
