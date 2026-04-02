from pathlib import Path

file = Path("app/api/routes.py")
text = file.read_text(encoding="utf-8")

text = text.replace(
    "from app.core.security
from app.core.deps import get_current_user import criar_access_token, decodificar_access_token, gerar_hash_senha, verificar_senha",
    "from app.core.security import criar_access_token, decodificar_access_token, gerar_hash_senha, verificar_senha
from app.core.deps import get_current_user"
)

text = text.replace(
    "from app.core.security
from app.core.deps import get_current_user",
    "from app.core.security import criar_access_token, decodificar_access_token, gerar_hash_senha, verificar_senha
from app.core.deps import get_current_user"
)

if "from app.core.deps import get_current_user" not in text:
    text = text.replace(
        "from app.core.security import criar_access_token, decodificar_access_token, gerar_hash_senha, verificar_senha",
        "from app.core.security import criar_access_token, decodificar_access_token, gerar_hash_senha, verificar_senha
from app.core.deps import get_current_user"
    )

file.write_text(text, encoding="utf-8")
print("OK: imports corrigidos")
