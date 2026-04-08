from pathlib import Path
import re

path = Path(r".\app\web\index.html")
text = path.read_text(encoding="utf-8")

# Substituir TODA função checkAuth por versão fake
text = re.sub(
    r'async function checkAuth\(\)\s*\{[\s\S]*?\}',
    '''async function checkAuth() {
  console.log("Auth desativado (modo dev)");
  setStatus("Modo desenvolvimento");
  carregarListas();
}''',
    text,
    count=1
)

path.write_text(text, encoding="utf-8")
print("checkAuth desativado com sucesso.")
