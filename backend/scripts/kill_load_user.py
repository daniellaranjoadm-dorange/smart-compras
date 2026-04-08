from pathlib import Path
import re

path = Path(r".\app\web\index.html")
text = path.read_text(encoding="utf-8")

# substituir função inteira por versão neutra
text = re.sub(
    r'async function loadCurrentUser\(\)\s*\{[\s\S]*?\}',
    '''async function loadCurrentUser() {
  console.log("loadCurrentUser desativado (modo dev)");
  return { id: 1, nome: "Dev", email: "dev@local" };
}''',
    text,
    count=1
)

path.write_text(text, encoding="utf-8")
print("loadCurrentUser neutralizado.")
