from dataclasses import dataclass, field


@dataclass
class Voo:
    preco: int
    escalas: int
    duracao_min: int
    origem: str
    destino: str
    partida: str
    chegada: str
    cias: list[str] = field(default_factory=list)
    aeroportos_escala: list[str] = field(default_factory=list)


def extrair_voos(resposta: dict, top_n: int) -> list[Voo]:
    opcoes = resposta.get("best_flights", []) + resposta.get("other_flights", [])
    voos = []
    for opcao in opcoes:
        trechos = opcao.get("flights") or []
        if not trechos or opcao.get("price") is None:
            continue
        cias = []
        for t in trechos:
            cia = t.get("airline")
            if cia and cia not in cias:
                cias.append(cia)
        primeiro, ultimo = trechos[0], trechos[-1]
        voos.append(Voo(
            preco=int(opcao["price"]),
            escalas=len(trechos) - 1,
            duracao_min=int(opcao.get("total_duration")
                            or sum(t.get("duration", 0) for t in trechos)),
            origem=primeiro["departure_airport"]["id"],
            destino=ultimo["arrival_airport"]["id"],
            partida=primeiro["departure_airport"].get("time", ""),
            chegada=ultimo["arrival_airport"].get("time", ""),
            cias=cias,
            aeroportos_escala=[l["id"] for l in opcao.get("layovers", []) if l.get("id")],
        ))
    voos.sort(key=lambda v: (v.preco, v.duracao_min))
    return voos[:top_n]


def nivel_preco(resposta: dict) -> str | None:
    return (resposta.get("price_insights") or {}).get("price_level")
