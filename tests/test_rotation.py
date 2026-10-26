from datetime import date

from buscador.rotation import chave, proxima

TRECHOS = [{"origem": "A", "destino": "B"}, {"origem": "C", "destino": "D"}]
OFFSETS = [7, 30]


def test_percorre_todas_combinacoes_e_volta():
    hoje = date(2026, 10, 24)
    cursor, vistos = 0, []
    for _ in range(5):
        trecho, offset, data_ida, cursor = proxima(TRECHOS, OFFSETS, cursor, hoje)
        vistos.append(chave(trecho, offset))
    assert vistos == ["A>B@7", "C>D@7", "A>B@30", "C>D@30", "A>B@7"]


def test_data_ida_e_cursor_fora_do_intervalo():
    _, offset, data_ida, novo = proxima(TRECHOS, OFFSETS, 99, date(2026, 10, 24))
    assert offset == 30 and data_ida == date(2026, 11, 23) and novo == 0
