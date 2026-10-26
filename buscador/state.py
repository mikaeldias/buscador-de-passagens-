import json
from pathlib import Path


def carregar(caminho: str) -> dict:
    p = Path(caminho)
    if not p.exists():
        return {"cursor": 0, "ultimo_preco": {}}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"cursor": 0, "ultimo_preco": {}}
    data.setdefault("cursor", 0)
    data.setdefault("ultimo_preco", {})
    return data


def salvar(caminho: str, state: dict) -> None:
    Path(caminho).write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
