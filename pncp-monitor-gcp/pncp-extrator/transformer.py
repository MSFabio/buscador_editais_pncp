"""
Transforma o JSON bruto da API do PNCP em um payload leve e otimizado
para consumo pelo Gemini (economia de tokens).
"""

from datetime import datetime


def transformar_edital(edital_bruto: dict) -> dict | None:
    """
    Extrai apenas os campos semanticamente relevantes de um edital.
    Retorna None se o edital não atender aos critérios mínimos.
    """
    controle = edital_bruto.get("numeroControlePNCP")
    objeto = edital_bruto.get("objetoCompra", "").strip()

    if not controle or not objeto:
        return None

    # Filtro temporal: apenas editais com abertura futura
    data_abertura_str = (
        edital_bruto.get("dataAberturaProposta")
        or edital_bruto.get("dataHoraAberturaLicitacao")
    )
    if data_abertura_str:
        try:
            dt_abertura = datetime.fromisoformat(data_abertura_str[:19])
            if dt_abertura < datetime.now():
                return None
        except (ValueError, TypeError):
            pass

    orgao_info = edital_bruto.get("orgaoEntidade", {})

    return {
        "id": controle,
        "objeto": objeto,
        "infoComplementar": (
            edital_bruto.get("informacaoComplementar", "") or ""
        )[:500],
        "orgao": orgao_info.get("razaoSocial", ""),
        "uf": orgao_info.get("ufSigla", ""),
        "municipio": edital_bruto.get("municipioNome", ""),
        "modalidade": edital_bruto.get("modalidadeNome", ""),
        "valorEstimado": edital_bruto.get("valorTotalEstimado"),
        "dataAbertura": data_abertura_str,
        "dataSessao": edital_bruto.get("dataEncerramentoProposta"),
        "linkPncp": _montar_link_pncp(controle, orgao_info.get("cnpj")),
    }


def _montar_link_pncp(controle: str, cnpj: str | None) -> str:
    """Monta o link direto para o edital no portal PNCP."""
    try:
        parts = controle.split("-")
        seq = int(parts[2].split("/")[0])
        ano = parts[2].split("/")[1]
        return f"https://pncp.gov.br/app/editais/{cnpj}/{ano}/{seq}"
    except (IndexError, ValueError):
        return f"https://pncp.gov.br/app/editais/visualizar?controle={controle}"
