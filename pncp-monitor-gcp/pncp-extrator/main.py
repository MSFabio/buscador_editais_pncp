"""
Entrypoint do Cloud Run Job para extração de editais do PNCP.
Consome a API, transforma os dados e publica no Pub/Sub.

Variáveis de ambiente:
  GCP_PROJECT_ID: ID do projeto GCP (obrigatório para Pub/Sub)
  MAX_PAGINAS: Limite de páginas a consultar (padrão: 100)
  MODO_LOCAL: Se 'true', salva lotes em arquivos locais em vez de Pub/Sub
"""

import logging
import os
import sys

from pncp_client import PNCPClient
from transformer import transformar_edital

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s"
)
logger = logging.getLogger("pncp-extrator")

PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "")
MAX_PAGINAS = int(os.environ.get("MAX_PAGINAS", "100"))
MODO_LOCAL = os.environ.get("MODO_LOCAL", "true").lower() == "true"


def criar_publisher():
    """Cria o publisher adequado baseado no modo de execução."""
    if MODO_LOCAL:
        from publisher import LocalPublisher
        logger.info("Modo LOCAL ativo. Lotes serão salvos em ./output/")
        return LocalPublisher(output_dir="./output")
    else:
        from publisher import EditalPublisher
        if not PROJECT_ID:
            logger.error("GCP_PROJECT_ID não configurado!")
            sys.exit(1)
        logger.info(f"Modo GCP ativo. Publicando no Pub/Sub do projeto '{PROJECT_ID}'")
        return EditalPublisher(project_id=PROJECT_ID)


def main():
    logger.info("=" * 60)
    logger.info("PNCP Extrator - Inicio da execucao")
    logger.info("=" * 60)

    client = PNCPClient(tamanho_pagina=50, delay=1.5)
    publisher = criar_publisher()

    total_extraidos = 0
    total_publicados = 0
    lote_acumulado = []

    def callback_progresso(pagina, total):
        logger.info(f"Progresso: Pagina {pagina}/{total}")

    try:
        for lote_bruto in client.buscar_todas_propostas_abertas(
            max_paginas=MAX_PAGINAS,
            callback=callback_progresso
        ):
            for edital_bruto in lote_bruto:
                edital_leve = transformar_edital(edital_bruto)
                if edital_leve:
                    lote_acumulado.append(edital_leve)
                    total_extraidos += 1

                # Publica quando acumular 50 editais
                if len(lote_acumulado) >= 50:
                    total_publicados += publisher.publicar_lote(lote_acumulado)
                    lote_acumulado = []

    except Exception as e:
        logger.error(f"Erro durante a extracao: {e}")

    # Publica o restante
    if lote_acumulado:
        total_publicados += publisher.publicar_lote(lote_acumulado)

    logger.info("=" * 60)
    logger.info(
        f"Extracao finalizada | "
        f"Extraidos: {total_extraidos} | Publicados: {total_publicados}"
    )
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
