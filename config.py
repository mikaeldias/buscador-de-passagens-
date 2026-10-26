"""Configuração editável do buscador. Altere aqui os trechos e o orçamento."""

# Códigos IATA separados por vírgula: uma única busca cobre todos os aeroportos da cidade.
TRECHOS = [
    {"origem": "GRU,CGH", "destino": "GIG,SDU", "nome": "São Paulo → Rio de Janeiro"},
    # {"origem": "GIG,SDU", "destino": "GRU,CGH", "nome": "Rio de Janeiro → São Paulo"},
    # {"origem": "GRU,CGH", "destino": "SSA", "nome": "São Paulo → Salvador"},
]

# Datas de ida pesquisadas = hoje + offset (dias). Só ida.
OFFSETS_DIAS = [7, 15, 30, 45, 60]

MOEDA = "BRL"
IDIOMA = "pt"
PAIS = "br"
FUSO = "America/Sao_Paulo"

# Orçamento SerpApi
COTA_MENSAL = 250
RESERVA = 10  # buscas nunca usadas pelo robô (margem para testes manuais)
DIA_RESET_COTA = 1  # dia do mês em que a cota renova
INTERVALO_HORAS = 3  # precisa bater com o cron de .github/workflows/buscar.yml
MAX_BUSCAS_POR_EXECUCAO = 3

TOP_N = 3  # quantos voos enviar por cotação

STATE_FILE = "state.json"
