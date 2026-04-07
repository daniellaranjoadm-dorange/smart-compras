from pathlib import Path
import json

data = json.loads(Path("atacadao_auth.json").read_text(encoding="utf-8"))
jwt = data.get("jwt", "").strip()

if not jwt:
    print("ERRO: jwt nao encontrado em atacadao_auth.json")
    raise SystemExit(1)

Path(".atacadao_jwt").write_text(jwt, encoding="utf-8")
print("OK: JWT salvo em .atacadao_jwt")
