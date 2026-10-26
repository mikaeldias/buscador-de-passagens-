import json
from datetime import date
from pathlib import Path

from buscador.parser import extrair_voos, nivel_preco
from buscador.telegram import formatar_duracao, formatar_mensagem, formatar_preco

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "google_flights_sample.json")
                     .read_text(encoding="utf-8"))


def test_ordena_por_preco_e_ignora_sem_preco():
    voos = extrair_voos(FIXTURE, top_n=10)
    assert [v.preco for v in voos] == [289, 312, 389]


def test_campos_principais():
    voo = extrair_voos(FIXTURE, top_n=3)[1]
    assert voo.escalas == 1
    assert voo.aeroportos_escala == ["BSB"]
    assert voo.duracao_min == 265
    assert (voo.origem, voo.destino) == ("GRU", "GIG")
    assert voo.cias == ["GOL"]


def test_top_n():
    assert len(extrair_voos(FIXTURE, top_n=2)) == 2


def test_resposta_vazia():
    assert extrair_voos({"error": "Google Flights hasn't returned any results"}, 3) == []
    assert nivel_preco({}) is None


def test_formatacao():
    assert formatar_preco(1289) == "R$ 1.289"
    assert formatar_duracao(65) == "1h 05min"
    assert formatar_duracao(45) == "45min"


def test_mensagem():
    voos = extrair_voos(FIXTURE, 3)
    msg = formatar_mensagem("São Paulo → Rio", date(2026, 11, 8), voos, "low", 329)
    assert "08/11/2026 (dom)" in msg
    assert "R$ 289" in msg and "Direto" in msg
    assert "1 escala (BSB)" in msg and "4h 25min" in msg
    assert "⬇️ caiu R$ 40" in msg
    assert "Nível de preço: baixo" in msg


def test_mensagem_sem_voos():
    msg = formatar_mensagem("A → B", date(2026, 11, 8), [], None, None)
    assert "Nenhum voo encontrado" in msg
