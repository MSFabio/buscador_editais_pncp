"""
Cliente para a API do Portal Nacional de Contratações Públicas (PNCP).
Implementa chamadas aos endpoints de consulta com retry, rate limiting e paginação.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Callable, Optional

import requests

import config

logger = logging.getLogger(__name__)


class PNCPClient:
    """Cliente HTTP para consultas à API do PNCP."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        tamanho_pagina: Optional[int] = None,
        delay: Optional[float] = None,
        max_retries: Optional[int] = None,
    ):
        self.base_url = base_url or config.PNCP_BASE_URL
        self.tamanho_pagina = tamanho_pagina or config.TAMANHO_PAGINA
        self.delay = delay if delay is not None else config.DELAY_ENTRE_REQUESTS
        self.max_retries = max_retries or config.MAX_RETRIES

        # Utiliza Session para reutilizar conexões (connection pooling)
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'PNCP-Busca-Editais/1.0',
        })

    def _fazer_requisicao(self, endpoint: str, params: dict) -> dict:
        """
        Executa uma requisição GET com retry e backoff exponencial.
        
        Retenta automaticamente em caso de erros 429 (rate limit),
        500, 502 e 503 (erros de servidor).
        
        Args:
            endpoint: Caminho relativo do endpoint da API.
            params: Dicionário de parâmetros de query string.
            
        Returns:
            Dicionário com a resposta JSON da API.
            
        Raises:
            requests.exceptions.HTTPError: Se o erro persistir após todas as tentativas.
        """
        url = f'{self.base_url}{endpoint}'
        erros_retentaveis = (429, 500, 502, 503)

        for tentativa in range(1, self.max_retries + 1):
            try:
                logger.debug(f'Requisição GET {url} | Params: {params} | Tentativa {tentativa}/{self.max_retries}')
                response = self.session.get(url, params=params, timeout=60)

                if response.status_code in erros_retentaveis:
                    tempo_espera = (2 ** tentativa) * 0.5  # Backoff exponencial: 1s, 2s, 4s...
                    logger.warning(
                        f'Erro {response.status_code} na tentativa {tentativa}/{self.max_retries}. '
                        f'Aguardando {tempo_espera:.1f}s antes de retentar...'
                    )
                    time.sleep(tempo_espera)
                    continue

                response.raise_for_status()
                return response.json()

            except requests.exceptions.ConnectionError as e:
                if tentativa < self.max_retries:
                    tempo_espera = (2 ** tentativa) * 0.5
                    logger.warning(
                        f'Erro de conexão na tentativa {tentativa}/{self.max_retries}: {e}. '
                        f'Aguardando {tempo_espera:.1f}s...'
                    )
                    time.sleep(tempo_espera)
                else:
                    logger.error(f'Erro de conexão após {self.max_retries} tentativas: {e}')
                    raise

            except requests.exceptions.Timeout as e:
                if tentativa < self.max_retries:
                    tempo_espera = (2 ** tentativa) * 0.5
                    logger.warning(
                        f'Timeout na tentativa {tentativa}/{self.max_retries}: {e}. '
                        f'Aguardando {tempo_espera:.1f}s...'
                    )
                    time.sleep(tempo_espera)
                else:
                    logger.error(f'Timeout após {self.max_retries} tentativas: {e}')
                    raise

        # Se esgotou as tentativas por erros retentáveis, lança exceção
        raise requests.exceptions.HTTPError(
            f'Erro persistente após {self.max_retries} tentativas para {url}'
        )

    def buscar_propostas_abertas(
        self,
        data_final: Optional[str] = None,
        modalidade: Optional[int] = None,
        uf: Optional[str] = None,
        pagina: int = 1,
    ) -> dict:
        """
        Consulta o endpoint de propostas abertas do PNCP.
        
        Endpoint: GET /v1/contratacoes/proposta
        
        Args:
            data_final: Data final no formato yyyyMMdd. Se não informado, usa hoje + 365 dias.
            modalidade: Código da modalidade de contratação (1-13).
            uf: Sigla da Unidade Federativa (ex: 'SP', 'RJ').
            pagina: Número da página (mínimo 1).
            
        Returns:
            Dicionário com a resposta JSON da API contendo os editais e metadados de paginação.
        """
        if data_final is None:
            data_final = (datetime.now() + timedelta(days=365)).strftime('%Y%m%d')

        params = {
            'dataFinal': data_final,
            'pagina': max(1, pagina),
            'tamanhoPagina': self.tamanho_pagina,
        }

        if modalidade is not None:
            params['codigoModalidadeContratacao'] = modalidade

        if uf is not None:
            params['uf'] = uf

        logger.info(f'Buscando propostas abertas - Página {pagina} | dataFinal={data_final}')
        return self._fazer_requisicao('/v1/contratacoes/proposta', params)

    def buscar_por_publicacao(
        self,
        data_inicial: str,
        data_final: str,
        modalidade: int,
        uf: Optional[str] = None,
        pagina: int = 1,
    ) -> dict:
        """
        Consulta o endpoint de contratações por data de publicação.
        
        Endpoint: GET /v1/contratacoes/publicacao
        
        Args:
            data_inicial: Data inicial no formato yyyyMMdd.
            data_final: Data final no formato yyyyMMdd.
            modalidade: Código da modalidade de contratação (1-13, obrigatório).
            uf: Sigla da Unidade Federativa (opcional).
            pagina: Número da página (mínimo 1).
            
        Returns:
            Dicionário com a resposta JSON da API.
        """
        params = {
            'dataInicial': data_inicial,
            'dataFinal': data_final,
            'codigoModalidadeContratacao': modalidade,
            'pagina': max(1, pagina),
            'tamanhoPagina': self.tamanho_pagina,
        }

        if uf is not None:
            params['uf'] = uf

        logger.info(
            f'Buscando por publicação - Página {pagina} | '
            f'dataInicial={data_inicial} | dataFinal={data_final} | modalidade={modalidade}'
        )
        return self._fazer_requisicao('/v1/contratacoes/publicacao', params)

    def buscar_todas_propostas_abertas(
        self,
        data_final: Optional[str] = None,
        modalidade: Optional[int] = None,
        uf: Optional[str] = None,
        max_paginas: Optional[int] = None,
        callback: Optional[Callable[[int, int], None]] = None,
    ):
        """
        Busca TODAS as páginas de propostas abertas, retornando um gerador que faz yield
        dos editais de cada página (lotes de 50).
        
        Respeita o rate limiting aplicando delay entre cada requisição.
        Chama o callback de progresso a cada página processada.
        
        Args:
            data_final: Data final no formato yyyyMMdd.
            modalidade: Código da modalidade de contratação.
            uf: Sigla da UF.
            max_paginas: Limite máximo de páginas a consultar.
            callback: Função callback(pagina_atual, total_paginas) para acompanhamento de progresso.
        """
        pagina_atual = 1
        total_paginas = 1

        logger.info('Iniciando busca completa de propostas abertas...')

        while pagina_atual <= total_paginas:
            # Verifica se atingiu o limite de páginas configurado
            if max_paginas is not None and pagina_atual > max_paginas:
                logger.info(f'Limite de {max_paginas} páginas atingido. Interrompendo busca.')
                break

            try:
                resultado = self.buscar_propostas_abertas(
                    data_final=data_final,
                    modalidade=modalidade,
                    uf=uf,
                    pagina=pagina_atual,
                )

                # Extrai os dados da resposta
                editais = resultado.get('data', resultado.get('resultado', []))
                
                # Atualiza o total de páginas com base na resposta da API
                total_paginas = resultado.get('totalPaginas', resultado.get('paginasRestantes', 0) + pagina_atual)
                
                # Ajusta se houver limite de páginas configurado
                total_paginas_visual = min(total_paginas, max_paginas) if max_paginas is not None else total_paginas

                logger.info(
                    f'Página {pagina_atual}/{total_paginas_visual} processada | '
                    f'{len(editais)} editais nesta página'
                )

                # Chama callback de progresso se fornecido
                if callback is not None:
                    callback(pagina_atual, total_paginas_visual)

                # Faz yield dos editais da página se for uma lista válida
                if isinstance(editais, list) and editais:
                    yield editais

                pagina_atual += 1

                # Respeita rate limiting entre requisições
                if pagina_atual <= total_paginas_visual:
                    time.sleep(self.delay)

            except requests.exceptions.HTTPError as e:
                logger.error(f'Erro HTTP ao buscar página {pagina_atual}: {e}')
                raise
            except requests.exceptions.ConnectionError as e:
                logger.error(f'Erro de conexão ao buscar página {pagina_atual}: {e}')
                raise
            except Exception as e:
                logger.error(f'Erro inesperado ao buscar página {pagina_atual}: {e}')
                raise

        logger.info('Busca de propostas abertas via gerador finalizada.')

    def buscar_itens_edital(self, cnpj: str, ano: str, sequencial: int) -> list:
        """
        Busca os itens de uma contratação específica no PNCP.
        
        Args:
            cnpj: CNPJ do órgão.
            ano: Ano da contratação.
            sequencial: Número sequencial da compra.
            
        Returns:
            Lista de itens da contratação.
        """
        url = f"https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}/itens"
        logger.info(f"Buscando itens do edital CNPJ={cnpj} Ano={ano} Seq={sequencial}...")
        response = self.session.get(url, params={"pagina": 1}, timeout=60)
        response.raise_for_status()
        return response.json()
