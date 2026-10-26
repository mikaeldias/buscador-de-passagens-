from datetime import date
from html import escape

import requests

from buscador.parser import Voo

DIAS_SEMANA = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
NIVEIS = {"low": "baixo", "typical": "típico", "high": "alto"}


def formatar_preco(valor: int) -> str:
    return f"R$ {valor:,}".replace(",", ".")


def formatar_duracao(minutos: int) -> str:
    h, m = divmod(minutos, 60)
    return f"{h}h {m:02d}min" if h else f"{m}min"


def _hora(datahora: str) -> str:
    return datahora.split(" ")[-1] if datahora else ""


def formatar_mensagem(nome: str, data_ida: date, voos: list[Voo],
                      nivel: str | None, preco_anterior: int | None) -> str:
    cabecalho = (f"✈️ <b>{escape(nome)}</b> — {data_ida:%d/%m/%Y} "
                 f"({DIAS_SEMANA[data_ida.weekday()]})")
    if not voos:
        return f"{cabecalho}\nNenhum voo encontrado."

    linhas = [cabecalho]
    for i, v in enumerate(voos, 1):
        if v.escalas == 0:
            escalas = "Direto"
        else:
            rotulo = "escala" if v.escalas == 1 else "escalas"
            via = f" ({', '.join(v.aeroportos_escala)})" if v.aeroportos_escala else ""
            escalas = f"{v.escalas} {rotulo}{via}"
        linhas.append(
            f"{i}) <b>{formatar_preco(v.preco)}</b> · {escalas} · {formatar_duracao(v.duracao_min)}\n"
            f"    {v.origem} {_hora(v.partida)} → {v.destino} {_hora(v.chegada)} · "
            f"{escape(', '.join(v.cias))}"
        )

    menor = voos[0].preco
    if preco_anterior is not None and menor != preco_anterior:
        diff = menor - preco_anterior
        seta = "⬇️ caiu" if diff < 0 else "⬆️ subiu"
        linhas.append(f"{seta} {formatar_preco(abs(diff))} vs. última consulta")
    if nivel:
        linhas.append(f"Nível de preço: {NIVEIS.get(nivel, nivel)}")
    return "\n".join(linhas)


def enviar(token: str, chat_id: str, texto: str) -> None:
    resp = requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": texto, "parse_mode": "HTML",
              "disable_web_page_preview": True},
        timeout=30,
    )
    if not resp.ok:
        raise RuntimeError(f"Telegram {resp.status_code}: {resp.text}")
