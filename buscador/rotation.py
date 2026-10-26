from datetime import date, timedelta


def combinacoes(trechos: list[dict], offsets: list[int]) -> list[tuple[dict, int]]:
    # Intercala trechos para que execuções consecutivas variem de trecho.
    return [(trecho, offset) for offset in offsets for trecho in trechos]


def proxima(trechos: list[dict], offsets: list[int], cursor: int,
            hoje: date) -> tuple[dict, int, date, int]:
    """Retorna (trecho, offset, data_ida, novo_cursor)."""
    combos = combinacoes(trechos, offsets)
    trecho, offset = combos[cursor % len(combos)]
    return trecho, offset, hoje + timedelta(days=offset), (cursor + 1) % len(combos)


def chave(trecho: dict, offset: int) -> str:
    return f"{trecho['origem']}>{trecho['destino']}@{offset}"
