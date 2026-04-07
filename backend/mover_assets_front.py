from pathlib import Path
import shutil

base = Path(".").resolve()

index_candidates = []
for p in base.rglob("index.html"):
    if ".venv" not in str(p):
        index_candidates.append(p)

if not index_candidates:
    print("ERRO: nenhum index.html encontrado")
    raise SystemExit(1)

target_dir = None
for p in index_candidates:
    if "web" in str(p).lower() or "frontend" in str(p).lower() or "static" in str(p).lower():
        target_dir = p.parent
        break

if target_dir is None:
    target_dir = index_candidates[0].parent

css_sources = [p for p in base.rglob("smart-comparacao.css") if ".venv" not in str(p)]
js_sources = [p for p in base.rglob("smart-comparacao.js") if ".venv" not in str(p)]

if not css_sources or not js_sources:
    print("ERRO: smart-comparacao.css/js nao encontrados")
    raise SystemExit(1)

css_src = css_sources[0]
js_src = js_sources[0]

css_dst = target_dir / "smart-comparacao.css"
js_dst = target_dir / "smart-comparacao.js"

if css_src.resolve() != css_dst.resolve():
    shutil.copy2(css_src, css_dst)

if js_src.resolve() != js_dst.resolve():
    shutil.copy2(js_src, js_dst)

print("OK: pasta alvo do frontend:", target_dir)
print("OK: CSS em", css_dst)
print("OK: JS em", js_dst)
