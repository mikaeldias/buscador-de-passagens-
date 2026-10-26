from datetime import datetime, timedelta, timezone

from buscador.budget import buscas_nesta_execucao, proximo_reset

UTC = timezone.utc


def calc(saldo, agora, maximo=3):
    return buscas_nesta_execucao(saldo, agora, dia_reset=1, intervalo_horas=3,
                                 reserva=10, maximo=maximo)


def test_proximo_reset():
    assert proximo_reset(datetime(2026, 10, 24, tzinfo=UTC), 1) == datetime(2026, 11, 1, tzinfo=UTC)
    assert proximo_reset(datetime(2026, 12, 5, tzinfo=UTC), 1) == datetime(2027, 1, 1, tzinfo=UTC)
    assert proximo_reset(datetime(2027, 1, 31, tzinfo=UTC), 31) == datetime(2027, 2, 28, tzinfo=UTC)


def test_sem_saldo_ou_so_reserva():
    agora = datetime(2026, 10, 10, tzinfo=UTC)
    assert calc(0, agora) == 0
    assert calc(10, agora) == 0


def test_fim_do_ciclo_com_sobra_usa_mais():
    agora = datetime(2026, 10, 31, 15, tzinfo=UTC)  # 3 execuções restantes
    assert calc(100, agora) == 3  # limitado pelo máximo


def test_mes_inteiro_nunca_estoura_cota():
    agora = datetime(2026, 10, 1, 0, tzinfo=UTC)
    saldo = 250
    while agora < datetime(2026, 11, 1, tzinfo=UTC):
        n = calc(saldo, agora)
        saldo -= n
        assert saldo >= 10
        agora += timedelta(hours=3)
    assert saldo <= 15  # cota praticamente toda aproveitada


def test_saldo_baixo_espalha_buscas():
    agora = datetime(2026, 10, 1, 0, tzinfo=UTC)
    saldo, usadas = 40, 0  # 30 disponíveis para 248 execuções
    while agora < datetime(2026, 11, 1, tzinfo=UTC):
        n = calc(saldo, agora)
        saldo -= n
        usadas += n
        agora += timedelta(hours=3)
    assert saldo >= 10
    assert usadas >= 25
