from pathlib import Path

file = Path("app/api/routes.py")
text = file.read_text(encoding="utf-8")

linhas = text.splitlines()

novas_linhas = []
pulando_security = False

for linha in linhas:
    if linha.strip() == "from app.core.security":
        continue
    if linha.strip().startswith("from app.core.deps import get_current_user import "):
        continue
    novas_linhas.append(linha)

texto = "\n".join(novas_linhas)

alvo = "from app.db.session import get_db"
substituto = """from app.db.session import get_db
from app.core.security import criar_access_token, decodificar_access_token, gerar_hash_senha, verificar_senha
from app.core.deps import get_current_user"""

texto = texto.replace(alvo, substituto)

file.write_text(texto, encoding="utf-8")
print("OK: imports do routes.py corrigidos")
