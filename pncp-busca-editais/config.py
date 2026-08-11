"""
Configurações da aplicação PNCP Busca Editais.
Contém todas as constantes e parâmetros de configuração do sistema.
"""

import os

# URL base da API do PNCP
PNCP_BASE_URL = 'https://pncp.gov.br/api/consulta'

# Tamanho máximo de página permitido pela API (10 a 50)
TAMANHO_PAGINA = 50

# Delay entre requisições à API (em segundos) para respeitar rate limiting
DELAY_ENTRE_REQUESTS = 2.0

# Número máximo de tentativas em caso de erro
MAX_RETRIES = 3

# Caminho do banco de dados SQLite
DATABASE_PATH = 'editais.db'

# Horários de execução automática das buscas (formato HH:MM)
HORARIOS_EXECUCAO = ['07:00', '19:00']

# Configurações do Flask
SQLALCHEMY_DATABASE_URI = 'sqlite:///editais.db'
SECRET_KEY = os.environ.get('SECRET_KEY', 'pncp-busca-editais-secret-key-2024')

# Dicionário de modalidades de contratação conforme códigos do PNCP
MODALIDADES = {
    1: 'Leilão - Eletrônico',
    2: 'Diálogo Competitivo',
    3: 'Concurso',
    4: 'Concorrência - Eletrônica',
    5: 'Concorrência - Presencial',
    6: 'Pregão - Eletrônico',
    7: 'Pregão - Presencial',
    8: 'Dispensa',
    9: 'Inexigibilidade',
    10: 'Manifestação de Interesse',
    11: 'Pré-qualificação',
    12: 'Credenciamento',
    13: 'Leilão - Presencial',
}

# Lista de todas as Unidades Federativas do Brasil
UFS = [
    'AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO',
    'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR',
    'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO',
]
