from pathlib import Path
import re

path = Path(r".\app\web\index.html")
text = path.read_text(encoding="utf-8")

# substituir função init inteira
text = re.sub(
    r'async function init\(\)\s*\{[\s\S]*?\}',
    '''async function init() {
  preencherSelectListas();
  preencherSelectProdutos();

  // MODO DEV: ignora auth
  try { await carregarListas(); } catch (e) { console.error(e); }
  try { await carregarItens(); } catch (e) {}
  try { await carregarProdutos(); } catch (e) {}

  setTopStatus("Modo desenvolvimento");
  setStatus("Sistema pronto", "ok");
}''',
    text,
    count=1
)

path.write_text(text, encoding="utf-8")
print("init() corrigido para modo dev.")
