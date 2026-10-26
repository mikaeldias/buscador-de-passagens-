import calendar
import math
from datetime import datetime, timezone


def proximo_reset(agora: datetime, dia_reset: int) -> datetime:
    def no_mes(ano: int, mes: int) -> datetime:
        dia = min(dia_reset, calendar.monthrange(ano, mes)[1])
        return datetime(ano, mes, dia, tzinfo=timezone.utc)

    candidato = no_mes(agora.year, agora.month)
    if candidato > agora:
        return candidato
    ano, mes = (agora.year + 1, 1) if agora.month == 12 else (agora.year, agora.month + 1)
    return no_mes(ano, mes)


def buscas_nesta_execucao(saldo: int, agora: datetime, dia_reset: int,
                          intervalo_horas: int, reserva: int, maximo: int) -> int:
    """Distribui o saldo uniformemente pelas execuções restantes até o reset da cota."""
    disponivel = saldo - reserva
    if disponivel <= 0:
        return 0

    horas_restantes = (proximo_reset(agora, dia_reset) - agora).total_seconds() / 3600
    execucoes_restantes = max(1, math.ceil(horas_restantes / intervalo_horas))

    por_execucao = disponivel // execucoes_restantes
    if por_execucao >= 1:
        return min(por_execucao, maximo)

    # Menos saldo que execuções: busca 1 a cada `passo` execuções.
    passo = math.ceil(execucoes_restantes / disponivel)
    indice_execucao = int(agora.timestamp() // 3600) // intervalo_horas
    return 1 if indice_execucao % passo == 0 else 0
