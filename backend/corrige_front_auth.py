from pathlib import Path

file = Path("app/web/index.html")
html = file.read_text(encoding="utf-8")

old = '''        if (!response.ok) {
          setMessage("registerMsg", data.detail || "Erro ao cadastrar", "erro");
          return;
        }'''

new = '''        if (!response.ok) {
          let msg = "Erro ao cadastrar";
          if (typeof data.detail === "string") {
            msg = data.detail;
          } else if (Array.isArray(data.detail)) {
            msg = data.detail.map(x => x.msg).join(" | ");
          }
          setMessage("registerMsg", msg, "erro");
          return;
        }'''

html = html.replace(old, new)

old2 = '''        if (!response.ok) {
          setMessage("loginMsg", data.detail || "Erro no login", "erro");
          return;
        }'''

new2 = '''        if (!response.ok) {
          let msg = "Erro no login";
          if (typeof data.detail === "string") {
            msg = data.detail;
          } else if (Array.isArray(data.detail)) {
            msg = data.detail.map(x => x.msg).join(" | ");
          }
          setMessage("loginMsg", msg, "erro");
          return;
        }'''

html = html.replace(old2, new2)

file.write_text(html, encoding="utf-8")
print("OK: index.html atualizado")
