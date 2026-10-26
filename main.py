import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import config
from buscador import budget, rotation, state as state_mod, telegram
from buscador.parser import extrair_voos, nivel_preco
from buscador.serpapi_client import LimiteAtingido, SerpApiError, buscar_voos, searches_left

FIXTURE = Path(__file__).parent / "tests" / "fixtures" / "google_flights_sample.json"

log = logging.getLogger("buscador")


def carregar_env(caminho: str = ".env") -> None:
    p = Path(caminho)
    if not p.exists():
        return
    for linha in p.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha and not linha.startswith("#") and "=" in linha:
            k, v = linha.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def exigir_env(*nomes: str) -> list[str]:
    faltando = [n for n in nomes if not os.environ.get(n)]
    if faltando:
        log.error("Variáveis de ambiente ausentes: %s", ", ".join(faltando))
        sys.exit(1)
    return [os.environ[n] for n in nomes]


def dry_run() -> None:
    hoje = datetime.now(ZoneInfo(config.FUSO)).date()
    trecho, offset, data_ida, _ = rotation.proxima(config.TRECHOS, config.OFFSETS_DIAS, 0, hoje)
    resposta = json.loads(FIXTURE.read_text(encoding="utf-8"))
    voos = extrair_voos(resposta, config.TOP_N)
    print(telegram.formatar_mensagem(trecho["nome"], data_ida, voos,
                                     nivel_preco(resposta), voos[0].preco + 40 if voos else None))


def executar() -> None:
    serp_key, tg_token, tg_chat = exigir_env("SERPAPI_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")
    agora = datetime.now(timezone.utc)

    try:
        saldo = searches_left(serp_key)
    except Exception as e:  # sem saldo confiável, não arrisca gastar cota
        log.error("Falha ao consultar saldo SerpApi: %s", e)
        return

    n = budget.buscas_nesta_execucao(saldo, agora, config.DIA_RESET_COTA, config.INTERVALO_HORAS,
                                     config.RESERVA, config.MAX_BUSCAS_POR_EXECUCAO)
    log.info("Saldo SerpApi: %d | buscas nesta execução: %d", saldo, n)
    if n == 0:
        return

    st = state_mod.carregar(config.STATE_FILE)
    hoje = agora.astimezone(ZoneInfo(config.FUSO)).date()
    try:
        for _ in range(n):
            trecho, offset, data_ida, novo_cursor = rotation.proxima(
                config.TRECHOS, config.OFFSETS_DIAS, st["cursor"], hoje)
            st["cursor"] = novo_cursor
            log.info("Buscando %s em %s", trecho["nome"], data_ida)
            try:
                resposta = buscar_voos(serp_key, trecho["origem"], trecho["destino"],
                                       data_ida.isoformat(), config.MOEDA, config.IDIOMA, config.PAIS)
            except LimiteAtingido as e:
                log.warning("Limite SerpApi atingido, encerrando: %s", e)
                break
            except (SerpApiError, OSError) as e:
                log.error("Erro na busca: %s", e)
                continue

            voos = extrair_voos(resposta, config.TOP_N)
            k = rotation.chave(trecho, offset)
            msg = telegram.formatar_mensagem(trecho["nome"], data_ida, voos,
                                             nivel_preco(resposta), st["ultimo_preco"].get(k))
            try:
                telegram.enviar(tg_token, tg_chat, msg)
            except Exception as e:
                log.error("Falha ao enviar para o Telegram: %s", e)
            if voos:
                st["ultimo_preco"][k] = voos[0].preco
    finally:
        state_mod.salvar(config.STATE_FILE, st)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    ap = argparse.ArgumentParser(description="Buscador de passagens → Telegram")
    ap.add_argument("--dry-run", action="store_true",
                    help="usa a fixture local e imprime a mensagem, sem chamar APIs")
    args = ap.parse_args()
    if args.dry_run:
        dry_run()
        return
    carregar_env()
    executar()


if __name__ == "__main__":
    main()
