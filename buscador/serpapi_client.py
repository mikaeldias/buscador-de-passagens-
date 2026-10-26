import requests

BASE_URL = "https://serpapi.com"
TIMEOUT = 60


class SerpApiError(Exception):
    pass


class LimiteAtingido(SerpApiError):
    pass


def searches_left(api_key: str) -> int:
    """Saldo de buscas da conta. Esta chamada não consome cota."""
    resp = requests.get(f"{BASE_URL}/account.json", params={"api_key": api_key}, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()
    for campo in ("total_searches_left", "plan_searches_left"):
        if campo in data:
            return int(data[campo])
    raise SerpApiError(f"Resposta de conta sem saldo: {list(data)}")


def buscar_voos(api_key: str, origem: str, destino: str, data_ida: str,
                moeda: str, idioma: str, pais: str) -> dict:
    params = {
        "engine": "google_flights",
        "departure_id": origem,
        "arrival_id": destino,
        "outbound_date": data_ida,
        "type": 2,  # só ida
        "currency": moeda,
        "hl": idioma,
        "gl": pais,
        "api_key": api_key,
    }
    resp = requests.get(f"{BASE_URL}/search.json", params=params, timeout=TIMEOUT)
    if resp.status_code == 429:
        raise LimiteAtingido("SerpApi retornou 429 (limite atingido)")
    data = resp.json()
    erro = data.get("error")
    if erro:
        if "run out of searches" in erro.lower():
            raise LimiteAtingido(erro)
        # "hasn't returned any results" é resposta válida: sem voos para a data
        if "any results" in erro.lower():
            return data
        raise SerpApiError(erro)
    resp.raise_for_status()
    return data
